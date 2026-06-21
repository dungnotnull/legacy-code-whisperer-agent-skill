# Sub-Skill: Refactor Roadmap Builder

## Purpose
Build a realistic, phased modernization plan for legacy code that keeps production
running at all times. No big-bang rewrites. No "stop the world" refactors.
Every step is independently deployable and reversible.

---

## The Anti-Pattern: Big Bang Rewrite

```
WHY BIG BANG REWRITES FAIL:
──────────────────────────────────────────────────
Month 1:  "We'll rewrite everything in 6 months"
Month 3:  "We're 60% done but hit unexpected complexity"
Month 5:  "We need to maintain both systems now"
Month 7:  "The old system got new features while we rewrote"
Month 9:  "We're delayed, cutting scope"
Month 12: "The new system has different bugs"
Month 14: "We're considering another rewrite"

The result: Double the code, double the bugs, business disruption,
team demoralization, and often — the new code has the same problems.
```

```
THE RIGHT APPROACH: Strangler Fig Refactoring
──────────────────────────────────────────────────
Week 1-2:  Understand the system (this skill's prior phases)
Week 3-4:  Add test coverage to critical paths
Month 2:   Extract first well-defined module
Month 3:   Extract second module
Month 4+:  Continue module by module
Result:    System is incrementally modernized while always running
```

---

## Step 1: Refactor Priority Matrix

Score each module/file for refactor priority:

### Scoring Dimensions

| Dimension | Weight | Score 1-5 |
|-----------|--------|-----------|
| **Change Frequency** — How often does this get modified? | 30% | 1=never, 5=weekly |
| **Bug Density** — How often does this cause bugs? | 25% | 1=never, 5=constantly |
| **Business Criticality** — How important is this to the business? | 20% | 1=peripheral, 5=core |
| **Developer Pain** — How much does this slow down development? | 15% | 1=no pain, 5=dread it |
| **Technical Debt Severity** — How bad is the code quality? | 10% | 1=clean, 5=cursed |

**Priority Score = Weighted sum (0-5 scale)**

```
REFACTOR PRIORITY REGISTRY
──────────────────────────────────────────────────────────────────
Module               | Change | Bugs | Crit | Pain | Debt | Score
─────────────────────|────────|──────|──────|──────|──────|──────
lib/pricing.js       |   5    |  4   |  5   |  4   |  4   | 4.55 🔴
routes/orders.js     |   5    |  3   |  5   |  4   |  3   | 4.15 🔴
lib/auth.js          |   2    |  1   |  5   |  2   |  4   | 2.85 🟡
workers/legacy-sync.js|  1    |  3   |  4   |  4   |  5   | 2.90 🟡
utils/helpers.js     |   4    |  2   |  2   |  3   |  3   | 2.90 🟡
models/User.js       |   3    |  2   |  4   |  2   |  2   | 2.70 🟢
config/database.js   |   1    |  1   |  5   |  1   |  2   | 2.00 🟢
──────────────────────────────────────────────────────────────────
```

---

## Step 2: Dependency-Aware Sequencing

Good refactor sequence = lowest dependency first.

```
REFACTOR SEQUENCING RULE:
Refactor leaves before trunks.
Refactor utilities before the things that use them.
Never refactor a module that other unrefactored modules depend on.

WRONG ORDER:          RIGHT ORDER:
────────────          ────────────
1. lib/auth.js        1. utils/string-helpers.js (no deps)
   (12 dependents)    2. config/tax-rates.js (1 dependent)
2. routes/*.js        3. lib/pricing.js (fewer deps now clean)
3. utils/*.js         4. lib/auth.js (after utils are clean)
                      5. routes/*.js (after lib is clean)
```

### Dependency Tree for Sequencing

```
DEPENDENCY-ORDERED REFACTOR SEQUENCE:
═══════════════════════════════════════════════
Layer 0 (no dependencies — refactor first):
  utils/string-helpers.js
  utils/date-helpers.js
  config/constants.js

Layer 1 (depends only on Layer 0):
  config/tax-rates.js
  lib/validators.js

Layer 2 (depends on Layer 0-1):
  lib/pricing.js
  lib/mailer.js

Layer 3 (depends on Layer 0-2):
  lib/auth.js
  lib/order-processor.js

Layer 4 (depends on all below):
  routes/*.js
  workers/*.js

Layer 5 (entry points — refactor last):
  app.js / server.js / index.js
═══════════════════════════════════════════════
```

---

## Step 3: Module Extraction Template

For each module to refactor:

```
MODULE EXTRACTION PLAN: lib/pricing.js
═══════════════════════════════════════════════
Current state: 387-line file doing: tax calculation, discount logic,
               price formatting, audit logging, cache management

Problem: Too many responsibilities. Hard to test. Hard to change.
         Every order-related feature requires touching this file.

Target state: 4 focused modules:
  lib/tax-calculator.js    — pure tax calculation
  lib/discount-engine.js   — discount rules and application
  lib/price-formatter.js   — display formatting
  lib/pricing-audit.js     — audit logging
  lib/pricing.js           — thin orchestrator (stays, but simplified)
─────────────────────────────────────────────────
EXTRACTION STEPS:

Week 1: Add characterization tests to pricing.js (20+ tests)
  Test every function's current output with realistic data
  Goal: Test suite protects against regression during refactor

Week 2: Extract lib/tax-calculator.js
  Move: getTaxRate(), calculateTax(), validateTaxRegion()
  Keep: pricing.js calls tax-calculator.js (behavior unchanged)
  Test: Run characterization tests — all must still pass

Week 3: Extract lib/discount-engine.js
  Move: applyDiscount(), getApplicableDiscounts(), stackDiscounts()
  Keep: pricing.js calls discount-engine.js
  Test: Run characterization tests — all must still pass

Week 4: Extract lib/price-formatter.js
  Move: formatCurrency(), formatPercent(), roundToNearest()
  Test: Run characterization tests

Month 2: Extract lib/pricing-audit.js
  Move: logPricingCalculation(), auditDiscount()
  Test: Verify audit logs still appear in database

Final: Simplify lib/pricing.js to orchestrator only
  Result: ~40 lines instead of 387, easy to understand
═══════════════════════════════════════════════
```

