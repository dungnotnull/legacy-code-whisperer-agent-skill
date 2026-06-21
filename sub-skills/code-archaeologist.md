# Sub-Skill: Code Archaeologist

## Purpose
Reconstruct the intent, history, and mental model behind any piece of code —
even without comments, documentation, or the original developer.

---

## Step 1: Era & Author Pattern Detection

### Dating the Code

Different eras have distinct patterns. Identifying when code was written
helps predict its structure and typical problems.

| Signal | Era | Typical Problems |
|--------|-----|-----------------|
| `var` everywhere, no `const`/`let` | Pre-2015 JS | Hoisting bugs, global pollution |
| `$.ajax(`, `$(document).ready(` | 2010-2018 jQuery | Callback hell, DOM coupling |
| `require(`, `module.exports` | 2012-2018 Node | CommonJS module confusion |
| `async/await` + `import/export` | 2017+ | Generally cleaner |
| `callback(err, result)` pattern | Pre-2015 Node | Error handling inconsistency |
| `Promise.then().catch()` | 2015-2018 | Mixed with callbacks |
| Class components everywhere | React 2016-2019 | Before hooks |
| Functional components + hooks | React 2019+ | Modern |
| `mysql_query(` (not `mysqli`) | Pre-2013 PHP | SQL injection risk |
| `global $db` in every function | Pre-framework PHP | |
| Django 1.x patterns | Pre-2017 Python | |

### Author Pattern Recognition

A single codebase often has multiple "authors" — different developers
who worked at different times. Identify them by:

