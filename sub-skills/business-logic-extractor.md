# Sub-Skill: Business Logic Extractor

## Purpose
Translate code into plain English business rules that non-technical stakeholders
can verify and developers can trust. Every magic number decoded, every conditional
translated, every side effect documented.

---

## The Translation Imperative

Code is compressed business logic. The original developer translated business rules
into code. This phase reverses that translation.

```
CODE:                              BUSINESS RULE:
─────────────────────────────      ──────────────────────────────────────
if (orders.length > 10 &&          "Premium customers who have placed
    user.type === 2 &&              more than 10 orders and have been
    user.createdAt < 365days)       customers for over a year get a
  applyDiscount(0.15)              15% automatic discount."

if (item.stock < 5)                "When inventory drops below 5 units,
  sendAlert('inventory@co.com')    send an email alert to the inventory
  item.status = 'low'              team and mark the item as low stock."

const TAX_RATE = 0.0875           "Sales tax is 8.75% — likely
                                   California state + local tax rate."
```

---

## Step 1: Magic Number Registry

Scan all code for numeric/string literals that represent business rules.

### Detection Patterns

```javascript
// Magic numbers to decode:
if (score > 750) → "credit score threshold for approval"
price * 1.0875   → "price with 8.75% tax (California?)"
if (age < 18)    → "minor age check (jurisdiction-specific)"
limit = 5000     → "API rate limit? transaction limit? character limit?"
delay = 86400000 → "24 hours in milliseconds — daily job interval"
type === 3       → "user type enum: 3 = ? (check where assigned)"
status = 'P'     → "status code: P = Pending? Published? Processing?"
```

For each magic number/string found, produce:
```
MAGIC VALUE DECODED
─────────────────────────────────────────────
Value: 0.0875
Location: lib/pricing.js:47
Type: Float multiplier
Decoded Business Rule: "Sales tax rate of 8.75% — likely California state + local"
Confidence: HIGH (matches CA state+local tax rate)
Risk if changed: HIGH — affects all pricing calculations
─────────────────────────────────────────────
```

### Common Magic Number Patterns

| Pattern | Likely Meaning |
|---------|---------------|
| `* 1.XX` or `* 0.XX` | Tax rate, discount rate, commission |
| `> 750` or `< 300` | Credit score thresholds |
| `=== 1/2/3/4` on type fields | Unimplemented enum |
| `* 86400` or `* 3600` | Time conversion (days/hours to seconds) |
| `> 50000` or `< 10` | Business threshold (orders, accounts, inventory) |
| `'admin'/'user'/'guest'` | Role system |
| `'pending'/'active'/'cancelled'` | State machine values |
| `== 'US'/'CA'/'EU'` | Geographic region logic |
| `+ 30` (on dates) | 30-day trial / payment terms |
| `* 100` (on money) | Converting dollars to cents (common in payment code) |

---

## Step 2: Conditional Logic Translation

For every significant if/else, switch, or ternary, produce a business rule statement.

### Translation Template

```
CONDITIONAL DECODED
─────────────────────────────────────────────
Location: routes/orders.js:142-167
Code pattern: nested if/else with 4 conditions
─────────────────────────────────────────────
BUSINESS RULE:
"When processing an order:
  1. IF the user's account is suspended → reject with error 'Account suspended'
  2. IF the order total exceeds $10,000 → require manager approval (sets status to 'pending_approval')
  3. IF the shipping address is outside supported regions → reject with 'Shipping unavailable'
  4. IF all checks pass → confirm order and decrement inventory"

STATE MACHINE DETECTED:
  pending → pending_approval → approved → fulfilled
  pending → rejected
  pending → cancelled (user-initiated)

SIDE EFFECTS:
  - Inventory decremented on order confirm
  - Email sent to manager on approval required
  - Audit log entry created on all state changes
─────────────────────────────────────────────
Confidence: HIGH
```

---

## Step 3: Side Effect Documentation

The most dangerous things in legacy code are **hidden side effects** — functions
that do more than their name suggests.

### Side Effect Scanner

For every function, document ALL effects:

