# Sub-Skill: Landmine Detector

## Purpose
Find every section of code that is dangerous to touch — from subtle timing bugs
to outright cursed sections that work only by accident. Protect developers from
expensive mistakes in unfamiliar territory.

---

## The Landmine Taxonomy

### Category 1: Timing Landmines

Code that depends on execution order or timing in non-obvious ways.

**Pattern: setTimeout as synchronization mechanism**
```javascript
// LANDMINE: Using setTimeout to "wait" for something
setTimeout(() => {
  processOrder(orderId)  // Assumes DB write from above is complete
}, 500)                  // 500ms is not guaranteed to be enough

// What breaks: On slow DB or high load, 500ms isn't enough
// What the developer was fixing: Race condition between DB write and processing
// Safe approach: Proper async/await or event-based completion signal
```

**Pattern: Order-dependent initialization**
```javascript
// LANDMINE: File A must be required before File B
const config = require('./config')      // Sets global state
const database = require('./database')  // Reads global state from config
// If database.js is ever required first → silent misconfiguration
```

**Pattern: Shared mutable state in async code**
```javascript
// LANDMINE: Shared variable modified by concurrent async operations
let currentBatch = []

async function processItem(item) {
  currentBatch.push(item)               // Multiple concurrent calls = corruption
  if (currentBatch.length >= 10) {
    await processBatch(currentBatch)
    currentBatch = []                    // Race: another push can happen here
  }
}
```

---

### Category 2: Data Integrity Landmines

Code that can corrupt data in non-obvious ways.

**Pattern: Non-atomic operations**
```javascript
// LANDMINE: Two database operations that should be atomic but aren't
async function transferFunds(fromId, toId, amount) {
  await debitAccount(fromId, amount)    // If this succeeds but next fails...
  await creditAccount(toId, amount)     // ...money disappears into void
  // Need: database transaction wrapping both operations
}
```

**Pattern: Soft delete inconsistency**
```javascript
// LANDMINE: Some queries filter deleted_at, others don't
const users = await User.findAll()                           // Returns deleted users!
const activeUsers = await User.findAll({ where: { deleted_at: null }}) // Correct

// The problem: you need to know which queries filter and which don't
// Risk: Showing deleted user data in some views
```

**Pattern: Currency as float**
```javascript
// LANDMINE: Classic financial floating point error
const total = 0.1 + 0.2   // = 0.30000000000000004, not 0.3
const tax = total * 0.0875 // Error compounds

// Every financial calculation in this codebase has potential rounding errors
// if using float instead of integer cents or decimal library
```

---

### Category 3: Security Landmines

```javascript
// LANDMINE: SQL injection in dynamic query
const query = `SELECT * FROM orders WHERE user_id = ${req.params.id}`
// An attacker can set id to: "1 OR 1=1" and get all orders

// LANDMINE: Mass assignment vulnerability
const user = await User.update(req.body)  // Updates ANY field the user sends
// Attacker can send: { role: 'admin' }

// LANDMINE: Unvalidated redirect
res.redirect(req.query.next)  // Open redirect — phishing attack vector
// Attacker can set next to: https://evil.com

// LANDMINE: API key in client-side code
const openAIKey = 'sk-...'  // Exposed to anyone who views page source

// LANDMINE: Eval with user input
eval(req.body.expression)  // Remote code execution
```

---

### Category 4: Performance Landmines

Code that works fine with small data but destroys performance at scale.

**Pattern: N+1 in a loop**
```javascript
// LANDMINE: N+1 query (1 query for list + 1 per item = disaster at scale)
const orders = await Order.findAll()          // 1 query
for (const order of orders) {
  order.user = await User.findById(order.userId)  // N queries!
}
// At 1,000 orders: 1,001 database queries
// At 100,000 orders: server death
```

**Pattern: Unindexed column in WHERE clause**
```javascript
// LANDMINE: Filtering on a column with no database index
await Order.findAll({ where: { status: 'pending', customer_email: email }})
// customer_email has no index → full table scan
// Works fast with 100 rows, unusable with 1,000,000 rows
```

