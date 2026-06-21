# Sub-Skill: Safe Change Advisor

## Purpose
For any specific change a developer needs to make, produce the exact safest
step-by-step procedure — including what to test, what could go wrong, and
how to roll back if it does.

---

## The Safe Change Framework

Every change request gets evaluated against this framework:

```
CHANGE REQUEST ANALYSIS
────────────────────────────────────────────
1. UNDERSTAND: What exactly needs to change?
2. LOCATE: Where in the code does it live?
3. MAP: What is the blast radius?
4. TEST: What tests exist? What's the baseline?
5. PLAN: What is the safest order of operations?
6. VERIFY: How do we know the change worked correctly?
7. ROLLBACK: If it breaks, how do we undo it?
```

---

## Step 1: Change Request Classification

Before advising, classify the change:

### Type A: Pure Addition (Safest)
Adding new functionality without modifying existing code.
- New API endpoint
- New database table
- New utility function
- New config option

Risk: LOW — existing behavior unchanged
Approach: Add alongside existing code

### Type B: Behavioral Extension (Low Risk)
Extending existing functionality in additive ways.
- Adding a new field to an existing response
- Adding a new status to a state machine
- Adding validation to an existing endpoint

Risk: LOW-MEDIUM — existing behavior mostly unchanged
Approach: Add new behavior, verify old behavior still works

### Type C: Behavioral Modification (Medium Risk)
Changing how existing code works.
- Changing business logic
- Modifying database queries
- Changing authentication behavior
- Altering pricing calculations

Risk: MEDIUM-HIGH — existing behavior changes
Approach: Shadow mode first (run old and new in parallel), then switch

### Type D: Structural Refactoring (High Risk)
Changing how code is organized without changing behavior.
- Renaming functions/variables
- Moving code between files
- Extracting functions
- Changing module structure

Risk: HIGH — very easy to break hidden dependencies
Approach: Mechanical refactoring only, comprehensive test coverage first

### Type E: Data Migration (Highest Risk)
Changing the database schema or migrating data.
- Adding/removing columns
- Changing column types
- Restructuring tables
- Migrating data between schemas

Risk: VERY HIGH — data loss possible
Approach: Always backward-compatible, always reversible, always backup first

---

## Step 2: Pre-Change Safety Checklist

```
PRE-CHANGE SAFETY CHECKLIST
═══════════════════════════════════════════════
Change: [description]
Type: [A/B/C/D/E]
Target files: [list]
─────────────────────────────────────────────
[ ] Read all target files completely
[ ] Ran existing tests — all pass (baseline established)
[ ] Checked DEPENDENCY_MAP.md for blast radius
[ ] Checked LANDMINE_REGISTRY.md for target files
[ ] Created feature branch (never work on main directly)
[ ] Noted current production behavior to verify against
[ ] Identified rollback procedure BEFORE starting
[ ] Database backup confirmed (for Type E changes)
═══════════════════════════════════════════════
```

---

## Step 3: The Strangler Fig Strategy

For any significant change in legacy code, use the Strangler Fig pattern:
Never modify the old code directly — wrap it, redirect to new code, remove old.

```
PHASE 1: Build new version alongside old
─────────────────────────────────────────
// Old code (don't touch):
function calculatePrice(product, user) {
  return product.price * 1.0875  // Mystery tax
}

// New code (add alongside):
function calculatePriceV2(product, user, options = {}) {
  const taxRate = getTaxRateForRegion(user.region)  // Proper tax
  const discount = getApplicableDiscount(user, product)
  return (product.price * taxRate) * (1 - discount)
}

PHASE 2: Switch callers one by one
─────────────────────────────────────────
// routes/cart.js — switch to V2
// routes/checkout.js — switch to V2
// workers/invoices.js — switch to V2
// Verify each switch works before moving to next

PHASE 3: Remove old function when all callers migrated
─────────────────────────────────────────
// Only when: all callers use V2, tests pass, monitoring shows no issues
// Delete calculatePrice()
```

---

## Step 4: Database Change Procedures

### Safe Column Addition

```sql
-- STEP 1: Add column as nullable (backward compatible)
ALTER TABLE orders ADD COLUMN notes TEXT;
-- Old code that doesn't include 'notes' in INSERT still works

-- STEP 2: Deploy new code that writes to the column
-- (Old code ignores it, new code uses it)

-- STEP 3 (Optional later): Add NOT NULL constraint after all rows have data
-- Only do this after confirming no NULLs remain
ALTER TABLE orders ALTER COLUMN notes SET DEFAULT '';
UPDATE orders SET notes = '' WHERE notes IS NULL;
ALTER TABLE orders ALTER COLUMN notes SET NOT NULL;
```