| Effect Type | What to Look For |
|-------------|-----------------|
| **Database writes** | INSERT, UPDATE, DELETE, save(), create(), destroy() |
| **File system changes** | writeFile, appendFile, unlink, rename |
| **External API calls** | fetch, axios, http.request, email sending |
| **Cache invalidation** | redis.del, cache.clear, invalidate |
| **Event emission** | emit(), trigger(), publish(), broadcast() |
| **Global state mutation** | Modifying variables outside function scope |
| **Audit/log writing** | Logging that has compliance implications |
| **Queue additions** | Job queue, task queue additions |

**Output format for each function:**

```
FUNCTION: calculateOrderTotal(order, user)
Location: lib/pricing.js:89

DOES MORE THAN IT SAYS:
  Primary:  Calculates order total with tax and discounts
  Hidden 1: Logs pricing calculation to audit table (database write)
  Hidden 2: Updates user's "last_purchase_amount" field (database write)
  Hidden 3: Emits 'pricing_calculated' event (triggers analytics)

DANGER: Calling this function has 3 side effects beyond its name.
```

---

## Step 4: State Machine Reconstruction

Many legacy systems have implicit state machines that were never formally designed.

### Detection Signals

```
status field with string values → implicit state machine
"pending", "active", "cancelled" fields → state transitions
functions that change a status field → transitions
```

### State Machine Reconstruction Template

```
IMPLICIT STATE MACHINE DETECTED
Entity: Order
─────────────────────────────────────────────
STATES FOUND:
  'draft'           → Order created but not submitted
  'pending'         → Submitted, awaiting payment
  'pending_approval'→ Over $10k threshold, needs manager
  'processing'      → Payment received, fulfilling
  'shipped'         → Tracking number assigned
  'delivered'       → Confirmed received (or 3 days after ship)
  'cancelled'       → Cancelled by user or system
  'refunded'        → Refund processed

TRANSITIONS FOUND (from code analysis):
  draft → pending         : submitOrder() in routes/orders.js:45
  pending → processing    : processPayment() in lib/payments.js:12
  pending → pending_approval: processPayment() if total > 10000
  processing → shipped    : fulfillOrder() in lib/fulfillment.js:78
  * → cancelled           : cancelOrder() in routes/orders.js:201
  * → refunded            : processRefund() in lib/payments.js:156

MISSING TRANSITIONS (not implemented but logically needed):
  delivered → refunded    : No path from delivered to refunded found
  shipped → cancelled     : No cancellation after ship found

⚠️ WARNING: Missing transitions are likely business edge cases
that were never implemented. Verify with stakeholders.
─────────────────────────────────────────────
```

---

## Step 5: Permission and Authorization Logic

Extract the permission model from code:

```
AUTHORIZATION MODEL EXTRACTED
─────────────────────────────────────────────
Role system: String-based ('admin', 'user', 'guest')
Location: middleware/auth.js

PERMISSIONS BY ROLE:
  admin:
    ✅ All routes
    ✅ User management
    ✅ Order cancellation after ship
    ✅ Price override

  user:
    ✅ Own orders (CRUD)
    ✅ Own profile
    ❌ Other users' data
    ❌ Bulk operations

  guest:
    ✅ Product catalog (read only)
    ✅ Cart (session-based)
    ❌ Checkout (must register)

AUTHORIZATION GAPS FOUND:
  ⚠️ /api/reports/* — no auth check found (CRITICAL)
  ⚠️ /api/admin/users — checks role but no ownership verification
  ⚠️ Order cancellation — user can cancel any order, not just their own
─────────────────────────────────────────────
```

---

## Phase 2 Output: Business Rules Document

```markdown
# Business Rules Extracted from Code

## [System Name] — Business Logic Reference

*Generated by Legacy Code Whisperer from code analysis*
*Confidence levels noted throughout — LOW confidence items need verification*

---

## Core Business Rules

### BR-001: Pricing Rules
[All pricing logic in plain English]

### BR-002: User Account Rules
[Account creation, verification, suspension rules]

### BR-003: Order Processing Rules
[Order lifecycle with state machine diagram]

### BR-004: Authorization Rules
[Who can do what]

---

## Magic Values Registry
| Value | Location | Business Meaning | Confidence |
|-------|----------|-----------------|-----------|
| 0.0875 | pricing.js:47 | Tax rate 8.75% | HIGH |
| 750 | credit.js:23 | Min credit score | MEDIUM |
...

---

## Hidden Side Effects Warning List
[All functions that do more than their name suggests]

---

## Unimplemented Business Rules (Gaps Found)
[Logical cases the code doesn't handle]
```
