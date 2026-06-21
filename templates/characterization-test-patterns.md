# Templates: Characterization Test Patterns

Ready-to-use templates for adding a safety net to legacy code BEFORE changing it.
Characterization tests document what code ACTUALLY does (not what it should do).

---

## Template 1: Basic Characterization Test (JavaScript/Jest)

```javascript
// characterization.test.js
// These tests document CURRENT behavior, even if it seems wrong.
// DO NOT "fix" the expected values to what you think they should be —
// these tests exist to catch unintended changes during refactoring.

const { calcTotal } = require('../orders')

describe('calcTotal - CHARACTERIZATION (documents existing behavior)', () => {
  test('regular user, single item', () => {
    const items = [{ price: 100, qty: 1 }]
    const user = { type: 1 }
    const result = calcTotal(items, user)
    // Document whatever it currently outputs:
    expect(result).toBe(108.75)  // 100 * 1.0875 (no discount)
  })

  test('VIP user (type 2), single item', () => {
    const items = [{ price: 100, qty: 1 }]
    const user = { type: 2 }
    const result = calcTotal(items, user)
    expect(result).toBeCloseTo(97.875)  // 100 * 0.9 * 1.0875
  })

  test('empty items array', () => {
    const result = calcTotal([], { type: 1 })
    expect(result).toBe(0)  // Document: does it crash or return 0?
  })

  test('user with no type field', () => {
    const items = [{ price: 100, qty: 1 }]
    const user = {}  // type is undefined
    const result = calcTotal(items, user)
    // Document actual behavior — does undefined === 2? (No, so no discount)
    expect(result).toBe(108.75)
  })

  test('negative quantity (edge case — should this even be possible?)', () => {
    const items = [{ price: 100, qty: -1 }]
    const result = calcTotal(items, { type: 1 })
    // Document: does it produce negative total? This reveals a missing validation.
    expect(result).toBeCloseTo(-108.75)
    // 🚩 FLAG: This reveals the function doesn't validate quantity > 0
  })
})
```

---

## Template 2: Characterization Test (Python/pytest)

```python
# test_characterization.py
"""
Characterization tests for legacy pricing module.
These document ACTUAL behavior — not intended behavior.
Use before refactoring to catch unintended changes.
"""
import pytest
from legacy.pricing import calculate_total

class TestCalculateTotalCharacterization:
    """Documents current behavior of calculate_total(), bugs and all."""

    def test_standard_calculation(self):
        items = [{'price': 100, 'qty': 1}]
        user = {'type': 1}
        result = calculate_total(items, user)
        assert result == pytest.approx(108.75)

    def test_vip_discount(self):
        items = [{'price': 100, 'qty': 1}]
        user = {'type': 2}
        result = calculate_total(items, user)
        assert result == pytest.approx(97.875)

    def test_empty_cart(self):
        result = calculate_total([], {'type': 1})
        assert result == 0

    def test_missing_user_type_defaults_to_no_discount(self):
        items = [{'price': 100, 'qty': 1}]
        result = calculate_total(items, {})
        assert result == pytest.approx(108.75)

    @pytest.mark.xfail(reason="Known bug: negative quantity not validated")
    def test_negative_quantity_should_be_rejected(self):
        """This SHOULD raise an error but currently doesn't."""
        items = [{'price': 100, 'qty': -1}]
        with pytest.raises(ValueError):
            calculate_total(items, {'type': 1})
```

---

## Template 3: API Endpoint Characterization (Integration Test)

```javascript
// orders.integration.test.js
const request = require('supertest')
const app = require('../app')

describe('POST /orders/create - CHARACTERIZATION', () => {
  test('creates order and returns expected shape', async () => {
    const response = await request(app)
      .post('/orders/create')
      .send({
        userId: 1,
        items: [{ id: 1, price: 50, qty: 2 }]
      })

    expect(response.status).toBe(200)
    expect(response.body).toHaveProperty('orderId')
    expect(response.body).toHaveProperty('total')
    // Document exact total calculation:
    expect(response.body.total).toBe(108.75)
  })

  test('SQL injection vulnerability exists (DOCUMENTING NOT CONDONING)', async () => {
    // This test documents a KNOWN VULNERABILITY for tracking purposes.
    // It should be used to verify the fix works, then UPDATED (not deleted)
    // to confirm injection no longer succeeds.
    const maliciousId = "1 OR 1=1"
    const response = await request(app)
      .get(`/orders/list?userId=${maliciousId}`)

    // 🚩 CURRENT BEHAVIOR: This returns ALL orders, not just user 1's
    // After fix: should return empty array or 400 error
    expect(response.body.length).toBeGreaterThan(1)  // Documents the vulnerability
  })

  test('missing items array - current crash behavior', async () => {
    const response = await request(app)
      .post('/orders/create')
      .send({ userId: 1 })  // No items field

    // Document: does this crash with 500, or handle gracefully?
    expect(response.status).toBe(500)  // Currently crashes — known issue
  })
})
```

