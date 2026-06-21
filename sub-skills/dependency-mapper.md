# Sub-Skill: Dependency Mapper

## Purpose
Map every coupling in the codebase so developers know exactly what breaks
when they touch anything. Build the blast radius map for every module.

---

## The Blast Radius Concept

```
BLAST RADIUS = Everything that could break if X is changed

Changing a database column:
  → All queries that SELECT that column        (direct)
  → All functions that use those query results (indirect)
  → All API endpoints that return that data    (downstream)
  → All clients that expect that field         (external)

Changing a utility function:
  → Every file that imports it                 (direct)
  → Every test that tests it                   (test)
  → Every function that depends on its output  (indirect)
```

---

## Step 1: Import/Dependency Graph

Build the complete import dependency tree.

### Dependency Analysis Template

For each file/module:

```
FILE: lib/pricing.js
─────────────────────────────────────────────
IMPORTS (depends on):
  utils/math.js        — rounding functions
  config/tax-rates.js  — tax configuration
  models/Product.js    — product data access
  lib/discounts.js     — discount calculation

IMPORTED BY (depended on by):
  routes/orders.js     — order total calculation
  routes/cart.js       — cart total display
  api/checkout.js      — checkout price confirmation
  workers/invoice.js   — invoice generation
  tests/pricing.test.js

BLAST RADIUS if lib/pricing.js changes:
  DIRECT:   3 routes, 1 worker, 1 test file
  INDIRECT: Everything downstream of those routes
  EXTERNAL: Any client displaying prices
─────────────────────────────────────────────
DANGER LEVEL: 🔴 HIGH — touches every money calculation
```

---

## Step 2: Database Dependency Mapping

### Column-Level Blast Radius

For every database table/column, map all code that touches it:

```
TABLE: orders
COLUMN: status
─────────────────────────────────────────────
READS:
  routes/orders.js:45     — GET /orders filtering
  routes/orders.js:201    — order detail view
  middleware/auth.js:78   — permission check
  workers/daily-report.js — reporting aggregation
  api/admin/orders.js:12  — admin dashboard

WRITES:
  lib/order-processor.js:34  — status transitions
  routes/orders.js:156       — manual status update
  workers/payment.js:89      — payment confirmation
  ⚠️ ALSO: lib/legacy-sync.js:445 — HIDDEN WRITE, unknown trigger

BLAST RADIUS of changing orders.status:
  5 read locations
  4 write locations (including 1 hidden)
  All order list APIs
  Admin dashboard
  Daily reports
─────────────────────────────────────────────
⚠️ WARNING: Hidden write found in legacy-sync.js
   This file appears to update status independently.
   Full behavior unknown without runtime testing.
```

### Circular Dependency Detection

Circular dependencies are common in legacy code and cause unpredictable behavior:

```
CIRCULAR DEPENDENCY DETECTED
─────────────────────────────────────────────
Chain: userService.js → orderService.js → userService.js

Impact:
  - Module initialization order is unpredictable
  - May cause "undefined" errors on startup
  - One service cannot be tested independently

Recommended fix: Extract shared logic to a third module that
both services import. Break the cycle.
─────────────────────────────────────────────
```

---

## Step 3: Hidden Coupling Detection

Hidden coupling = things that depend on each other without explicit imports.

### Coupling Types

**Global Variable Coupling:**
```javascript
// File A sets global:
global.currentUser = await getUser(req)

// File B reads global (no import!):
if (global.currentUser.role === 'admin') { ... }
```
Detection: Scan for `global.`, `window.`, bare variable names set in one file and read in another.

**Shared Database State Coupling:**
```javascript
// Job 1 writes:
await db.query('UPDATE settings SET value = ? WHERE key = "processing"', [true])

// Job 2 reads (completely separate file):
const isProcessing = await db.query('SELECT value FROM settings WHERE key = "processing"')
```
Detection: Same table/column written in one place, read in unrelated code path.

**Event Bus Coupling:**
```javascript
// Publisher (lib/orders.js):
eventBus.emit('order:created', orderData)

// Subscriber (unknown location):
eventBus.on('order:created', sendConfirmationEmail)
```
Detection: Scan for `.emit()`, `.trigger()`, `.publish()` — then find ALL `.on()`, `.subscribe()` listeners.

**Environment Variable Coupling:**
```javascript
// Used in 12 different files without validation:
const DB_URL = process.env.DATABASE_URL
```
Detection: Same env var read in multiple files without centralized validation.

---

## Step 4: Blast Radius Visualization

### Text-Based Dependency Map

```
BLAST RADIUS MAP: Changing lib/auth.js
═══════════════════════════════════════

lib/auth.js
├── DIRECTLY USED BY:
│   ├── 🔴 middleware/requireAuth.js [CRITICAL PATH]
│   │   └── ALL protected routes depend on this
│   ├── 🟠 routes/login.js
│   ├── 🟠 routes/register.js
│   └── 🟡 tests/auth.test.js
│
├── INDIRECT DEPENDENTS (through middleware/requireAuth.js):
│   ├── routes/orders.js (all order endpoints)
│   ├── routes/users.js (all user endpoints)
│   ├── routes/admin/*.js (all admin routes)
│   └── api/webhooks.js
│
└── EXTERNAL IMPACT:
    └── Any client that calls protected endpoints

TOTAL BLAST RADIUS:
  Direct:    4 files
  Indirect:  12+ files
  External:  All authenticated API clients

RECOMMENDED APPROACH:
  1. Add tests for current behavior BEFORE changing
  2. Run full regression test suite after any change
  3. Consider: can you add behavior without changing existing?
```

---

## Step 5: Safe Dependency Zones

Identify code with LOW blast radius — safe to change freely:

```
SAFE ZONES (Low Blast Radius)
─────────────────────────────────────────────
✅ utils/string-helpers.js
   Imported by: 2 files
   No database access
   Pure functions only
   Has tests
   → SAFE TO CHANGE

✅ scripts/seed-data.js
   Not imported by anything
   Dev-only script
   → SAFE TO CHANGE

✅ templates/email-templates/*.html
   Read by: mailer.js only
   No business logic
   → SAFE TO CHANGE

⚠️ Not safe:
  lib/auth.js        — 16 dependents
  models/User.js     — 23 dependents
  config/database.js — App won't start without it
─────────────────────────────────────────────
```

---

## Phase 3 Output: Dependency Map Document

```markdown
# Dependency Map

## Blast Radius Registry

### Critical Files (highest blast radius)
| File | Direct Dependents | Indirect Dependents | Danger Level |
|------|------------------|--------------------|-|
| lib/auth.js | 4 | 12+ | 🔴 |
| models/User.js | 8 | 20+ | 🔴 |
| config/database.js | 15 | ALL | 💀 |

### Safe Files (low blast radius)
[Files safe to change freely]

### Circular Dependencies
[All circular dependency chains]

### Hidden Couplings
[All non-import dependencies found]

## Change Impact Analysis
For each file a developer might want to change:
[Specific blast radius and recommended approach]
```
