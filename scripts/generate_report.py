#!/usr/bin/env python3
"""
Legacy Code Whisperer — Intelligence Report Generator
Generates all 7 output documents from codebase analysis.

Usage:
    python scripts/generate_report.py --analysis analysis.json --output-dir ./legacy-report
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


SEVERITY_ICONS = {'CURSED': '💀', 'LANDMINE': '🔴', 'RISKY': '🟠', 'CAUTION': '🟡', 'INFO': '🟢'}


def load_analysis(path: str) -> dict:
    return json.loads(Path(path).read_text())


def score_bar(score: int, width: int = 10) -> str:
    filled = score * width // 100
    return '█' * filled + '░' * (width - filled)


# ─── Document 1: Codebase Intel ──────────────────────────────────────────────

def generate_codebase_intel(analysis: dict, meta: dict, output_dir: Path):
    h = analysis.get('health', {})
    score = h.get('score', 0)
    stats = h.get('codebase_stats', {})
    hotspots = analysis.get('hotspots', [])
    languages = analysis.get('languages', {})

    lines = [
        f"# Codebase Intelligence Report\n",
        f"**Path:** {analysis.get('root', 'Unknown')}  ",
        f"**Analyzed:** {datetime.now().strftime('%Y-%m-%d')}  ",
        f"**App Name:** {meta.get('app_name', 'Unknown')}  \n",
        "---\n",
        f"## Health Score\n",
        f"```\n{score}/100  [{score_bar(score)}]  {h.get('label', '')}\n```\n",
        "## Codebase Stats\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Files | {analysis.get('file_count', 0)} |",
        f"| Total Lines | {stats.get('total_lines', 0):,} |",
        f"| Languages | {', '.join(f'{l}({n})' for l, n in sorted(languages.items(), key=lambda x: -x[1]))} |",
        f"| TODOs | {stats.get('total_todos', 0)} |",
        f"| Danger Comments | {stats.get('total_danger_comments', 0)} |",
        f"| Avg Complexity/File | {stats.get('avg_complexity_per_file', 0)} |\n",
        "## Issue Summary\n",
        f"| Severity | Count | Impact |",
        f"|----------|-------|--------|",
    ]
    for sev in ['CURSED', 'LANDMINE', 'RISKY', 'CAUTION']:
        count = h.get('by_severity', {}).get(sev, 0)
        impact = {'CURSED': 'Production disaster guaranteed', 'LANDMINE': 'Major failure risk',
                  'RISKY': 'Significant failure risk', 'CAUTION': 'Minor risk'}.get(sev, '')
        if count:
            lines.append(f"| {SEVERITY_ICONS[sev]} {sev} | {count} | {impact} |")

    lines += ["\n## Top Hotspot Files\n"]
    for spot in hotspots[:5]:
        lines += [
            f"### `{spot['file']}`  (danger score: {spot['danger_score']})\n",
            f"- Lines: {spot['lines']}, Complexity: {spot['complexity']}",
            f"- Empty catches: {spot['empty_catches']}, Danger comments: {spot['danger_comments']}\n",
        ]

    blast = analysis.get('blast_radii', [])
    if blast:
        lines += ["## High Blast Radius Files\n",
                  "| File | Direct | Indirect | Total Impact |",
                  "|------|--------|----------|-------------|"]
        for br in blast[:8]:
            lines.append(f"| `{br['file']}` | {len(br['direct'])} | {len(br['indirect'])} | {br['total_impact']} |")
        lines.append("")

    lines += [
        "---\n",
        "## What This Codebase Does\n",
        "*[AI agent: Describe what this codebase does in plain English based on code analysis]*\n",
        "## Main Entry Points\n",
        "*[AI agent: Identify and explain main entry points]*\n",
        "## Key Architecture Pattern\n",
        "*[AI agent: Describe the overall architecture pattern found]*\n",
    ]

    (output_dir / 'CODEBASE_INTEL.md').write_text('\n'.join(lines))
    print("✅ CODEBASE_INTEL.md")


# ─── Document 2: Business Rules ──────────────────────────────────────────────

def generate_business_rules(analysis: dict, meta: dict, output_dir: Path):
    issues = analysis.get('issues', [])
    magic_number_issues = [i for i in issues if 'magic' in i.get('title', '').lower()
                           or 'monetary' in i.get('category', '')]

    lines = [
        f"# Business Rules Extracted from Code\n",
        f"**Codebase:** {meta.get('app_name', 'Unknown')}  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n",
        "> All rules extracted from code analysis. Confidence levels noted.\n",
        "---\n",
        "## Core Business Rules\n",
        "*[AI agent: Extract and document business rules from code analysis — Phase 2]*\n",
        "### BR-001: [First business rule name]\n",
        "**Source:** [file:line]  \n**Rule:** [Plain English description]  \n**Confidence:** [HIGH/MEDIUM/LOW]\n",
        "---\n",
        "## Magic Values Registry\n",
        "| Value | Location | Business Meaning | Confidence |",
        "|-------|----------|-----------------|-----------|",
        "*[AI agent: Fill from code analysis — see Phase 2: Business Logic Extractor]*\n",
        "---\n",
        "## State Machines Found\n",
        "*[AI agent: Document all implicit state machines discovered in the code]*\n",
        "---\n",
        "## Hidden Side Effects\n",
        "| Function | Location | Hidden Effect |",
        "|----------|----------|--------------|",
        "*[AI agent: Document all functions that do more than their name suggests]*\n",
        "---\n",
        "## Authorization Model\n",
        "*[AI agent: Extract and document permission/role system from code]*\n",
        "---\n",
        "## Unimplemented Business Rules (Gaps)\n",
        "*[AI agent: Document logical cases the code doesn't handle]*\n",
    ]

    (output_dir / 'BUSINESS_RULES.md').write_text('\n'.join(lines))
    print("✅ BUSINESS_RULES.md")


# ─── Document 3: Dependency Map ──────────────────────────────────────────────

def generate_dependency_map(analysis: dict, meta: dict, output_dir: Path):
    blast_radii = analysis.get('blast_radii', [])
    dep_graph = analysis.get('dependency_graph', {})

    lines = [
        f"# Dependency Map\n",
        f"**Codebase:** {meta.get('app_name', 'Unknown')}  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n",
        "---\n",
        "## Blast Radius Registry\n",
        "### Critical Files (Highest Impact)\n",
        "| File | Direct Dependents | Indirect Dependents | Total Impact | Danger Level |",
        "|------|-----------------|-------------------|-------------|-------------|",
    ]

    for br in blast_radii:
        total = br['total_impact']
        danger = '🔴 CRITICAL' if total > 10 else '🟠 HIGH' if total > 5 else '🟡 MEDIUM'
        lines.append(f"| `{br['file']}` | {len(br['direct'])} | {len(br['indirect'])} | {total} | {danger} |")

    lines += [
        "\n### Detailed Blast Radii\n",
    ]
    for br in blast_radii[:8]:
        lines += [
            f"#### `{br['file']}`\n",
            f"**Direct dependents ({len(br['direct'])}):**",
        ]
        for d in br['direct'][:5]:
            lines.append(f"- `{d}`")
        if len(br['direct']) > 5:
            lines.append(f"- *...and {len(br['direct'])-5} more*")
        if br['indirect']:
            lines.append(f"\n**Indirect dependents ({len(br['indirect'])}):**")
            for d in br['indirect'][:3]:
                lines.append(f"- `{d}`")
            if len(br['indirect']) > 3:
                lines.append(f"- *...and {len(br['indirect'])-3} more*")
        lines.append("")

    lines += [
        "---\n",
        "## Safe Zones (Low Blast Radius)\n",
        "*[AI agent: Identify files that are safe to change freely — Phase 3]*\n",
        "---\n",
        "## Circular Dependencies\n",
        "*[AI agent: Identify and document circular dependency chains — Phase 3]*\n",
        "---\n",
        "## Hidden Couplings\n",
        "*[AI agent: Document non-import dependencies (globals, shared DB state, events) — Phase 3]*\n",
    ]

    (output_dir / 'DEPENDENCY_MAP.md').write_text('\n'.join(lines))
    print("✅ DEPENDENCY_MAP.md")


# ─── Document 4: Landmine Registry ───────────────────────────────────────────

def generate_landmine_registry(analysis: dict, meta: dict, output_dir: Path):
    issues = analysis.get('issues', [])
    cursed = [i for i in issues if i['severity'] == 'CURSED']
    landmines = [i for i in issues if i['severity'] == 'LANDMINE']
    risky = [i for i in issues if i['severity'] == 'RISKY']

    lines = [
        f"# Landmine Registry\n",
        f"## ⚠️ READ THIS BEFORE CHANGING ANYTHING\n",
        f"**Codebase:** {meta.get('app_name', 'Unknown')}  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n",
        f"> **{len(cursed) + len(landmines)} critical danger zones found.**\n",
        "---\n",
    ]

    if cursed:
        lines += [f"## 💀 CURSED Sections — Do Not Touch ({len(cursed)})\n",
                  "*These sections work by accident or have unknown behavior. Leave them alone.*\n"]
        for i, issue in enumerate(cursed, 1):
            lines += [
                f"### CURSED-{i:03d}: {issue['title']}",
                f"**File:** `{issue['file']}`:{issue.get('line', '?')}  ",
                f"**Problem:** {issue['description']}  ",
            ]
            if issue.get('snippet'):
                lines += [f"```\n{issue['snippet']}\n```"]
            if issue.get('fix'):
                lines.append(f"**If you must change it:** {issue['fix']}\n")

    if landmines:
        lines += [f"## 🔴 LANDMINES — Touch Only With Extreme Care ({len(landmines)})\n"]
        for i, issue in enumerate(landmines, 1):
            lines += [
                f"### LM-{i:03d}: {issue['title']}",
                f"**File:** `{issue['file']}`:{issue.get('line', '?')}  ",
                f"**Category:** {issue['category']}  ",
                f"**Problem:** {issue['description']}  ",
            ]
            if issue.get('snippet'):
                lines += [f"```\n{issue['snippet']}\n```"]
            if issue.get('fix'):
                lines.append(f"**Safe approach:** {issue['fix']}\n")

    if risky:
        lines += [f"## 🟠 RISKY Sections — Treat With Caution ({len(risky)})\n"]
        for i, issue in enumerate(risky, 1):
            lines += [
                f"### RISKY-{i:03d}: {issue['title']}",
                f"**File:** `{issue['file']}`:{issue.get('line', '?')} — {issue['description']}\n",
            ]

    if not cursed and not landmines and not risky:
        lines.append("✅ **No critical landmines detected by automated scan.**\n")
        lines.append("*Run AI agent Phase 4 analysis for deeper behavioral pattern detection.*\n")

    lines += [
        "---\n",
        "## Safe Zones (Free to Change)\n",
        "*[AI agent: List files that are safe to modify based on Phase 3+4 analysis]*\n",
        "---\n",
        "## Additional Landmines Found by AI Analysis\n",
        "*[AI agent: Document landmines requiring code reading to detect — Phase 4]*\n",
    ]

    (output_dir / 'LANDMINE_REGISTRY.md').write_text('\n'.join(lines))
    print("✅ LANDMINE_REGISTRY.md")


# ─── Document 5: Onboarding Guide ────────────────────────────────────────────

def generate_onboarding_guide(analysis: dict, meta: dict, output_dir: Path):
    languages = analysis.get('languages', {})
    primary_lang = max(languages, key=languages.get) if languages else 'unknown'

    lines = [
        f"# Developer Onboarding Guide\n",
        f"## Welcome to {meta.get('app_name', 'This Codebase')}\n",
        f"*Generated by Legacy Code Whisperer — {datetime.now().strftime('%Y-%m-%d')}*\n",
        f"> Estimated reading time: 45 minutes. After reading, you should be productive.\n",
        "---\n",
        "## What This App Does\n",
        "*[AI agent: Plain English description — Phase 5]*\n",
        "## Getting It Running\n",
        f"**Primary language:** {primary_lang}  \n",
        "*[AI agent: Extract setup steps from code analysis — Phase 5]*\n",
        "### Required Environment Variables\n",
        "*[AI agent: Extract all process.env references — Phase 5]*\n",
        "### Known Setup Issues\n",
        "*[AI agent: Document common errors found in error handling — Phase 5]*\n",
        "---\n",
        "## How It's Organized\n",
        "*[AI agent: Directory structure with plain English explanation — Phase 5]*\n",
        "---\n",
        "## The Main Flows\n",
        "*[AI agent: Step-by-step explanation of core user flows — Phase 5]*\n",
        "---\n",
        "## The Database\n",
        "*[AI agent: Tables, relationships, and key fields — Phase 5]*\n",
        "---\n",
        "## Things That Will Catch You Out\n",
        "*[AI agent: Critical gotchas every developer must know — from Phases 1-4 findings]*\n",
    ]

    # Auto-populate from automated findings
    issues = analysis.get('issues', [])
    critical = [i for i in issues if i['severity'] in ('CURSED', 'LANDMINE')]
    if critical:
        lines += [
            "\n### ⚠️ Auto-Detected Critical Warnings\n",
            "The automated scanner found these issues — review before touching anything:\n",
        ]
        for issue in critical[:5]:
            lines.append(f"- **{issue['title']}** in `{issue['file']}` — {issue['description']}")

    lines += [
        "\n---\n",
        "## Making Your First Change\n",
        "*[AI agent: Safe first-change procedure for this specific codebase — Phase 5]*\n",
        "### Before You Change Anything\n",
        "1. Read `LANDMINE_REGISTRY.md` — know what's dangerous\n"
        "2. Check `DEPENDENCY_MAP.md` for the file you're changing\n"
        "3. Run the test suite to establish baseline\n"
        "4. Create a feature branch — never work on main\n",
    ]

    (output_dir / 'ONBOARDING_GUIDE.md').write_text('\n'.join(lines))
    print("✅ ONBOARDING_GUIDE.md")


# ─── Document 6: Change Plan ─────────────────────────────────────────────────

def generate_change_plan(analysis: dict, meta: dict, output_dir: Path):
    lines = [
        f"# Safe Change Plan\n",
        f"**Codebase:** {meta.get('app_name', 'Unknown')}  ",
        f"**Requested Change:** {meta.get('change_request', 'Not specified')}  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n",
        "---\n",
        "## Change Classification\n",
        "**Type:** *[AI agent: A/B/C/D/E — Pure Addition / Extension / Modification / Refactor / Migration]*  \n",
        "**Risk Level:** *[AI agent: 🟢/🟡/🟠/🔴]*  \n",
        "**Estimated Effort:** *[AI agent: hours]*\n",
        "---\n",
        "## Target Files\n",
        "*[AI agent: List files that need to change and what changes in each]*\n",
        "---\n",
        "## Blast Radius\n",
        "*[AI agent: From DEPENDENCY_MAP.md — what could break]*\n",
        "---\n",
        "## Pre-Change Safety Steps\n",
        "- [ ] Read all target files completely\n"
        "- [ ] Run existing tests — establish baseline\n"
        "- [ ] Check LANDMINE_REGISTRY.md for target files\n"
        "- [ ] Create feature branch\n",
        "---\n",
        "## Step-by-Step Change Procedure\n",
        "*[AI agent: Exact ordered steps with code snippets — Phase 6]*\n",
        "---\n",
        "## Tests to Run\n",
        "*[AI agent: Specific test commands and manual verification steps]*\n",
        "---\n",
        "## Rollback Procedure\n",
        "*[AI agent: Exact rollback steps including commands and time estimate]*\n",
        "---\n",
        "## Known Risks\n",
        "*[AI agent: Specific risks for this change with mitigation strategies]*\n",
    ]

    (output_dir / 'CHANGE_PLAN.md').write_text('\n'.join(lines))
    print("✅ CHANGE_PLAN.md")


# ─── Document 7: Refactor Roadmap ────────────────────────────────────────────

def generate_refactor_roadmap(analysis: dict, meta: dict, output_dir: Path):
    hotspots = analysis.get('hotspots', [])
    h = analysis.get('health', {})

    lines = [
        f"# Refactor Roadmap\n",
        f"**Codebase:** {meta.get('app_name', 'Unknown')}  ",
        f"**Health Score:** {h.get('score', 0)}/100  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n",
        "> Approach: Incremental strangler fig — no big-bang rewrites.\n",
        "> Every step is independently deployable and reversible.\n",
        "---\n",
        "## Priority Registry (Auto-scored)\n",
        "| File | Lines | Complexity | Empty Catches | Danger Comments | Priority |",
        "|------|-------|-----------|--------------|----------------|---------|",
    ]

    for spot in hotspots[:10]:
        priority = '🔴 HIGH' if spot['danger_score'] > 15 else '🟡 MEDIUM' if spot['danger_score'] > 5 else '🟢 LOW'
        lines.append(
            f"| `{spot['file']}` | {spot['lines']} | {spot['complexity']} | "
            f"{spot['empty_catches']} | {spot['danger_comments']} | {priority} |"
        )

    lines += [
        "\n---\n",
        "## 3-Month Modernization Plan\n",
        "### Month 1: Safety Net\n",
        "**Goal:** Add test coverage before changing anything\n",
        "- [ ] Week 1-2: Characterization tests for top 3 hotspot files\n"
        "- [ ] Week 3-4: CI/CD setup — automated tests on every PR\n",
        "**Success criteria:** Can change any critical file and know in 2 minutes if broken\n",
        "### Month 2: Foundation Modernization\n",
        "*[AI agent: Specific plan based on Phase 7 analysis]*\n",
        "### Month 3: Business Logic Modernization\n",
        "*[AI agent: Specific module extraction plans for top priority files]*\n",
        "---\n",
        "## Module Extraction Plans\n",
    ]

    for spot in hotspots[:3]:
        lines += [
            f"### `{spot['file']}` (Priority Refactor)\n",
            f"**Current state:** {spot['lines']} lines, complexity {spot['complexity']}\n",
            "*[AI agent: Specific extraction plan for this file — Phase 7]*\n",
        ]

    lines += [
        "---\n",
        "## Definition of Done\n",
        "- [ ] All critical paths have 70%+ test coverage\n"
        "- [ ] No file over 200 lines (or documented exception)\n"
        "- [ ] No circular dependencies\n"
        "- [ ] All magic numbers documented in constants file\n"
        "- [ ] New developer productive in 1 day (ONBOARDING_GUIDE.md verified)\n",
    ]

    (output_dir / 'REFACTOR_ROADMAP.md').write_text('\n'.join(lines))
    print("✅ REFACTOR_ROADMAP.md")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Legacy Code Whisperer — Report Generator')
    parser.add_argument('--analysis', required=True, help='Analysis JSON from analyze_codebase.py')
    parser.add_argument('--output-dir', default='./legacy-report')
    parser.add_argument('--app-name', default='Unknown App', help='Application name')
    parser.add_argument('--change-request', default='', help='Specific change being planned')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis = load_analysis(args.analysis)
    meta = {'app_name': args.app_name, 'change_request': args.change_request}

    print(f"\n🔮 Legacy Code Whisperer — Report Generator")
    print(f"{'─' * 50}")
    print(f"App: {args.app_name}")
    print(f"Health: {analysis.get('health', {}).get('score', '?')}/100")
    print(f"Output: {output_dir}\n")

    generate_codebase_intel(analysis, meta, output_dir)
    generate_business_rules(analysis, meta, output_dir)
    generate_dependency_map(analysis, meta, output_dir)
    generate_landmine_registry(analysis, meta, output_dir)
    generate_onboarding_guide(analysis, meta, output_dir)
    generate_change_plan(analysis, meta, output_dir)
    generate_refactor_roadmap(analysis, meta, output_dir)

    print(f"\n✅ All 7 documents generated in: {output_dir}/")
    print(f"   Start with LANDMINE_REGISTRY.md before touching anything")


if __name__ == '__main__':
    main()