---

## Template 4: Snapshot Testing for Complex Output

When the function output is complex (objects, arrays, HTML), snapshot testing
captures the full current behavior without manually writing every assertion.

```javascript
// Useful for legacy functions with complex return objects
test('generateInvoiceData - snapshot of current behavior', () => {
  const order = { id: 1, items: [...], user: {...} }
  const result = generateInvoiceData(order)

  expect(result).toMatchSnapshot()
  // First run: creates __snapshots__/file.test.js.snap
  // Subsequent runs: fails if output changes
  // Review snapshot diffs carefully — some changes are intentional improvements,
  // others are regressions
})
```

---

## Template 5: Database State Characterization

For functions with side effects, test the database state before/after:

```javascript
describe('createOrder - side effect characterization', () => {
  test('decrements product stock', async () => {
    // Setup: known starting state
    await db.query('UPDATE products SET stock = 10 WHERE id = 1')

    await createOrder({ userId: 1, items: [{ id: 1, qty: 3 }] })

    const [product] = await db.query('SELECT stock FROM products WHERE id = 1')
    expect(product.stock).toBe(7)  // Documents: stock decremented correctly
  })

  test('CURRENT BUG: allows negative stock', async () => {
    await db.query('UPDATE products SET stock = 2 WHERE id = 1')

    await createOrder({ userId: 1, items: [{ id: 1, qty: 10 }] })

    const [product] = await db.query('SELECT stock FROM products WHERE id = 1')
    // 🚩 Documents the bug: this SHOULD fail/reject but currently doesn't
    expect(product.stock).toBe(-8)
  })

  test('stock update failure does not roll back order (KNOWN ISSUE)', async () => {
    // This test documents the empty catch block issue (LM-002)
    // Simulate a stock update failure scenario
    // ... (requires mocking db to throw on specific query)
    // Expected current behavior: order succeeds even if stock update fails
  })
})
```

---

## Template 6: Behavior Documentation Header

For any file you're about to refactor, add this header documenting current behavior:

```javascript
/**
 * ============================================================
 * LEGACY CODE — BEHAVIOR DOCUMENTATION
 * ============================================================
 * Documented by: Legacy Code Whisperer analysis
 * Date: [date]
 *
 * KNOWN BEHAVIOR (verified by characterization tests):
 * - calcTotal() applies 10% discount for user.type === 2
 * - calcTotal() applies 8.75% tax to all orders after discount
 * - calcTotal() does NOT validate negative quantities (BUG)
 * - calcTotal() returns 0 for empty items array
 *
 * KNOWN ISSUES (see LANDMINE_REGISTRY.md):
 * - LM-001: SQL injection in user ID query
 * - LM-002: Silent failure on stock update (empty catch)
 * - LM-003: Stock can go negative (no validation)
 *
 * DO NOT CHANGE BEHAVIOR WITHOUT:
 * 1. Updating characterization tests first
 * 2. Confirming with business stakeholders if behavior change is intentional
 * 3. Documenting the change in this header
 * ============================================================
 */
```

---

## When to Use Each Template

| Scenario | Template |
|----------|----------|
| Single pure function, clear inputs/outputs | Template 1/2 (Basic) |
| API endpoint with side effects | Template 3 (Integration) |
| Complex object/HTML output | Template 4 (Snapshot) |
| Function modifies database | Template 5 (Database state) |
| About to refactor a whole file | Template 6 (Header) + all applicable above |

## The Golden Rule of Characterization Tests

> Test what IS, not what SHOULD BE.
>
> If the code has a bug, your characterization test documents the bug exists.
> This is intentional — it lets you safely refactor without accidentally
> "fixing" the bug as a side effect of unrelated changes (which could break
> other code that has come to depend on the buggy behavior).
>
> Once you've decided to FIX the bug (a deliberate, tracked decision),
> update the test to reflect the new correct behavior.
