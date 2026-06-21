# PROJECT-detail.md — Legacy Code Whisperer

## 1. Problem Statement

### The Gap

Every developer eventually inherits code they didn't write. Existing tools fail this scenario:

- **Linters/SonarQube** — flag style issues, miss business logic and intent
- **Documentation generators** (JSDoc, Sphinx) — only work if comments already exist
- **Code search tools** — find code, don't explain WHY it exists
- **AI coding assistants** — great at writing new code, weak at explaining unfamiliar
  existing code with full context of risk and history
- **Git blame/history** — shows WHO and WHEN, not WHY or WHAT IT MEANS

**The actual problem developers face:**
1. Code with zero documentation and the original author is gone
2. Fear of changing anything because consequences are unknown
3. No way to know what's safe to refactor vs. what's load-bearing
4. New team members take weeks to become productive
5. Technical debt discussions are vague ("this code is bad") not actionable

### Market Context

- Average enterprise codebase: 60-80% "legacy" by typical definitions (no active original author)
- Developer onboarding time industry average: 3-9 months to full productivity
- Estimated 23% of developer time spent understanding existing code vs. writing new code
- "We don't know why this works" is one of the most common phrases in engineering retros

---

## 2. Design Philosophy

### Philosophy 1: Forensics, Not Judgment
This skill never says "this code is terrible." It says "here's what this code does,
here's likely why it was written this way, here's the risk if you change it."
Judgment without actionable insight just creates anxiety.

### Philosophy 2: Confidence Calibration
Every claim about code behavior is labeled HIGH/MEDIUM/LOW/UNKNOWN confidence.
Overconfident wrong analysis is more dangerous than admitted uncertainty.

### Philosophy 3: Blast Radius Before Opinion
Before recommending any change, map exactly what depends on the code in question.
Developers make better decisions with complete dependency information.

### Philosophy 4: Strangler Fig, Never Big Bang
Every refactor recommendation follows the pattern: build new alongside old,
migrate callers incrementally, remove old only when fully migrated.
Big-bang rewrites are explicitly discouraged with reasoning.

### Philosophy 5: The Original Developer Was Smart
Code that looks bad in isolation often made sense given constraints (deadline,
unclear requirements, since-changed business rules, framework limitations at the time).
This skill actively looks for "why this made sense" before concluding "this is wrong."

---

## 3. Phase Architecture

### Phase Data Flow

```
Input Codebase
    │
    ▼
Phase 1: CODE ARCHAEOLOGY
    │ → Era detection, author patterns, intent reconstruction
    │ → Technical debt classification (5 types)
    │ → Preliminary landmine flags
    ▼
Phase 2: BUSINESS LOGIC EXTRACTION
    │ → Magic number/string decoding
    │ → Conditional → business rule translation
    │ → Hidden side effect documentation
    │ → Implicit state machine reconstruction
    │ → Authorization model extraction
    ▼
Phase 3: DEPENDENCY MAPPING
    │ → Import/dependency graph
    │ → Database column-level blast radius
    │ → Circular dependency detection
    │ → Hidden coupling detection (globals, shared DB state, events)
    │ → Safe zone identification
    ▼
Phase 4: LANDMINE DETECTION
    │ → Timing landmines (race conditions, setTimeout-as-sync)
    │ → Data integrity landmines (non-atomic ops, float money)
    │ → Security landmines (injection, eval, hardcoded secrets)
    │ → Performance landmines (N+1, unindexed, unbounded loads)
    │ → Cursed patterns (silent failures, accidental correctness)
    ▼
Phase 5: ONBOARDING GUIDE GENERATION
    │ → Reconstructed setup instructions
    │ → Codebase map with plain English
    │ → Main flow documentation
    │ → Critical gotchas list
    ▼
Phase 6: SAFE CHANGE ADVISOR
    │ → Change type classification (A-E)
    │ → Strangler fig procedure
    │ → Database change procedures (add/rename/remove)
    │ → Testing strategy (characterization tests)
    │ → Rollback procedures
    ▼
Phase 7: REFACTOR ROADMAP
    │ → Priority scoring matrix
    │ → Dependency-aware sequencing
    │ → Module extraction plans
    │ → 3-month phased timeline
    ▼
OUTPUT: 7 Intelligence Documents
```

---

## 4. Sub-Skill Specifications

### Phase 1: Code Archaeologist
**Key algorithms:**
- Era detection via syntax pattern matching (var vs let/const, callback vs async/await, etc.)
- Author pattern clustering via naming convention + style consistency analysis
- Intent reconstruction algorithm (5-step: name → I/O → comments → tests → call chain)
- 5-type technical debt classification (Intentional/Accretion/Knowledge/Survival/Abandoned)

### Phase 2: Business Logic Extractor
**Key algorithms:**
- Magic number registry with pattern-based meaning inference
- Conditional logic → natural language translation template
- Side effect scanner (8 effect types: DB writes, file I/O, API calls, cache, events, globals, logs, queues)
- State machine reconstruction from status field analysis
- Authorization model extraction from middleware/role-check patterns

