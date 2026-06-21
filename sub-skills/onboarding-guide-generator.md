# Sub-Skill: Onboarding Guide Generator

## Purpose
Generate a human-readable onboarding document that lets a new developer understand
the codebase in 1 day instead of 3 weeks. Written from code analysis, not assumptions.

---

## The Onboarding Guide Structure

A great onboarding guide answers questions in the order a new developer asks them:

```
Hour 1:  "What does this app do?"
Hour 2:  "How do I get it running?"
Hour 3:  "How is it organized?"
Hour 4:  "How does the main flow work?"
Day 2:   "How do I make my first change safely?"
Week 1:  "What are the gotchas I need to know?"
```

---

## Section 1: What This App Does (5 Minutes to Read)

Written for someone who has never seen this codebase.

```markdown
# [App Name] — Developer Onboarding Guide

## What This Is

[2-3 sentences: What does this app do? Who uses it? Why does it exist?]

Extracted from code analysis:
- [Feature 1 found in code]
- [Feature 2 found in code]
- [Feature 3 found in code]

## The One Sentence

"[App name] is a [type of app] that lets [who] do [what] by [how]."

Example: "OrderFlow is a B2B order management system that lets wholesale
distributors track orders from placement through delivery via a web dashboard
and email notifications."
```

---

## Section 2: Local Setup (Reconstructed from Code)

Extract setup requirements from code analysis:

```markdown
## Getting It Running

### What You Need
[Detected from code and config files:]
- Node.js [version from package.json engines field, or detected from syntax]
- PostgreSQL [detected from database driver]
- Redis [detected from ioredis/redis dependency]
- [Other services detected]

### Environment Variables Required
[Extracted from all process.env. references:]
DATABASE_URL=         # PostgreSQL connection string
REDIS_URL=            # Redis connection (used for sessions + job queue)
JWT_SECRET=           # Must be 32+ characters
STRIPE_SECRET_KEY=    # Payment processing
SENDGRID_API_KEY=     # Email sending
PORT=3000             # HTTP port (defaults to 3000)
NODE_ENV=             # 'development' | 'production' | 'test'

### Start Commands
[From package.json scripts:]
npm install           # Install dependencies
npm run db:migrate    # Run database migrations
npm run db:seed       # Optional: load sample data
npm run dev           # Start development server (hot reload)
npm test              # Run test suite

### Known Setup Issues
[Common issues found by analyzing error handling:]
- [Issue 1]: If you see "[error message]", it means [explanation and fix]
- [Issue 2]: The app expects PostgreSQL 12+ — older versions may have issues
```

---

## Section 3: Codebase Map

```markdown
## How It's Organized

### Directory Structure
[Generated from analysis:]

/
├── routes/          ← HTTP request handlers (where URLs are defined)
│   ├── auth.js      ← Login, logout, password reset
│   ├── orders.js    ← Order CRUD operations
│   └── admin/       ← Admin-only routes (requires admin role)
│
├── lib/             ← Business logic (the important stuff)
│   ├── pricing.js   ← All price calculation logic (tax, discounts)
│   ├── auth.js      ← Authentication/JWT logic
│   └── mailer.js    ← Email sending wrapper
│
├── models/          ← Database access layer
│   ├── User.js      ← User queries and relationships
│   ├── Order.js     ← Order queries and state machine
│   └── Product.js   ← Product catalog queries
│
├── workers/         ← Background jobs (runs independently of HTTP)
│   ├── invoices.js  ← Daily invoice generation
│   └── cleanup.js   ← Old session cleanup
│
├── middleware/      ← Request processing (runs before route handlers)
│   ├── requireAuth.js ← Blocks unauthenticated requests
│   └── validate.js    ← Request validation
│
├── config/          ← Configuration (database, mail, etc.)
├── tests/           ← Test files (mirrors main structure)
└── migrations/      ← Database schema changes (chronological)

### The Golden Rule of This Codebase
[Extracted from code patterns:]
"Routes call lib/ functions. Lib/ functions use models/. Models/ talk to the database.
Never put database queries directly in routes. Never put business logic in models."
[Note: State where this rule is violated if detected]
```