---

## Step 4: The 3-Month Roadmap Template

```
LEGACY MODERNIZATION ROADMAP
═══════════════════════════════════════════════
System: [App name]
Analysis date: [date]
Team size: [N developers]
Approach: Incremental strangler fig (no big bang)
─────────────────────────────────────────────
MONTH 1: SAFETY NET
Goal: Add test coverage to critical paths before changing anything

Week 1-2: Characterization tests for top 3 priority modules
  [ ] lib/pricing.js — 20 characterization tests
  [ ] lib/auth.js — 15 characterization tests
  [ ] routes/orders.js — 10 integration tests

Week 3-4: CI/CD setup
  [ ] Automated test run on every PR
  [ ] Lint configuration (catch common errors)
  [ ] Pre-commit hooks (prevent committing broken code)

Success criteria: Can make a change to any critical file
                  and know within 2 minutes if it broke something

─────────────────────────────────────────────
MONTH 2: FOUNDATION MODERNIZATION
Goal: Clean up the utilities and shared code everything depends on

Week 1-2: Extract and modernize utils/
  [ ] utils/string-helpers.js — cleanup + tests
  [ ] utils/date-helpers.js — replace moment.js with date-fns
  [ ] utils/validation.js — add zod schema validation

Week 3-4: Modernize configuration
  [ ] config/ — validate all env vars on startup
  [ ] Centralize all magic numbers into config/constants.js
  [ ] Document every config value and its business meaning

Success criteria: All utility functions have tests.
                  No magic numbers in business logic files.

─────────────────────────────────────────────
MONTH 3: BUSINESS LOGIC MODERNIZATION
Goal: Clean up the most-changed, most-painful business logic

Week 1-2: lib/pricing.js extraction (see Module Extraction Plan above)

Week 3: lib/auth.js modernization
  [ ] Add proper error types instead of string errors
  [ ] Add refresh token support (without breaking existing JWTs)
  [ ] Centralize all JWT configuration

Week 4: Route organization
  [ ] Extract validation middleware from route handlers
  [ ] Standardize error response format across all routes
  [ ] Add request/response logging to all routes

Success criteria: The 3 highest-pain files are refactored.
                  Developer velocity measurably improved.

─────────────────────────────────────────────
ONGOING (Month 4+): INCREMENTAL IMPROVEMENT
Continue module by module, highest priority first:
  - Module N: [refactor plan]
  - Module N+1: [refactor plan]

COMPLETION CRITERIA:
  [ ] All critical paths have 80%+ test coverage
  [ ] No file over 200 lines (or justified exception)
  [ ] No circular dependencies
  [ ] All magic numbers documented in constants
  [ ] New developer can be productive in 1 day (using ONBOARDING_GUIDE.md)
═══════════════════════════════════════════════
```

---

## Step 5: Technology Migration Guide

For modernizing specific technology choices:

### Callback Hell → Async/Await

```javascript
// BEFORE (callback hell):
function getOrderWithUser(orderId, callback) {
  db.query('SELECT * FROM orders WHERE id = ?', [orderId], (err, order) => {
    if (err) return callback(err)
    db.query('SELECT * FROM users WHERE id = ?', [order.userId], (err, user) => {
      if (err) return callback(err)
      callback(null, { order, user })
    })
  })
}

// AFTER (async/await):
async function getOrderWithUser(orderId) {
  const order = await db.query('SELECT * FROM orders WHERE id = ?', [orderId])
  const user = await db.query('SELECT * FROM users WHERE id = ?', [order.userId])
  return { order, user }
}

// MIGRATION STRATEGY:
// Step 1: Add promisify wrapper to DB module
// Step 2: Rewrite one function at a time
// Step 3: Update callers to use await
// Step 4: When all callers are updated, remove old callback version
```

### require() → ES Modules

```javascript
// This migration requires careful planning — mixing is messy

// STRATEGY: Don't migrate until necessary
// IF migrating: Add "type": "module" to package.json
//               Rename files .js → .mjs during transition
//               Update all import paths
// RISK: High. Do last, after all other refactoring done.
```

### Raw SQL → ORM (or ORM → Raw SQL)

```javascript
// Moving to ORM is often the WRONG direction for complex queries
// Moving FROM ORM for complex queries is often RIGHT

// RULE: Use ORM for simple CRUD, raw SQL for complex queries
// Don't migrate everything — evaluate per query

// Safe migration: ORM sits alongside raw SQL
// const users = await User.findAll()           // ORM for simple
// const report = await db.query(complexSQL)    // Raw for complex
```

---

## Phase 7 Output

```markdown
# Refactor Roadmap

## Executive Summary
[Current state, target state, timeline, risk level]

## Priority Registry
[Scored modules in priority order]

## 3-Month Plan
[Week-by-week breakdown with specific tasks]

## Module Extraction Plans
[Detailed extraction plan for top 3 modules]

## Technology Migration Notes
[Any technology-level migrations needed and their risk]

## Definition of Done
[What "refactoring complete" looks like for this codebase]
```
