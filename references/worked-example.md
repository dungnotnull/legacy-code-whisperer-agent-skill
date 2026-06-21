# Worked Example: Complete Legacy Code Analysis

This example demonstrates the expected AI agent output across all 7 phases,
using a realistic legacy Node.js e-commerce order processing module.

---

## Example Input

```javascript
// orders.js - last meaningful comment from 2019
// TODO: refactor this someday

var express = require('express')
var router = express.Router()
var db = require('../db')

function calcTotal(items, usr) {
  var t = 0
  for (var i = 0; i < items.length; i++) {
    t = t + items[i].price * items[i].qty
  }
  if (usr.type == 2) {
    t = t * 0.9  // VIP discount
  }
  t = t * 1.0875
  return t
}

router.post('/create', function(req, res) {
  var items = req.body.items
  var userId = req.body.userId

  db.query('SELECT * FROM users WHERE id = ' + userId, function(err, users) {
    if (err) {
      console.log(err)
      return
    }
    var usr = users[0]
    var total = calcTotal(items, usr)

    db.query('INSERT INTO orders (user_id, total, status) VALUES (' + userId + ', ' + total + ', "pending")', function(err, result) {
      // don't ask
      try {
        for (var i = 0; i < items.length; i++) {
          db.query('UPDATE products SET stock = stock - ' + items[i].qty + ' WHERE id = ' + items[i].id)
        }
      } catch (e) {}

      setTimeout(function() {
        sendConfirmationEmail(usr.email, result.insertId)
      }, 1000)

      res.json({ orderId: result.insertId, total: total })
    })
  })
})

router.get('/list', function(req, res) {
  db.query('SELECT * FROM orders WHERE user_id = ' + req.query.userId, function(err, orders) {
    res.json(orders)
  })
})

module.exports = router
```

---

## Phase 1 Output — Code Archaeology

**Phase Summary:**
```
### Phase 1: Code Archaeology
Decoded: Pre-2015 Node.js callback-style order processing module
Danger Level: 🔴 Risky
Key Insight: This file has 5 distinct CRITICAL security/data issues stacked together
```

**Era & Author Detection:**
- `var` everywhere, no `const`/`let` → Pre-2015 JavaScript
- Callback-style `function(err, result)` → Pre-Promise/async-await Node.js
- Single author pattern throughout (consistent style)
- Last comment dated 2019 — file likely untouched for 5+ years
- Comment "TODO: refactor this someday" — developer knew about debt, never addressed

**Intent Reconstruction:**
- `calcTotal()`: Calculates order total with VIP discount (user type 2) and tax
- `/create`: Creates an order, decrements inventory, sends confirmation email
- `/list`: Lists orders for a given user

**Technical Debt Classification:**
- Type C (Knowledge Debt): "VIP discount" comment but no documentation on what user type 2 means elsewhere
- Type D (Survival Code): `// don't ask` comment + empty catch — developer knew this was fragile

---

## Phase 2 Output — Business Logic Extraction

**Magic Values Decoded:**

| Value | Location | Business Meaning | Confidence |
|-------|----------|-----------------|------------|
| `0.9` | calcTotal:9 | VIP discount = 10% off | HIGH |
| `1.0875` | calcTotal:11 | Tax rate 8.75% (likely CA) | HIGH |
| `usr.type == 2` | calcTotal:8 | User type 2 = VIP/Premium customer | MEDIUM (not documented elsewhere) |
| `1000` (setTimeout) | create:18 | Assumed 1 second is "enough time" before sending email | LOW — appears arbitrary |

**Business Rule Extracted:**
> "BR-001: VIP Pricing — Customers with account type 2 (VIP) receive a 10% discount
> on their order subtotal before tax is applied. Sales tax of 8.75% is applied to all orders."

**Hidden Side Effects Found:**

```
FUNCTION: POST /create
Primary: Creates an order
Hidden 1: Decrements product stock (can go negative — no check!)
Hidden 2: Sends confirmation email (fire-and-forget, 1-second delay)
Hidden 3: Silently swallows ANY error in stock update (empty catch)
```

---

## Phase 3 Output — Dependency Mapping

**Blast Radius for `calcTotal()`:**
```
Direct dependents: 1 (router.post('/create'))
Indirect dependents: Anything calling POST /orders/create
External impact: Frontend checkout flow, any mobile app client
```

**Hidden Coupling Found:**
- `req.body.items` assumes specific shape `{price, qty, id}` — not validated anywhere
- No foreign key constraint visible between orders.user_id and users.id (assumed from query pattern)

---

## Phase 4 Output — Landmine Detection