---

## Section 4: The Main Flows

```markdown
## How the Main Things Work

### Flow 1: User Login
1. POST /auth/login with email + password
2. middleware/validate.js checks request format
3. routes/auth.js calls lib/auth.js:authenticate()
4. lib/auth.js queries User model, bcrypt.compare()
5. If valid: generates JWT, sets in cookie + returns in body
6. All subsequent requests: middleware/requireAuth.js verifies JWT

### Flow 2: Creating an Order
1. POST /orders with cart data
2. requireAuth middleware verifies user
3. routes/orders.js calls lib/order-processor.js:create()
4. lib/order-processor.js:
   a. Validates inventory (models/Product.js)
   b. Calculates price (lib/pricing.js)
   c. Creates order record (models/Order.js)
   d. Decrements inventory (models/Product.js)
   e. Sends confirmation email (lib/mailer.js)
   f. Queues invoice generation (workers/invoices.js)
5. Returns order ID and confirmation

### [Flow N]: [Next major flow]
[Continue for all major flows detected]
```

---

## Section 5: Database Overview

```markdown
## The Database

### Tables and What They Store
| Table | What It Is | Key Fields |
|-------|-----------|-----------|
| users | Customer accounts | id, email, role, created_at |
| orders | Purchase orders | id, user_id, status, total |
| order_items | Line items in orders | order_id, product_id, quantity, price |
| products | Product catalog | id, name, sku, stock, price |
| sessions | User login sessions | token, user_id, expires_at |

### Key Relationships
- A user has many orders
- An order has many order_items
- An order_item belongs to one product
- [Other relationships found]

### Important: These Columns Are Everywhere
[Columns that appear in many places — changing them has high blast radius]
- users.role — checked in 8 places
- orders.status — drives the entire order lifecycle
- products.stock — decremented on order, must not go negative
```

---

## Section 6: Things That Will Catch You Out

```markdown
## ⚠️ Things Every Developer Needs to Know

### The Stuff Nobody Told You

**1. Soft Deletes**
Users and products are soft-deleted (deleted_at field), not actually removed.
Always filter: `WHERE deleted_at IS NULL` unless you want deleted records.
Files that forget this: [list any found]

**2. The orders.status Field Is a State Machine**
Valid statuses: pending → processing → shipped → delivered (+ cancelled, refunded)
Not all transitions are valid. Use lib/order-processor.js, not raw SQL updates.
If you update status directly in the DB, email notifications won't send.

**3. Pricing Must Go Through lib/pricing.js**
Tax and discount logic is complex. Never calculate prices inline.
The function has hidden side effects: it logs to audit table and updates user stats.

**4. The Legacy Sync Worker**
workers/legacy-sync.js runs every 5 minutes and does mysterious things.
It was never documented. Don't disable it — something breaks when it's off.
See LANDMINE_REGISTRY.md for details.

**5. The Test Database**
Tests use a separate database. See .env.test for configuration.
Running `npm test` will wipe and rebuild the test DB — don't point it at production.

**6. Email in Development**
Emails are not sent in development (NODE_ENV=development).
They're logged to console. To test actual email delivery, use Mailtrap.
```

---

## Section 7: First Change Guide

```markdown
## Making Your First Change

### Before You Change Anything
1. Read LANDMINE_REGISTRY.md — know what's dangerous
2. Check DEPENDENCY_MAP.md for the file you're changing
3. Run the test suite to establish baseline: `npm test`
4. Create a branch: `git checkout -b your-name/feature-name`

### The Safe Change Checklist
Before committing any change:
- [ ] Ran tests locally and they pass
- [ ] Checked blast radius in DEPENDENCY_MAP.md
- [ ] Didn't modify any CURSED or LANDMINE files without team review
- [ ] Added/updated tests for the change
- [ ] Checked for magic numbers and documented any you added

### Getting Help
- BUSINESS_RULES.md — what the business rules are
- DEPENDENCY_MAP.md — what will break
- LANDMINE_REGISTRY.md — what not to touch
- [Team contact info if available]
```