- **Naming conventions** (camelCase vs snake_case vs PascalCase mixing)
- **Comment style** (// vs /\* \*/ vs # vs different languages)
- **Error handling patterns** (some functions handle errors, others don't)
- **Abstraction level** (some code is highly abstracted, other sections are raw)
- **Magic number density** (concentrated in specific files = one author's style)

Output: "This codebase has **3 distinct author patterns**:
- Author A (database layer): uses class-based OOP, comprehensive error handling
- Author B (API routes): callback-style, minimal validation
- Author C (utility files): functional style, heavy use of .reduce()/.map()"

---

## Step 2: Intent Reconstruction

For every function/module, reconstruct intent using this algorithm:

### Intent Reconstruction Algorithm

```
1. READ THE FUNCTION NAME (even if terrible)
   - "processData" → some data transformation
   - "doStuff2" → replacement for doStuff, added later
   - "fixBugWithOrders" → patches an order processing bug
   - "TEMP_dont_delete" → critical code, developer was afraid to commit to naming it

2. READ THE INPUTS AND OUTPUTS
   - What data goes in? (type, shape, constraints)
   - What data comes out? (or what side effect happens)
   - What errors are handled? (reveals edge cases the developer knew about)

3. READ THE COMMENTS (if any exist)
   - Old comments: "// TODO: fix this" (never fixed, probably important)
   - Warning comments: "// DON'T REMOVE" (something bad happened once)
   - Dated comments: "// 2019-03-15 added for client X" (feature flag era)
   - Apologetic comments: "// I know this is bad but..." (known debt)

4. READ THE TESTS (if any exist)
   - Test names often reveal intent better than code names
   - Test data reveals expected inputs/outputs
   - Skipped tests reveal known broken functionality

5. FOLLOW THE CALL CHAIN
   - Who calls this function?
   - What does it call?
   - The call chain often reveals more intent than the function itself
```

### Common Disguised Patterns

| What the code looks like | What it actually is |
|--------------------------|---------------------|
| 200-line function doing "everything" | Missing abstraction — was written once and grew |
| Identical code in 3 files | Copy-paste engineering — should be one shared function |
| Function called from 1 place | Premature abstraction — was probably inline code first |
| Config object with 40 keys | Feature flag system that grew organically |
| `if (user.type === 3)` | Enum that was never created — 3 = "admin" |
| `setTimeout(fn, 100)` | Race condition fix — something isn't ready synchronously |
| Global variable set in function A, read in function B | Hidden coupling that will bite you |
| Comment: "don't change the order" | Initialization order dependency |
| Nested ternary 4 levels deep | Complex business rule that needs its own function |
| `catch(e) {}` (empty catch) | Error being silently swallowed — real problems hidden |

---

## Step 3: Technical Debt Classification

For each section of code, classify the debt type:

### Debt Type A: Intentional Shortcuts ("We'll fix this later")
- **Detection**: Comments like "TODO", "FIXME", "HACK", "TEMP"
- **Risk**: Usually low — developer knew it was a shortcut
- **Action**: Document what the proper solution should be

### Debt Type B: Accretion Debt (Built up slowly over time)
- **Detection**: Functions that are 300+ lines, files that do everything
- **Risk**: Medium — unclear what can be safely extracted
- **Action**: Identify boundaries before touching

### Debt Type C: Knowledge Debt (Original developer left with context)
- **Detection**: Complex business logic with no explanation, magic numbers
- **Risk**: High — behavior may be important but reasons are unknown
- **Action**: Document all observable behavior before changing anything

### Debt Type D: Survival Code ("It worked once, don't touch it")
- **Detection**: Comments like "DO NOT REMOVE", code that looks wrong but is in a critical path
- **Risk**: Very High — likely compensating for something non-obvious
- **Action**: Test extensively before touching, or leave alone

### Debt Type E: Abandoned Features
- **Detection**: `if (featureFlag && false)` patterns, commented-out code blocks, dead function paths
- **Risk**: Low — safely removable after confirming not used
- **Action**: Remove in separate cleanup PR

---

## Step 4: Codebase Structure Analysis

Map the overall structure:

```
CODEBASE STRUCTURE CARD
═══════════════════════════════════════════════════
Language(s):       [detected]
Framework(s):      [detected]
Era:               [estimated year range]
Author patterns:   [X distinct author styles]
Size:              [lines of code / file count]
Test coverage:     [estimate: none / minimal / partial / good]
Documentation:     [none / comments only / README / full docs]
─────────────────────────────────────────────────
Core modules:
  [module name] → [what it does in plain English]
  [module name] → [what it does in plain English]

Entry points:
  [how the app starts / where requests come in]

Data stores:
  [databases, files, external services found]

Critical paths:
  [the most important workflows based on code analysis]

Known landmines (preliminary):
  [files/functions flagged for Phase 4 deeper analysis]
═══════════════════════════════════════════════════
```

---

## Step 5: Confidence Scoring

For every interpretation, state your confidence:

| Confidence | Meaning | Statement |
|------------|---------|-----------|
| **HIGH** | Code behavior is clear and deterministic | "This function definitively does X" |
| **MEDIUM** | Behavior is likely but has edge cases | "This appears to do X, though edge cases exist when Y" |
| **LOW** | Inferred from context, not certain | "Based on how it's called, this likely does X, but verify" |
| **UNKNOWN** | Genuinely cannot determine | "This code's purpose is unclear — needs runtime testing to determine" |

**Never state LOW/UNKNOWN as HIGH confidence.** The developer needs to know when they're on uncertain ground.

---

## Phase 1 Output

```
CODE ARCHAEOLOGY REPORT
═══════════════════════════════════════════════════
Codebase: [name/description]
Analyzed: [date]
Language: [languages detected]
Era: [estimated: e.g. "2016-2018 Node.js, with newer sections from 2022"]
─────────────────────────────────────────────────
STRUCTURAL OVERVIEW:
[Plain English description of what this codebase is and does]

AUTHOR PATTERNS:
[Description of distinct coding styles found]

TECHNICAL DEBT SUMMARY:
  Type A (Intentional): X instances
  Type B (Accretion):   X instances
  Type C (Knowledge):   X instances — HIGHEST RISK
  Type D (Survival):    X instances — DO NOT TOUCH
  Type E (Abandoned):   X instances — Safe to remove

PRELIMINARY LANDMINE FLAGS:
  🔴 [file/function]: [why flagged]
  🟠 [file/function]: [why flagged]

CONFIDENCE IN ANALYSIS: [High / Medium / Low]
AREAS OF UNCERTAINTY: [what needs runtime testing to confirm]
═══════════════════════════════════════════════════
```