### Safe Column Rename (3-Deploy Strategy)

```
Deploy 1: Add new column, write to BOTH old and new
  ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
  -- Code: writes to both 'name' AND 'full_name'

Deploy 2: Read from new column, still write to both
  -- Code: reads from 'full_name', writes to both

Deploy 3: Stop writing to old column, drop it
  ALTER TABLE users DROP COLUMN name;
  -- Code: reads and writes only 'full_name'

Why 3 deploys: Any rollback at any stage is safe.
              Never have a window where both old and new code
              could run against an incompatible schema.
```

### Safe Column Removal

```
NEVER do this:
  ALTER TABLE orders DROP COLUMN status;  -- Code still references it → crash

INSTEAD:
  Step 1: Find and remove ALL references in code
  Step 2: Deploy code with no references to column
  Step 3: Verify in production that column is not accessed
  Step 4: Drop the column
```

---

## Step 5: Testing Strategy for Legacy Code

### When No Tests Exist

```
CHARACTERIZATION TEST APPROACH:
─────────────────────────────────────────────
Don't test what the code SHOULD do.
Test what it ACTUALLY does.

Step 1: Run the function with real/prod-like data
Step 2: Record the output (even if output seems wrong)
Step 3: Write a test that asserts that exact output
Step 4: Now you have a safety net before changing

// Example characterization test:
test('calculatePrice does what it currently does', () => {
  const result = calculatePrice({ price: 100 }, { type: 2 })
  expect(result).toBe(108.75)  // Whatever the current output is
  // Now change the code — this test will catch regressions
})
```

### Minimum Test Coverage for Safe Change

For any Type C/D/E change, minimum tests needed:
1. **Happy path test** — normal expected behavior
2. **Edge case tests** — empty input, null, zero, max values
3. **Regression test** — specifically tests the thing being changed
4. **Integration test** — tests the change in context of the full flow

---

## Step 6: Rollback Procedures

Every change must have a defined rollback before starting.

### Code Rollback

```bash
# If using feature branches (recommended):
git revert HEAD           # Undo last commit
git push origin main      # Deploy reverted version

# Or: Revert to specific commit
git revert abc1234        # Create new commit that undoes abc1234

# For deployed systems:
# Vercel: vercel rollback
# Railway: railway rollback
# Custom: deploy previous Docker image tag
```

### Database Rollback

```bash
# Prisma:
npx prisma migrate resolve --rolled-back "migration_name"

# Sequelize:
npx sequelize-cli db:migrate:undo

# Raw SQL migrations:
# Each UP migration must have a corresponding DOWN migration
# Test: can you migrate up, then migrate down, without data loss?
```

### Feature Flag Rollback (Fastest)

```javascript
// Before deploying risky change, wrap in feature flag:
const USE_NEW_PRICING = process.env.USE_NEW_PRICING === 'true'

function calculatePrice(product, user) {
  if (USE_NEW_PRICING) {
    return calculatePriceV2(product, user)
  }
  return calculatePriceLegacy(product, user)
}

// Rollback = set USE_NEW_PRICING=false in env
// No code deploy needed, instant rollback
```

---

## Step 7: Change Plan Template

For every change request, produce this document:

```
SAFE CHANGE PLAN
═══════════════════════════════════════════════════
Change: [specific change requested]
Change Type: [A/B/C/D/E]
Risk Level: [🟢/🟡/🟠/🔴]
Estimated Effort: [hours]
─────────────────────────────────────────────────
TARGET FILES:
  [file]: [what changes in this file]
  [file]: [what changes in this file]

BLAST RADIUS:
  Direct impact:   [files that directly depend on targets]
  Indirect impact: [downstream effects]
  External impact: [API consumers, UI effects]

PRE-CHANGE STEPS:
  1. [First safety step]
  2. [Second safety step]
  ...

CHANGE PROCEDURE (exact order):
  Step 1: [Exact first change with code snippet]
  Step 2: [Exact second change]
  Step 3: [Verification step]
  ...

TESTS TO RUN:
  [ ] [specific test command]
  [ ] [specific behavior to verify manually]

VERIFICATION:
  How to confirm the change worked:
  - [Observable outcome 1]
  - [Observable outcome 2]

ROLLBACK PROCEDURE:
  If this breaks: [exact rollback steps, including commands]
  Time to rollback: [estimated minutes]

KNOWN RISKS:
  - [Risk 1]: [how to mitigate]
  - [Risk 2]: [how to mitigate]
═══════════════════════════════════════════════════
```
