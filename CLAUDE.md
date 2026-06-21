# CLAUDE.md — Legacy Code Whisperer

## Project Identity

**Name:** `legacy-code-whisperer`
**Type:** Claude Agent Skill — 7-Phase Forensic Code Analysis Workflow
**Version:** 1.0.0
**Category:** Developer Tooling / Legacy Code Intelligence
**Target User:** Any developer working with undocumented, inherited, or chaotic codebases

---

## What This Skill Does

Legacy Code Whisperer is a forensic software archaeologist that reads any codebase —
regardless of age, language, or chaos level — and produces:

- **Plain English explanations** of what cryptic code actually does
- **Business rules extracted** from magic numbers and conditionals
- **Complete dependency maps** showing exact blast radius of any change
- **Landmine registries** flagging dangerous code before you touch it
- **1-day onboarding guides** instead of 3-week ramp-ups
- **Safe change plans** with rollback procedures for any specific modification
- **Incremental refactor roadmaps** that never require stopping production

### The One-Sentence Pitch
> "Give me any codebase — undocumented, ancient, or terrifying — and I'll tell you
> exactly what it does, what's dangerous to touch, and how to safely change it."

---

## Architecture

```
legacy-code-whisperer/
│
├── SKILL.md                              ← Entry point: 7-phase harness
│
├── sub-skills/
│   ├── code-archaeologist.md             ← Phase 1: Intent reconstruction
│   ├── business-logic-extractor.md       ← Phase 2: Code → plain English rules
│   ├── dependency-mapper.md              ← Phase 3: Blast radius mapping
│   ├── landmine-detector.md              ← Phase 4: Danger zone identification
│   ├── onboarding-guide-generator.md     ← Phase 5: New dev documentation
│   ├── safe-change-advisor.md            ← Phase 6: Change-specific safety plan
│   └── refactor-roadmap-builder.md       ← Phase 7: Incremental modernization
│
├── scripts/
│   ├── analyze_codebase.py               ← Automated pattern + landmine scan
│   └── generate_report.py                ← 7 output document generator
│
├── hooks/
│   ├── pre_change_gate.py                ← Safety gate before any change
│   └── post_change_verify.py             ← Before/after comparison verification
│
├── references/
│   ├── legacy-pattern-decoder.md         ← Naming/pattern → meaning dictionary
│   └── worked-example.md                 ← Full e-commerce module walkthrough
│
├── checklists/
│   └── legacy-safety-checklists.md       ← 8 scenario-specific checklists
│
├── templates/
│   └── characterization-test-patterns.md ← Test-before-refactor templates
│
├── assets/
│   └── sample-landmine-registry.md       ← Sample output
│
├── CLAUDE.md                             ← This file
├── PROJECT-detail.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
└── README.md
```

---

## 7-Phase Workflow

| Phase | Name | Output |
|-------|------|--------|
| 1 | Code Archaeologist | Intent, era, author patterns, debt classification |
| 2 | Business Logic Extractor | Plain English business rules from code |
| 3 | Dependency Mapper | Complete blast radius for every module |
| 4 | Landmine Detector | Danger registry with severity levels |
| 5 | Onboarding Guide Generator | 1-day ramp-up documentation |
| 6 | Safe Change Advisor | Exact safe procedure for specific changes |
| 7 | Refactor Roadmap Builder | 3-month incremental modernization plan |

---

## Danger Classification

| Level | Meaning | Action |
|-------|---------|--------|
| 🟢 SAFE | Well-isolated, clear behavior | Change freely |
| 🟡 CAUTION | Some coupling but manageable | Change with care |
| 🟠 RISKY | Many dependents or unclear behavior | Wrap, don't modify directly |
| 🔴 LANDMINE | Do not touch without full analysis | Wrap, never change directly |
| 💀 CURSED | Unknown behavior, works by accident | Leave alone or full rewrite only |

---

## Quick Start

### Pure AI Mode
Paste code or describe the codebase:
> "I inherited this codebase and don't understand it. [paste code]"

### Script-Assisted Mode (recommended for full codebases)
```bash
# Scan the codebase
python3 scripts/analyze_codebase.py --path ./legacy-app --output analysis.json --report

# Generate all 7 intelligence documents
python3 scripts/generate_report.py --analysis analysis.json --app-name "My App"

# Before making any change
python3 hooks/pre_change_gate.py --file lib/pricing.js --analysis analysis.json --change-type C

# After making a change, verify nothing new broke
python3 scripts/analyze_codebase.py --path ./legacy-app --output after.json
python3 hooks/post_change_verify.py --before analysis.json --after after.json --file lib/pricing.js
```

### Quick Decode Mode
> "What does this function do? [paste single function]"

### Emergency Mode
> "Production is broken and I don't understand this code" → immediate triage

---

## Output Documents

| File | Contents |
|------|---------|
| `CODEBASE_INTEL.md` | What this codebase does, health score, hotspots |
| `BUSINESS_RULES.md` | Every business rule extracted from code |
| `DEPENDENCY_MAP.md` | Blast radius for every module |
| `LANDMINE_REGISTRY.md` | Dangerous code with DO NOT TOUCH warnings |
| `ONBOARDING_GUIDE.md` | 1-day ramp-up guide for new developers |
| `CHANGE_PLAN.md` | Safe step-by-step plan for a specific change |
| `REFACTOR_ROADMAP.md` | 3-month incremental modernization plan |

---

## Language Support

JavaScript/TypeScript · Python · PHP · Ruby · Java · C#/.NET · SQL · Bash · Go · Rust

---

## Core Principles

1. **Never shame the original developer** — every "bad" code had constraints we don't know
2. **Evidence-based conclusions only** — state confidence level explicitly
3. **Blast radius first** — map what could break before recommending changes
4. **Strangler Fig pattern always** — never big-bang rewrites
5. **Working > Perfect** — the goal is developer confidence, not code beauty
