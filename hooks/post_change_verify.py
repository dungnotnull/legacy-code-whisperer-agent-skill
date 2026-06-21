#!/usr/bin/env python3
"""
Legacy Code Whisperer — Post-Change Verification
Verifies a change didn't introduce new landmines or break dependency contracts.

Usage:
    python hooks/post_change_verify.py --before before_analysis.json --after after_analysis.json --file lib/pricing.js
"""

import argparse
import json
import sys
from pathlib import Path


def load_analysis(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def compare_issues(before: dict, after: dict, target_file: str = None) -> dict:
    before_issues = before.get('issues', [])
    after_issues = after.get('issues', [])

    if target_file:
        before_issues = [i for i in before_issues if target_file in i.get('file', '')]
        after_issues = [i for i in after_issues if target_file in i.get('file', '')]

    def issue_key(i):
        return (i.get('code'), i.get('file'), i.get('title'))

    before_keys = {issue_key(i) for i in before_issues}
    after_keys = {issue_key(i) for i in after_issues}

    new_issues = [i for i in after_issues if issue_key(i) not in before_keys]
    resolved_issues = [i for i in before_issues if issue_key(i) not in after_keys]

    return {
        'new_issues': new_issues,
        'resolved_issues': resolved_issues,
        'before_count': len(before_issues),
        'after_count': len(after_issues),
    }


def compare_health(before: dict, after: dict) -> dict:
    before_score = before.get('health', {}).get('score', 0)
    after_score = after.get('health', {}).get('score', 0)
    return {
        'before_score': before_score,
        'after_score': after_score,
        'delta': after_score - before_score,
    }


def compare_blast_radius(before: dict, after: dict, target_file: str) -> dict:
    def find_br(analysis, file):
        for br in analysis.get('blast_radii', []):
            if file in br.get('file', ''):
                return br.get('total_impact', 0)
        return 0

    before_br = find_br(before, target_file)
    after_br = find_br(after, target_file)

    return {
        'before': before_br,
        'after': after_br,
        'delta': after_br - before_br,
    }


def main():
    parser = argparse.ArgumentParser(description='Legacy Code Whisperer — Post-Change Verification')
    parser.add_argument('--before', required=True, help='Analysis JSON before change')
    parser.add_argument('--after', required=True, help='Analysis JSON after change')
    parser.add_argument('--file', help='Specific file that was changed (optional, narrows scope)')
    args = parser.parse_args()

    use_color = sys.stdout.isatty()
    G = '\033[92m' if use_color else ''
    R = '\033[91m' if use_color else ''
    Y = '\033[93m' if use_color else ''
    B = '\033[1m' if use_color else ''
    X = '\033[0m' if use_color else ''

    before = load_analysis(args.before)
    after = load_analysis(args.after)

    print(f"\n{'═' * 60}")
    print(f"  {B}🔮 LEGACY CODE WHISPERER — POST-CHANGE VERIFICATION{X}")
    print(f"{'═' * 60}\n")

    # Health comparison
    health = compare_health(before, after)
    delta_color = G if health['delta'] >= 0 else R
    delta_sign = '+' if health['delta'] >= 0 else ''
    print(f"🏥 {B}Health Score:{X} {health['before_score']} → {health['after_score']} "
          f"({delta_color}{delta_sign}{health['delta']}{X})")

    # Issue comparison
    issues = compare_issues(before, after, args.file)
    print(f"\n📊 {B}Issues:{X} {issues['before_count']} → {issues['after_count']}")

    if issues['resolved_issues']:
        print(f"\n{G}✅ RESOLVED ({len(issues['resolved_issues'])}):{X}")
        for issue in issues['resolved_issues'][:10]:
            print(f"   • [{issue['code']}] {issue['title']} in {issue['file']}")

    if issues['new_issues']:
        print(f"\n{R}🆕 NEW ISSUES INTRODUCED ({len(issues['new_issues'])}):{X}")
        for issue in issues['new_issues'][:10]:
            severity_icon = {'CURSED': '💀', 'LANDMINE': '🔴', 'RISKY': '🟠', 'CAUTION': '🟡'}.get(
                issue['severity'], '•')
            print(f"   {severity_icon} [{issue['code']}] {issue['title']} in {issue['file']}:{issue.get('line','?')}")
            if issue.get('fix'):
                print(f"      Fix: {issue['fix'][:80]}")

    # Blast radius comparison (if specific file given)
    if args.file:
        br = compare_blast_radius(before, after, args.file)
        if br['delta'] != 0:
            delta_color = R if br['delta'] > 0 else G
            print(f"\n💥 {B}Blast Radius for {args.file}:{X} {br['before']} → {br['after']} "
                  f"({delta_color}{'+' if br['delta']>0 else ''}{br['delta']}{X})")

    # Verdict
    print(f"\n{'─' * 60}")
    new_critical = [i for i in issues['new_issues'] if i['severity'] in ('CURSED', 'LANDMINE')]

    if new_critical:
        print(f"{R}{B}🚫 VERDICT: NEW CRITICAL ISSUES DETECTED{X}")
        print(f"   This change introduced {len(new_critical)} critical issue(s).")
        print(f"   Review carefully before merging. Consider reverting.")
        exit_code = 1
    elif health['delta'] < -5:
        print(f"{Y}{B}⚠️  VERDICT: HEALTH SCORE DECLINED{X}")
        print(f"   Health dropped by {abs(health['delta'])} points. Review the new issues above.")
        exit_code = 1
    elif issues['new_issues']:
        print(f"{Y}{B}⚠️  VERDICT: MINOR NEW ISSUES{X}")
        print(f"   {len(issues['new_issues'])} new non-critical issue(s) — review when convenient")
        exit_code = 0
    else:
        print(f"{G}{B}✅ VERDICT: CLEAN CHANGE{X}")
        print(f"   No new issues detected. Safe to proceed.")
        exit_code = 0

    print(f"{'═' * 60}\n")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
