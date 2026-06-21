#!/usr/bin/env python3
"""
Legacy Code Whisperer — Codebase Analyzer
Automatically scans a codebase for legacy patterns, landmines, and complexity metrics.

Usage:
    python scripts/analyze_codebase.py --path ./my-app --output analysis.json
    python scripts/analyze_codebase.py --path ./my-app --report
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import defaultdict


# ─── Issue Registry ──────────────────────────────────────────────────────────

@dataclass
class CodeIssue:
    severity: str        # CURSED / LANDMINE / RISKY / CAUTION / INFO
    category: str        # timing / security / data / performance / coupling
    code: str            # LM-001
    title: str
    description: str
    file: str
    line: Optional[int] = None
    snippet: Optional[str] = None
    fix: Optional[str] = None


@dataclass
class FileMetrics:
    path: str
    lines: int = 0
    functions: int = 0
    complexity: int = 0      # Rough cyclomatic complexity
    magic_numbers: int = 0
    empty_catches: int = 0
    todos: int = 0
    danger_comments: int = 0
    imports: list = field(default_factory=list)
    exports: list = field(default_factory=list)
    language: str = 'unknown'


# ─── Pattern Definitions ─────────────────────────────────────────────────────

LANDMINE_PATTERNS = [
    # Timing landmines
    {
        'code': 'LM-001', 'severity': 'RISKY', 'category': 'timing',
        'title': 'setTimeout used as synchronization',
        'pattern': re.compile(r'setTimeout\s*\([^,]+,\s*\d{2,4}\s*\)', re.MULTILINE),
        'description': 'setTimeout used to wait for async operation — unreliable under load',
        'fix': 'Replace with proper async/await or event-based completion signal'
    },
    # Security landmines
    {
        'code': 'LM-010', 'severity': 'LANDMINE', 'category': 'security',
        'title': 'SQL injection via string concatenation',
        'pattern': re.compile(
            r'(query|execute|run)\s*\(\s*[`"\'].*?(WHERE|SET|VALUES).*?\$\{|'
            r'(query|execute|run)\s*\(\s*["\'].*?(WHERE|SET|VALUES).*?\+\s*\w',
            re.IGNORECASE | re.MULTILINE
        ),
        'description': 'SQL query built via string interpolation — SQL injection vulnerability',
        'fix': 'Use parameterized queries: db.query("SELECT * WHERE id = ?", [id])'
    },
    {
        'code': 'LM-011', 'severity': 'LANDMINE', 'category': 'security',
        'title': 'eval() with dynamic content',
        'pattern': re.compile(r'\beval\s*\(', re.MULTILINE),
        'description': 'eval() usage — potential remote code execution if input is user-controlled',
        'fix': 'Remove eval() entirely. Use JSON.parse() for data, proper functions for logic'
    },
    {
        'code': 'LM-012', 'severity': 'LANDMINE', 'category': 'security',
        'title': 'Hardcoded secret or credential',
        'pattern': re.compile(
            r'(password|secret|api_key|apikey|token|jwt_secret)\s*[=:]\s*["\'][^"\']{8,}["\']',
            re.IGNORECASE
        ),
        'description': 'Hardcoded credential detected in source code',
        'fix': 'Move to environment variable immediately. Rotate the exposed credential.'
    },
    # Data integrity landmines
    {
        'code': 'LM-020', 'severity': 'RISKY', 'category': 'data',
        'title': 'Non-atomic multi-step database operation',
        'pattern': re.compile(
            r'await\s+\w+\.(save|create|update|destroy|delete)\(.*?\)\s*\n'
            r'.*?await\s+\w+\.(save|create|update|destroy|delete)\(',
            re.MULTILINE | re.DOTALL
        ),
        'description': 'Multiple database operations without transaction — data corruption risk if one fails',
        'fix': 'Wrap in database transaction to ensure atomicity'
    },
    {
        'code': 'LM-021', 'severity': 'RISKY', 'category': 'data',
        'title': 'Float used for monetary calculation',
        'pattern': re.compile(
            r'(price|amount|cost|total|fee|charge|payment)\s*[*+\-/]\s*(?:\d+\.?\d*|'
            r'\w+\s*[*]\s*(?:0\.\d+|1\.\d+))',
            re.IGNORECASE
        ),
        'description': 'Floating point arithmetic on monetary values causes rounding errors',
        'fix': 'Use integer cents (multiply by 100) or a decimal library like decimal.js'
    },
    # Performance landmines
    {
        'code': 'LM-030', 'severity': 'RISKY', 'category': 'performance',
        'title': 'Database query inside loop',
        'pattern': re.compile(
            r'for\s*\([^)]+\)[^{]*\{[^}]*await[^}]*(query|find|fetch|select|get)\(',
            re.MULTILINE | re.DOTALL
        ),
        'description': 'Database query inside loop — N+1 query problem, destroys performance at scale',
        'fix': 'Fetch all needed data before the loop, use JOIN, or use DataLoader pattern'
    },
    {
        'code': 'LM-031', 'severity': 'CAUTION', 'category': 'performance',
        'title': 'findAll/findMany without limit',
        'pattern': re.compile(
            r'\.(findAll|findMany|find\(\s*\))\s*\(\s*\{(?![^}]*limit)',
            re.MULTILINE
        ),
        'description': 'Fetching all records without LIMIT — works for small datasets, crashes large ones',
        'fix': 'Add limit/pagination: findAll({ limit: 100, offset: page * 100 })'
    },
    # Silent failure patterns
    {
        'code': 'LM-040', 'severity': 'LANDMINE', 'category': 'reliability',
        'title': 'Empty catch block — silent error swallowing',
        'pattern': re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}', re.MULTILINE),
        'description': 'Errors caught and silently discarded — hides failures in production',
        'fix': 'At minimum: console.error(e) or logger.error(e). Better: proper error handling'
    },
    {
        'code': 'LM-041', 'severity': 'RISKY', 'category': 'reliability',
        'title': 'Unhandled promise (no .catch)',
        'pattern': re.compile(
            r'(?<!await\s)(?<!return\s)\w+\([^)]*\)\s*\.then\s*\([^)]+\)\s*(?!\.catch)',
            re.MULTILINE
        ),
        'description': 'Promise chain without .catch() — unhandled rejections crash Node.js',
        'fix': 'Add .catch(err => logger.error(err)) or use async/await with try/catch'
    },
    # Global state
    {
        'code': 'LM-050', 'severity': 'CAUTION', 'category': 'coupling',
        'title': 'Global variable mutation',
        'pattern': re.compile(r'\bglobal\.\w+\s*=|process\.env\.\w+\s*=', re.MULTILINE),
        'description': 'Mutating global state — hidden coupling between modules',
        'fix': 'Pass state explicitly as function parameters or use dependency injection'
    },
]

MAGIC_NUMBER_PATTERN = re.compile(
    r'(?<!["\'\w.])(?<!\$\{)(\d{2,}(?:\.\d+)?)(?!\s*[ms]|px|em|rem|%|vh|vw|s\b)',
    re.MULTILINE
)

DANGER_COMMENT_PATTERNS = [
    re.compile(r'#\s*(HACK|FIXME|XXX|BUG|DANGER|WARNING|DO NOT|DONT|DON\'T|BROKEN|CURSED)', re.IGNORECASE),
    re.compile(r'//\s*(HACK|FIXME|XXX|BUG|DANGER|WARNING|DO NOT|DONT|DON\'T|BROKEN|CURSED)', re.IGNORECASE),
]

TODO_PATTERN = re.compile(r'(//|#)\s*TODO[:\s]', re.IGNORECASE)

IMPORT_PATTERNS = {
    'js_require': re.compile(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"),
    'js_import': re.compile(r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]"),
    'py_import': re.compile(r"^(?:from\s+(\S+)\s+)?import\s+(\S+)", re.MULTILINE),
}

FUNCTION_PATTERNS = {
    'js': re.compile(r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>|\w+\s*=>))', re.MULTILINE),
    'py': re.compile(r'^(?:async\s+)?def\s+\w+', re.MULTILINE),
}

LANGUAGE_EXTENSIONS = {
    '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
    '.ts': 'typescript', '.tsx': 'typescript',
    '.py': 'python',
    '.php': 'php',
    '.rb': 'ruby',
    '.go': 'go',
    '.java': 'java',
    '.cs': 'csharp',
    '.sql': 'sql',
    '.sh': 'shell',
}

SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '.next', '__pycache__',
    '.venv', 'venv', 'vendor', 'coverage', '.pytest_cache', 'migrations',
}

SKIP_EXTS = {'.min.js', '.bundle.js', '.map', '.lock', '.svg', '.png', '.jpg'}


# ─── File Analysis ────────────────────────────────────────────────────────────

def detect_language(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    for ext, lang in LANGUAGE_EXTENSIONS.items():
        if filepath.name.endswith(ext):
            return lang
    return 'unknown'


def analyze_file(filepath: Path, root: Path) -> tuple:
    """Analyze a single file. Returns (FileMetrics, list[CodeIssue])."""
    rel_path = str(filepath.relative_to(root))
    language = detect_language(filepath)
    issues = []

    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return None, []

    lines = content.splitlines()
    metrics = FileMetrics(
        path=rel_path,
        lines=len(lines),
        language=language,
    )

    # Count functions
    for lang, pattern in FUNCTION_PATTERNS.items():
        if lang in language:
            metrics.functions = len(pattern.findall(content))
            break

    # Count TODOs
    metrics.todos = len(TODO_PATTERN.findall(content))

    # Count danger comments
    for pattern in DANGER_COMMENT_PATTERNS:
        metrics.danger_comments += len(pattern.findall(content))

    # Count magic numbers (rough)
    magic_matches = MAGIC_NUMBER_PATTERN.findall(content)
    metrics.magic_numbers = len([m for m in magic_matches
                                  if m not in ('0', '1', '2', '100', '1000', '404', '200', '500')])

    # Rough cyclomatic complexity
    complexity_keywords = ['if ', 'else ', 'elif ', 'for ', 'while ', 'catch ', 'case ', '&&', '||', '?']
    metrics.complexity = sum(content.count(kw) for kw in complexity_keywords)

    # Extract imports
    for pattern_name, pattern in IMPORT_PATTERNS.items():
        found = pattern.findall(content)
        if found:
            if isinstance(found[0], tuple):
                metrics.imports.extend([f for f in (g for grp in found for g in grp) if f])
            else:
                metrics.imports.extend(found)
            break

    # Scan for landmines
    for lm in LANDMINE_PATTERNS:
        for match in lm['pattern'].finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            snippet = content[max(0, match.start()-20):match.end()+20].replace('\n', ' ').strip()
            issues.append(CodeIssue(
                severity=lm['severity'],
                category=lm['category'],
                code=lm['code'],
                title=lm['title'],
                description=lm['description'],
                file=rel_path,
                line=line_num,
                snippet=snippet[:150],
                fix=lm['fix'],
            ))

    # Check for empty catches specifically
    empty_catch = re.findall(r'catch\s*\([^)]*\)\s*\{\s*\}', content)
    metrics.empty_catches = len(empty_catch)

    return metrics, issues


# ─── Dependency Analysis ──────────────────────────────────────────────────────

def build_dependency_graph(all_metrics: list) -> dict:
    """Build import dependency graph between files."""
    file_map = {m.path: m for m in all_metrics}
    graph = defaultdict(list)  # file -> list of files it imports

    for metrics in all_metrics:
        for imp in metrics.imports:
            # Resolve relative imports
            if imp.startswith('.'):
                base = str(Path(metrics.path).parent / imp)
                for ext in ['.js', '.ts', '.py', '.jsx', '.tsx']:
                    candidate = base + ext
                    if candidate in file_map:
                        graph[metrics.path].append(candidate)
                        break
                    candidate2 = base + '/index' + ext
                    if candidate2 in file_map:
                        graph[metrics.path].append(candidate2)
                        break

    return dict(graph)


def calculate_blast_radius(dep_graph: dict, target_file: str) -> dict:
    """Calculate what files depend on target_file."""
    direct = []
    for file, deps in dep_graph.items():
        if target_file in deps:
            direct.append(file)

    # Indirect: who depends on the direct dependents
    indirect = set()
    for direct_file in direct:
        for file, deps in dep_graph.items():
            if direct_file in deps and file not in direct:
                indirect.add(file)

    return {
        'direct': direct,
        'indirect': list(indirect),
        'total_impact': len(direct) + len(indirect),
    }


# ─── Scoring ──────────────────────────────────────────────────────────────────

def calculate_health_score(all_issues: list, all_metrics: list) -> dict:
    """Calculate overall codebase health score (0-100, higher = healthier)."""
    severity_deductions = {
        'CURSED': 25, 'LANDMINE': 15, 'RISKY': 8, 'CAUTION': 3, 'INFO': 0
    }
    total_deduction = sum(severity_deductions.get(i.severity, 0) for i in all_issues)
    base_score = max(0, 100 - total_deduction)

    total_lines = sum(m.lines for m in all_metrics)
    total_todos = sum(m.todos for m in all_metrics)
    total_danger = sum(m.danger_comments for m in all_metrics)
    avg_complexity = sum(m.complexity for m in all_metrics) / max(1, len(all_metrics))

    label = (
        '🟢 Manageable' if base_score >= 75 else
        '🟡 Concerning' if base_score >= 50 else
        '🟠 Serious Technical Debt' if base_score >= 25 else
        '🔴 Critical — Major Work Needed'
    )

    return {
        'score': base_score,
        'label': label,
        'total_issues': len(all_issues),
        'by_severity': {
            s: sum(1 for i in all_issues if i.severity == s)
            for s in ['CURSED', 'LANDMINE', 'RISKY', 'CAUTION', 'INFO']
        },
        'codebase_stats': {
            'total_files': len(all_metrics),
            'total_lines': total_lines,
            'total_todos': total_todos,
            'total_danger_comments': total_danger,
            'avg_complexity_per_file': round(avg_complexity, 1),
        }
    }


def identify_hotspots(all_metrics: list) -> list:
    """Identify the most problematic files."""
    scored = []
    for m in all_metrics:
        danger_score = (
            m.empty_catches * 8 +
            m.danger_comments * 3 +
            m.magic_numbers * 0.5 +
            max(0, m.lines - 300) * 0.01 +
            max(0, m.complexity - 50) * 0.1
        )
        if danger_score > 0:
            scored.append({
                'file': m.path,
                'danger_score': round(danger_score, 1),
                'lines': m.lines,
                'complexity': m.complexity,
                'empty_catches': m.empty_catches,
                'danger_comments': m.danger_comments,
                'magic_numbers': m.magic_numbers,
                'todos': m.todos,
            })

    return sorted(scored, key=lambda x: x['danger_score'], reverse=True)[:10]


# ─── Main Scanner ─────────────────────────────────────────────────────────────

def scan(root_path: str) -> dict:
    root = Path(root_path)
    all_metrics = []
    all_issues = []
    languages_found = defaultdict(int)

    print(f"🔍 Scanning {root_path}...")
    file_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            filepath = Path(dirpath) / filename
            # Skip non-source files
            if any(filename.endswith(ext) for ext in SKIP_EXTS):
                continue
            if filepath.suffix.lower() not in LANGUAGE_EXTENSIONS:
                continue

            metrics, issues = analyze_file(filepath, root)
            if metrics:
                all_metrics.append(metrics)
                all_issues.extend(issues)
                languages_found[metrics.language] += 1
                file_count += 1

    print(f"   Analyzed {file_count} source files")

    dep_graph = build_dependency_graph(all_metrics)
    health = calculate_health_score(all_issues, all_metrics)
    hotspots = identify_hotspots(all_metrics)

    # Top blast radius files
    blast_radii = []
    for m in all_metrics:
        br = calculate_blast_radius(dep_graph, m.path)
        if br['total_impact'] > 2:
            blast_radii.append({'file': m.path, **br})
    blast_radii.sort(key=lambda x: x['total_impact'], reverse=True)

    return {
        'root': root_path,
        'health': health,
        'hotspots': hotspots,
        'blast_radii': blast_radii[:10],
        'languages': dict(languages_found),
        'issues': [asdict(i) for i in all_issues],
        'dependency_graph': dep_graph,
        'file_count': file_count,
    }


def print_report(result: dict):
    use_color = sys.stdout.isatty()
    G = '\033[92m' if use_color else ''
    R = '\033[91m' if use_color else ''
    Y = '\033[93m' if use_color else ''
    B = '\033[1m' if use_color else ''
    X = '\033[0m' if use_color else ''

    h = result['health']
    SICONS = {'CURSED': f'{R}💀{X}', 'LANDMINE': f'{R}🔴{X}', 'RISKY': f'{Y}🟠{X}',
              'CAUTION': '🟡', 'INFO': '🟢'}

    print(f"\n{'═' * 60}")
    print(f"  {B}LEGACY CODE WHISPERER — CODEBASE ANALYSIS{X}")
    print(f"{'═' * 60}")
    print(f"\n📁 Path: {result['root']}")
    print(f"📄 Files: {result['file_count']}")
    if result.get('languages'):
        langs = ', '.join(f"{l}({n})" for l, n in sorted(result['languages'].items(), key=lambda x: -x[1]))
        print(f"🔧 Languages: {langs}")

    print(f"\n{'─' * 60}")
    score = h['score']
    score_bar = '█' * (score // 10) + '░' * (10 - score // 10)
    print(f"🏥 {B}CODEBASE HEALTH: {score}/100  [{score_bar}]{X}")
    print(f"   {h['label']}")
    print(f"\n   Issues: ", end='')
    for sev in ['CURSED', 'LANDMINE', 'RISKY', 'CAUTION']:
        count = h['by_severity'].get(sev, 0)
        if count:
            print(f"{SICONS[sev]}{count} {sev}  ", end='')
    print()

    stats = h.get('codebase_stats', {})
    print(f"\n   📊 Stats: {stats.get('total_lines',0):,} lines · "
          f"{stats.get('total_todos',0)} TODOs · "
          f"{stats.get('total_danger_comments',0)} danger comments")

    if result.get('hotspots'):
        print(f"\n{'─' * 60}")
        print(f"{B}🔥 HOTSPOT FILES (highest danger score){X}")
        for spot in result['hotspots'][:5]:
            print(f"\n  {Y}⚠️  {spot['file']}{X}  (danger score: {spot['danger_score']})")
            if spot['empty_catches']:
                print(f"     💀 {spot['empty_catches']} empty catch block(s)")
            if spot['danger_comments']:
                print(f"     ⚠️  {spot['danger_comments']} danger comment(s)")
            if spot['lines'] > 300:
                print(f"     📏 {spot['lines']} lines (consider splitting)")

    if result.get('blast_radii'):
        print(f"\n{'─' * 60}")
        print(f"{B}💥 HIGH BLAST RADIUS FILES{X}")
        print(f"   (Changing these affects the most other files)\n")
        for br in result['blast_radii'][:5]:
            danger = R if br['total_impact'] > 10 else Y
            print(f"  {danger}{br['file']}{X}")
            print(f"     → {br['total_impact']} files affected "
                  f"({len(br['direct'])} direct, {len(br['indirect'])} indirect)")

    critical = [i for i in result['issues'] if i['severity'] in ('CURSED', 'LANDMINE')]
    if critical:
        print(f"\n{'─' * 60}")
        print(f"{R}{B}🚨 CRITICAL ISSUES ({len(critical)} found){X}")
        for issue in critical[:8]:
            print(f"\n  {SICONS.get(issue['severity'], '•')} [{issue['code']}] {issue['title']}")
            print(f"     File: {issue['file']}:{issue.get('line', '?')}")
            if issue.get('snippet'):
                print(f"     Code: {issue['snippet'][:80]}...")
            if issue.get('fix'):
                print(f"     Fix:  {issue['fix'][:80]}")

    print(f"\n{'═' * 60}")
    print(f"Feed analysis.json to the AI agent for full intelligence report.")
    print(f"{'═' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description='Legacy Code Whisperer — Codebase Analyzer')
    parser.add_argument('--path', required=True, help='Path to codebase root')
    parser.add_argument('--output', default='analysis.json', help='Output JSON file')
    parser.add_argument('--report', action='store_true', help='Print human-readable report')
    args = parser.parse_args()

    result = scan(args.path)
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(f"💾 Analysis saved to {args.output}")

    if args.report:
        print_report(result)


if __name__ == '__main__':
    main()
