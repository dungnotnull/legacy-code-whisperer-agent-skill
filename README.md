# 🔮 Legacy Code Whisperer

> *Decode, document, and safely navigate any legacy codebase.*

A Claude Agent Skill that reads any codebase — undocumented, ancient, or terrifying —
and tells you exactly what it does, what's dangerous to touch, and how to safely change it.

---

## The Problem

You inherited a codebase. There are no docs. The original developer is gone.
Function names like `processData2_FINAL` tell you nothing. You're scared to
change anything because you don't know what will break.

Legacy Code Whisperer fixes this.

---

## Quick Start

### Option A: Paste code, ask a question
> "I don't understand this code. [paste code] What does it do?"

### Option B: Full codebase analysis
```bash
python3 scripts/analyze_codebase.py --path ./my-app --output analysis.json --report
python3 scripts/generate_report.py --analysis analysis.json --app-name "My App"
```

### Option C: Before changing anything
```bash
python3 hooks/pre_change_gate.py --file lib/pricing.js --analysis analysis.json --change-type C
```

### Option D: Emergency (production broken, unfamiliar code)
> "Production is down and I don't understand this code" → immediate triage

---

## 7-Phase Analysis

| Phase | What It Does |
|-------|-------------|
| 🏺 **Code Archaeology** | Reconstruct intent, era, author patterns |
| 📜 **Business Logic Extraction** | Translate magic numbers into business rules |
| 🗺️ **Dependency Mapping** | Show exact blast radius of any change |
| 💣 **Landmine Detection** | Find every dangerous section before you touch it |
| 📚 **Onboarding Guide** | 1-day ramp-up instead of 3-week confusion |
| 🛡️ **Safe Change Advisor** | Exact safe procedure for your specific change |
| 🗓️ **Refactor Roadmap** | 3-month incremental modernization plan |

---

## Danger Levels

| Level | Meaning |
|-------|---------|
| 🟢 SAFE | Change freely |
| 🟡 CAUTION | Change with care |
| 🟠 RISKY | Wrap, don't modify directly |
| 🔴 LANDMINE | Do not touch without full analysis |
| 💀 CURSED | Leave alone — works by accident |

---

## What You Get

| File | Use It For |
|------|-----------|
| `CODEBASE_INTEL.md` | Understand what the codebase does |
| `BUSINESS_RULES.md` | Every business rule decoded from code |
| `DEPENDENCY_MAP.md` | Know what breaks before you touch anything |
| `LANDMINE_REGISTRY.md` | Avoid expensive mistakes |
| `ONBOARDING_GUIDE.md` | Get new team members productive fast |
| `CHANGE_PLAN.md` | Step-by-step safe procedure for your change |
| `REFACTOR_ROADMAP.md` | Modernize without breaking production |

---

## Sample Finding

```
🔴 LANDMINE LM-002: Empty Catch Block — Silent Stock Corruption
Location: orders.js line 35
Comment found: "// don't ask" — developer knew this was problematic

Risk: If stock update fails, the order is still created and confirmed,
but inventory becomes inaccurate. No alert, no log, no retry.

Fix: At minimum log the error. Better: wrap order creation and stock
update in a transaction so both succeed or both fail.
```

---

## Language Support

JavaScript/TypeScript · Python · PHP · Ruby · Java · C#/.NET · SQL · Go · Rust · Bash

---

*Never shames the original developer. Always evidence-based. Never recommends big-bang rewrites.*
