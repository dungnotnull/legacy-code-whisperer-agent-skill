#!/usr/bin/env python3
"""
Legacy Code Whisperer — Pre-Change Safety Gate
Validates safety before making any change to legacy code.

Usage:
    python hooks/pre_change_gate.py --file lib/pricing.js --analysis analysis.json
    python hooks/pre_change_gate.py --file lib/auth.js --change-type C
"""

import argparse
import json
import sys
from pathlib import Path


CHANGE_TYPES = {
    'A': ('Pure Addition', 'LOW', 'Adding new code without modifying existing'),
    'B': ('Behavioral Extension', 'LOW-MEDIUM', 'Extending existing functionality additively'),
    'C': ('Behavioral Modification', 'MEDIUM-HIGH', 'Changing how existing code works'),
    'D': ('Structural Refactoring', 'HIGH', 'Reorganizing code without changing behavior'),
    'E': ('Data Migration', 'VERY HIGH', 'Changing database schema or migrating data'),
}


def load_analysis(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def check_file_safety(target_file: str, analysis: dict) -> dict:
    results = {
        'is_landmine': False,
        'is_cursed': False,
        'blast_radius': 0,
        'blast_details': {},
        'issues_in_file': [],
        'danger_score': 0,
    }

    # Check issues in this file
    issues = analysis.get('issues', [])
    file_issues = [i for i in issues if target_file in i.get('file', '')]
    results['issues_in_file'] = file_issues

    for issue in file_issues:
        if issue['severity'] == 'CURSED':
            results['is_cursed'] = True
        if issue['severity'] == 'LANDMINE':
            results['is_landmine'] = True

    # Check blast radius
    blast_radii = analysis.get('blast_radii', [])
    for br in blast_radii:
        if target_file in br.get('file', ''):
            results['blast_radius'] = br['total_impact']
            results['blast_details'] = br
            break

    # Check hotspots
    hotspots = analysis.get('hotspots', [])
    for spot in hotspots:
        if target_file in spot.get('file', ''):
            results['danger_score'] = spot['danger_score']
            break

    return results


def format_gate_output(target_file: str, change_type: str, safety: dict,
                       use_color: bool = True) -> tuple:
    """Returns (output_lines, is_blocked)"""
    G = '\033[92m' if use_color else ''
    R = '\033[91m' if use_color else ''
    Y = '\033[93m' if use_color else ''
    B = '\033[1m' if use_color else ''
    X = '\033[0m' if use_color else ''

    ct_name, ct_risk, ct_desc = CHANGE_TYPES.get(change_type, ('Unknown', 'UNKNOWN', ''))
    blockers = []
    warnings = []
    lines = []

    lines.append(f"\n{'═' * 60}")
    lines.append(f"  {B}🔮 LEGACY CODE WHISPERER — PRE-CHANGE GATE{X}")
    lines.append(f"{'═' * 60}")
    lines.append(f"\n📄 Target file: {B}{target_file}{X}")
    lines.append(f"🔧 Change type: {ct_name} — Risk: {ct_risk}")
    lines.append(f"   {ct_desc}\n")

    # Cursed check
    if safety['is_cursed']:
        blockers.append(f"💀 CURSED section detected in {target_file}")
        lines.append(f"  {R}💀 CURSED: This file contains sections that should NEVER be changed{X}")
        lines.append(f"     See LANDMINE_REGISTRY.md for details before proceeding\n")

    # Landmine check
    if safety['is_landmine']:
        if change_type in ('C', 'D', 'E'):
            blockers.append(f"🔴 LANDMINE found in {target_file} — high risk change type")
        else:
            warnings.append(f"🔴 LANDMINE patterns found — proceed with extreme caution")
        lines.append(f"  {R}🔴 LANDMINE: Dangerous patterns detected in this file{X}")
        for issue in safety['issues_in_file']:
            if issue['severity'] in ('CURSED', 'LANDMINE'):
                lines.append(f"     [{issue['code']}] {issue['title']}")
                lines.append(f"     Line {issue.get('line', '?')}: {issue.get('description', '')[:80]}")
        lines.append("")

    # Blast radius check
    br = safety['blast_radius']
    if br > 15:
        blockers.append(f"💥 Extreme blast radius: {br} files affected")
        lines.append(f"  {R}💥 EXTREME BLAST RADIUS: Changing this affects {br} other files{X}\n")
    elif br > 8:
        warnings.append(f"💥 High blast radius: {br} files affected")
        lines.append(f"  {Y}⚠️  HIGH BLAST RADIUS: {br} files depend on this{X}\n")
    elif br > 3:
        warnings.append(f"Impact: {br} files may be affected")
        lines.append(f"  ℹ️  Blast radius: {br} files depend on this\n")
    elif br == 0:
        lines.append(f"  {G}✅ Low blast radius — isolated file{X}\n")

    if safety['blast_details'].get('direct'):
        lines.append(f"  Directly affected files:")
        for f in safety['blast_details']['direct'][:5]:
            lines.append(f"    → {f}")
        extra = len(safety['blast_details']['direct']) - 5
        if extra > 0:
            lines.append(f"    → ...and {extra} more")
        lines.append("")

    # Danger score
    ds = safety['danger_score']
    if ds > 20:
        warnings.append(f"⚠️ High danger score: {ds}")
        lines.append(f"  {Y}⚠️  High complexity/danger score ({ds}) — this file is problematic{X}\n")

    # Change type specific warnings
    if change_type == 'E':
        blockers.append("Type E change: Database migration — requires backup confirmation")
        lines.append(f"  {R}🗄️  DATABASE MIGRATION: Requires confirmed backup before proceeding{X}\n")
    if change_type == 'D' and br > 5:
        warnings.append("Structural refactoring with high blast radius — needs test coverage first")

    # Required safety steps
    steps = []
    if safety['is_cursed'] or safety['is_landmine']:
        steps.append("Read LANDMINE_REGISTRY.md entry for this file")
    if br > 5:
        steps.append("Review DEPENDENCY_MAP.md blast radius details")
    steps.append("Run test suite to establish baseline: npm test / pytest")
    steps.append("Create feature branch: git checkout -b your-name/change-description")
    if change_type in ('C', 'D'):
        steps.append("Add characterization tests BEFORE making changes")
    if change_type == 'E':
        steps.append("Confirm database backup is recent and restorable")
        steps.append("Write DOWN migration before writing UP migration")

    lines.append(f"{'─' * 60}")
    lines.append(f"{B}Required safety steps before proceeding:{X}")
    for i, step in enumerate(steps, 1):
        lines.append(f"  {i}. [ ] {step}")

    lines.append(f"\n{'─' * 60}")

    is_blocked = len(blockers) > 0

    if is_blocked:
        lines.append(f"{R}{B}🚫 GATE: BLOCKED{X}")
        lines.append(f"   Resolve these issues before proceeding:")
        for b in blockers:
            lines.append(f"   • {b}")
    elif warnings:
        lines.append(f"{Y}{B}⚠️  GATE: PROCEED WITH CAUTION{X}")
        lines.append(f"   Warnings to address:")
        for w in warnings:
            lines.append(f"   • {w}")
    else:
        lines.append(f"{G}{B}✅ GATE: SAFE TO PROCEED{X}")
        lines.append(f"   No critical blockers detected for this change")

    lines.append(f"{'═' * 60}\n")
    return lines, is_blocked


def main():
    parser = argparse.ArgumentParser(description='Legacy Code Whisperer — Pre-Change Gate')
    parser.add_argument('--file', required=True, help='File you intend to change')
    parser.add_argument('--analysis', default='analysis.json', help='Analysis JSON')
    parser.add_argument('--change-type', default='C',
                        choices=['A', 'B', 'C', 'D', 'E'],
                        help='A=Add B=Extend C=Modify D=Refactor E=Migration')
    parser.add_argument('--force', action='store_true', help='Proceed despite blockers (logs warning)')
    args = parser.parse_args()

    use_color = sys.stdout.isatty()
    analysis = load_analysis(args.analysis)
    safety = check_file_safety(args.file, analysis)
    output_lines, is_blocked = format_gate_output(args.file, args.change_type, safety, use_color)

    for line in output_lines:
        print(line)

    if is_blocked and not args.force:
        sys.exit(1)
    elif is_blocked and args.force:
        print("⚠️  --force flag used. Proceeding despite blockers. Developer takes responsibility.")
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