**Pattern: Loading all records into memory**
```javascript
// LANDMINE: Will work until dataset gets large
const allOrders = await Order.findAll()        // Loads everything into RAM
const filtered = allOrders.filter(o => ...)   // Filter in JS, not SQL
// At 1M records: out-of-memory crash
```

---

### Category 5: The "Cursed" Patterns

Code that appears to work but no one understands why.

**Pattern: Silent error swallowing**
```javascript
// LANDMINE: Errors are swallowed silently
try {
  await sendEmail(user)
} catch (e) {
  // ← empty catch block
}
// If email fails, nothing happens. No log. No retry. User never knows.
// This pattern hides failures in production for years.
```

**Pattern: Implicit truthiness in critical path**
```javascript
// LANDMINE: Works because of JS truthiness quirks
if (user.permissions) {          // True if permissions is any non-empty value
  allowAccess()                  // Including permissions = "none" (truthy string!)
}
// A non-technical admin who sets permissions to "none" grants full access
```

**Pattern: The "fix" that created coupling**
```javascript
// LANDMINE: Comment says "don't move this"
// IMPORTANT: This require() must stay at the top of this file.
// Moving it causes the payment module to initialize before the logger.
// - DevName, March 2019
const logger = require('./logger')  // ← This require is load-bearing
```

**Pattern: Working-by-accident timing**
```javascript
// LANDMINE: Only works because database is slow enough
async function createOrderAndNotify(orderData) {
  createOrder(orderData)          // Not awaited! (intentional or bug?)
  await sendNotification()        // Sends before order exists... usually
  // Works in dev (fast notification, slow-ish DB)
  // Fails in prod (fast DB sometimes confirms before notification sends)
}
```

---

## Step: Landmine Registry Format

For each landmine found:

```
LANDMINE REGISTRY ENTRY
═══════════════════════════════════════════════════
ID: LM-042
Type: Data Integrity — Non-atomic operation
Location: lib/payments.js, lines 89-96
Severity: 🔴 LANDMINE
─────────────────────────────────────────────────
DESCRIPTION:
The transferFunds() function debits one account and credits another in
two separate database operations without a transaction. If the credit
operation fails after the debit succeeds, the money is lost.

HOW IT MANIFESTS:
Works perfectly 99.9% of the time. Fails silently during database
connection drops, timeouts, or deadlocks. Very hard to reproduce in testing.

EVIDENCE OF KNOWN PROBLEMS:
Line 94: comment "// TODO: wrap in transaction"  [Added 2020-01-15]
Git blame shows this file modified 12 times in 2020 — likely patching bugs.

HOW TO SAFELY HANDLE:
Option A (safest): Wrap in database transaction:
  await db.transaction(async (t) => {
    await debitAccount(fromId, amount, { transaction: t })
    await creditAccount(toId, amount, { transaction: t })
  })
Option B (avoid): Do not call this function in new code.
  Create transferFundsV2() with proper transaction.

DO NOT: Add more code inside this function until fixed.
═══════════════════════════════════════════════════
```

---

## Landmine Severity Scale

| Severity | Action Required | Touch If... |
|----------|----------------|------------|
| 💀 CURSED | Never touch without full rewrite plan | Production disaster guaranteed |
| 🔴 LANDMINE | Read-only understanding first, full regression test before change | Only if absolutely necessary |
| 🟠 RISKY | Test coverage before change, code review required | With care and tests |
| 🟡 CAUTION | Note the coupling, test change | Normal development practice |

---

## Phase 4 Output: Landmine Registry

```markdown
# Landmine Registry
## ⚠️ READ THIS BEFORE CHANGING ANYTHING

### 💀 CURSED Sections — Do Not Touch
[List with evidence and wrapping strategy]

### 🔴 LANDMINE Sections — Touch Only With Extreme Care
[List with exact blast radius and safe approach]

### 🟠 RISKY Sections — Treat With Caution
[List with specific warnings]

### Safe Zones — Low Risk Areas
[Areas where developers can work freely]
```