```
LANDMINE REGISTRY
═══════════════════════════════════════════════════

🔴 LANDMINE LM-001: SQL Injection (3 instances)
Location: orders.js lines 24, 31, 39, 46
Description: User input concatenated directly into SQL strings
Evidence: 'SELECT * FROM users WHERE id = ' + userId
Risk: An attacker can pass userId = "1 OR 1=1" to dump all users,
      or worse, inject destructive SQL.
Fix: Use parameterized queries:
  db.query('SELECT * FROM users WHERE id = ?', [userId], callback)

🔴 LANDMINE LM-002: Empty Catch Block — Silent Stock Corruption
Location: orders.js line 35
Description: Stock decrement errors are silently swallowed
Comment found: "// don't ask" — developer knew this was problematic
Risk: If stock update fails, the order is still created and confirmed,
      but inventory becomes inaccurate. No alert, no log, no retry.
Fix: At minimum log the error. Better: wrap order creation and stock
     update in a transaction so both succeed or both fail.

🔴 LANDMINE LM-003: Negative Stock Possible
Location: orders.js line 32
Description: Stock decremented without checking if sufficient stock exists
Risk: Can oversell inventory — stock goes negative, no validation
Fix: Add WHERE stock >= ? check, verify affected rows = 1

🟠 RISKY LM-004: setTimeout as Email Delay
Location: orders.js line 38
Description: 1-second delay before sending email — unclear purpose
Risk: If this was meant to "wait" for the order to be fully committed,
      1 second is an unreliable assumption under load
Fix: Send email after confirming all DB operations succeeded, not on a timer

🟠 RISKY LM-005: No Input Validation on Order Items
Location: orders.js line 14 (req.body.items)
Description: Items array shape is assumed, never validated
Risk: Malformed request could crash the server or create corrupt orders
Fix: Add schema validation (e.g., with Joi or manual checks) before processing

💀 CURSED: None found — but LM-002 is borderline given developer's own
   "don't ask" comment suggesting unknown failure modes were observed.
═══════════════════════════════════════════════════
```

---

## Phase 5 Output — Onboarding Guide (excerpt)

```markdown
## Things That Will Catch You Out

**1. This file has SQL injection vulnerabilities**
Every query concatenates user input directly. DO NOT add new queries
following this pattern. Use parameterized queries for anything new.

**2. Stock can go negative**
There's no check preventing overselling. If you're debugging "negative
stock" reports, this is why.

**3. The empty catch block is hiding bugs**
Line 35 has `catch (e) {}` — if stock updates have been failing silently,
you won't see it in logs. Check the database directly if investigating
inventory discrepancies.

**4. "User type 2" means VIP**
There's no enum or constant for this. Just tribal knowledge now documented
in BUSINESS_RULES.md.
```

---

## Phase 6 Output — Safe Change Plan (example: "Add a shipping cost field")

```
SAFE CHANGE PLAN
═══════════════════════════════════════════════════
Change: Add shipping cost to order total calculation
Change Type: B (Behavioral Extension)
Risk Level: 🟡 MEDIUM (touches calcTotal, which has 1 dependent, but
            also touches the SQL injection landmine area)
─────────────────────────────────────────────────
RECOMMENDED APPROACH (Strangler Fig):

Step 1: Create new function alongside old (don't modify calcTotal directly)
  function calcTotalV2(items, usr, shippingCost = 0) {
    const subtotal = items.reduce((sum, item) => sum + item.price * item.qty, 0)
    const discount = usr.type === 2 ? subtotal * 0.1 : 0
    const taxableAmount = subtotal - discount
    const tax = taxableAmount * 0.0875
    return taxableAmount + tax + shippingCost
  }

Step 2: ALSO fix the SQL injection while you're in this file (since you're
  touching it anyway — recommended bundling for this specific case):
  db.query('SELECT * FROM users WHERE id = ?', [userId], callback)

Step 3: Switch /create route to use calcTotalV2 with shipping param

Step 4: Add test verifying old behavior preserved when shippingCost = 0
  (regression test against calcTotal's known output)

Step 5: Remove old calcTotal once confirmed working in production

TESTS TO RUN:
  - Manual: Create order with VIP user, verify 10% discount + tax + shipping
  - Manual: Create order with regular user, verify tax + shipping only
  - Regression: Compare new total vs old total when shipping = 0 (should match)

ROLLBACK PROCEDURE:
  git revert <commit-hash>
  Time to rollback: < 2 minutes (no DB schema change)

KNOWN RISKS:
  - If frontend doesn't send shippingCost, defaults to 0 (safe)
  - SQL injection fix changes query interface slightly — verify db wrapper
    library supports parameterized queries (most do)
═══════════════════════════════════════════════════
```

---

## Phase 7 Output — Refactor Roadmap (excerpt)

```
PRIORITY REGISTRY
─────────────────────────────────────────────
File: orders.js
Change Frequency: HIGH (core business file)
Bug Density: HIGH (SQL injection, silent failures)
Business Criticality: VERY HIGH (revenue-critical path)
Developer Pain: HIGH (callback style, hard to test)
Technical Debt Severity: VERY HIGH (5 landmines found)
PRIORITY SCORE: 4.7/5 🔴 — TOP REFACTOR PRIORITY

MODULE EXTRACTION PLAN:
Week 1: Add characterization tests for calcTotal() and both routes
Week 2: Fix SQL injection (parameterized queries) — Type C change, test thoroughly
Week 3: Extract calcTotal to lib/pricing.js, convert to async/await
Week 4: Add transaction wrapping for order creation + stock decrement
Month 2: Add input validation (Joi/Zod schema) for /create endpoint
Month 2: Replace setTimeout email pattern with proper async flow
```

---

## Key Teaching Points from This Example

1. **Multiple landmines often cluster together** — this 50-line file had 5 distinct issues
2. **"Don't ask" comments are gold** — they tell you exactly where to look first
3. **Magic numbers (0.9, 1.0875) decode to real business rules** worth documenting
4. **The safest change wraps old code rather than modifying it directly**
5. **Bundling a security fix with a feature change is justified** when you're already
   touching the dangerous code — but only with proper test coverage
