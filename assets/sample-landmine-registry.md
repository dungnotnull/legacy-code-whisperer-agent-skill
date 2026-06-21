# Sample Output: Landmine Registry

This shows what `LANDMINE_REGISTRY.md` looks like after running full analysis
on a typical legacy e-commerce order processing module.

---

# Landmine Registry
## ⚠️ READ THIS BEFORE CHANGING ANYTHING

**Codebase:** ShopFlow Order Service
**Date:** 2025-06-10

> **5 critical danger zones found.**

---

## 🔴 LANDMINES — Touch Only With Extreme Care (3)

### LM-001: SQL Injection via String Concatenation
**File:** `routes/orders.js`:24, 31, 39, 46
**Category:** security
**Problem:** SQL query built via string interpolation — SQL injection vulnerability

```javascript
db.query('SELECT * FROM users WHERE id = ' + userId, function(err, users) {
```

**Safe approach:** Use parameterized queries: `db.query("SELECT * WHERE id = ?", [id])`

---

### LM-002: Empty Catch Block — Silent Error Swallowing
**File:** `routes/orders.js`:35
**Category:** reliability
**Problem:** Errors caught and silently discarded — hides failures in production

```javascript
try {
  for (var i = 0; i < items.length; i++) {
    db.query('UPDATE products SET stock = stock - ' + items[i].qty...
```

**Safe approach:** At minimum: `console.error(e)` or `logger.error(e)`. Better: proper error handling with transaction rollback.

---

### LM-003: Non-Atomic Multi-Step Database Operation
**File:** `routes/orders.js`:28-36
**Category:** data
**Problem:** Multiple database operations without transaction — data corruption risk if one fails

**Safe approach:** Wrap order creation and stock decrement in a database transaction to ensure atomicity.

---

## 🟠 RISKY Sections — Treat With Caution (2)

### RISKY-001: setTimeout used as synchronization
**File:** `routes/orders.js`:38 — setTimeout used to wait for async operation, unreliable under load

### RISKY-002: findAll without limit
**File:** `routes/admin/reports.js`:67 — Fetching all records without LIMIT, works for small datasets, crashes large ones

---

## Safe Zones (Free to Change)

✅ `utils/string-helpers.js` — 2 dependents, pure functions, has tests
✅ `templates/email-templates/*.html` — read by mailer.js only, no business logic
✅ `scripts/seed-data.js` — not imported anywhere, dev-only

---

## Additional Landmines Found by AI Analysis

🔴 **Negative Stock Possible** — `routes/orders.js`:32
Stock decremented without checking sufficient quantity exists. Can oversell inventory.
Comment evidence: developer left `// don't ask` immediately above this code, suggesting
known but unaddressed issues.

🟡 **"VIP" User Type Undocumented** — `lib/pricing.js`:8
`if (usr.type == 2)` — no enum or constant exists anywhere in codebase defining what
user types mean. This tribal knowledge has been lost. Verify with team before any
changes to user type logic.