### Phase 3: Dependency Mapper
**Key algorithms:**
- Import graph construction (handles require/import/from patterns across languages)
- Column-level database blast radius (READ vs WRITE locations per column)
- Circular dependency detection (cycle detection in import graph)
- Hidden coupling detection (4 types: global vars, shared DB state, event bus, env vars)
- Safe zone identification (low blast radius + has tests + pure functions)

### Phase 4: Landmine Detector
**5 landmine categories, 18+ specific patterns:**
1. Timing landmines (setTimeout-as-sync, order-dependent init, shared mutable async state)
2. Data integrity landmines (non-atomic ops, soft-delete inconsistency, float currency)
3. Security landmines (SQL injection, mass assignment, open redirect, exposed secrets, eval)
4. Performance landmines (N+1 in loop, unindexed WHERE, unbounded memory load)
5. Cursed patterns (silent error swallowing, implicit truthiness, load-bearing requires, accidental timing correctness)

### Phase 5: Onboarding Guide Generator
**7-section structure** matching the natural question progression of a new developer:
What it does → Setup → Organization → Main flows → Database → Gotchas → First change

### Phase 6: Safe Change Advisor
**5-type change classification (A-E)** with risk-appropriate procedures:
- Type A (Pure Addition): LOW risk, add alongside
- Type B (Behavioral Extension): LOW-MEDIUM risk, additive only
- Type C (Behavioral Modification): MEDIUM-HIGH risk, shadow mode first
- Type D (Structural Refactoring): HIGH risk, mechanical only with full test coverage
- Type E (Data Migration): VERY HIGH risk, always reversible, always backed up

**Database change procedures:** Safe column addition (nullable first), safe rename
(3-deploy strategy), safe removal (reference removal → verify → drop)

### Phase 7: Refactor Roadmap Builder
**Key algorithms:**
- Weighted priority scoring (Change Frequency 30%, Bug Density 25%, Business Criticality 20%,
  Developer Pain 15%, Technical Debt Severity 10%)
- Dependency-aware sequencing (leaves before trunks — refactor zero-dependency files first)
- Module extraction template (characterization tests → incremental extraction → verification)
- 3-month phased timeline template (Safety Net → Foundation → Business Logic → Ongoing)

---

## 5. Script Architecture

### analyze_codebase.py

**Automated detection (no AI required):**
- 12 landmine pattern types via regex (SQL injection, eval, hardcoded secrets, empty
  catches, unhandled promises, N+1 queries, float currency, global mutation, etc.)
- File metrics: lines, functions, complexity (rough cyclomatic), magic numbers, TODOs,
  danger comments, empty catches
- Language detection (10+ languages by extension)
- Import dependency graph construction
- Blast radius calculation (direct + indirect dependents)
- Health score calculation (0-100, severity-weighted deductions)
- Hotspot identification (danger score ranking)

**Output:** JSON consumable by both generate_report.py and AI agent

### generate_report.py

**7 document generators**, each pre-populated with automated findings where possible
(health scores, blast radii, hotspot files) and templated for AI agent completion
where deep code reading is required (business rule extraction, onboarding narrative).

### hooks/pre_change_gate.py

**Interactive safety gate** that:
- Checks if target file contains CURSED or LANDMINE patterns
- Calculates blast radius and blocks if extreme (>15 files) combined with risky change type
- Generates change-type-specific required safety steps
- Returns exit code 0 (proceed) or 1 (blocked) for CI/CD integration
- `--force` flag available for informed override

### hooks/post_change_verify.py

**Before/after comparison** that:
- Diffs issue lists between two analysis runs
- Reports new issues introduced and issues resolved
- Compares health score delta
- Compares blast radius delta for specific file
- Returns exit code 0 (clean) or 1 (new critical issues) for CI/CD gating

---

## 6. Reference Architecture

### legacy-pattern-decoder.md
5-part dictionary: Naming conventions → Common code smells with origin stories →
Framework-specific patterns (jQuery, callback hell, AngularJS, class components, old PHP) →
Database pattern archaeology → Comment translation guide

### worked-example.md
Complete 7-phase walkthrough using a realistic 50-line legacy Node.js order processing
module containing 5 stacked landmines (SQL injection ×3, empty catch, negative stock
possible), demonstrating exactly how each phase output should look.

---

## 7. Limitations

- **Cannot execute code**: All analysis is static; runtime behavior in edge cases requires
  actual testing, which the skill recommends but cannot perform itself
- **Cannot access git history directly**: Recommends git blame/log investigation but
  doesn't have native git integration in v1.0
- **Regex-based pattern detection has false positives/negatives**: The automated scanner
  is a starting point; AI agent deep-reading is required for full accuracy
- **Cannot verify business rule correctness**: Extracts what the code DOES, cannot confirm
  this matches actual business intent without stakeholder verification
- **Large codebases**: Very large codebases (1000+ files) may need directory-by-directory
  analysis rather than single full-codebase scan due to context limits
