# Reference: Legacy Pattern Decoder Dictionary

A lookup reference for translating common legacy code patterns into plain
English meaning. Used during Phase 1 (Archaeology) and Phase 2 (Business Logic Extraction).

---

## Part 1: Naming Convention Archaeology

### Suffix/Prefix Decoder

| Pattern | Likely Meaning | Era Signal |
|---------|----------------|-----------|
| `functionName2`, `functionNameNew` | Replacement that never got cleaned up | Any era |
| `functionName_OLD`, `functionNameDeprecated` | Marked for removal, check if still called | Any era |
| `functionName_FINAL` | Developer thought this was the last version (rarely true) | Any era |
| `functionName_v2`, `_v3` | Versioned without proper deprecation strategy | Any era |
| `tmpFunction`, `tempFix` | Meant to be temporary, became permanent | Any era |
| `doStuff`, `handleThing`, `processData` | Generic name = unclear responsibility, grew organically | Any era |
| `XxxHelper`, `XxxUtil` | Catch-all for code that didn't fit elsewhere | Any era |
| `XxxManager`, `XxxService` | Often god-object pattern in older code | 2010-2018 |
| `XxxController` | MVC-pattern, often has too much logic (fat controller) | 2008-2016 |
| `legacy_xxx`, `old_xxx` | Explicitly marked legacy — verify still in use | Any era |
| `xxx2`, `xxx_copy` | Copy-paste that diverged from original | Any era |

### Variable Naming Archaeology

| Pattern | Likely Meaning |
|---------|----------------|
| `flag`, `flag2`, `tempFlag` | Boolean state with unclear purpose — read all usages |
| `data`, `result`, `temp`, `obj` | Generic naming = quick fix that stayed |
| `x`, `y`, `i`, `j` outside loops | Either math-heavy code or very old/rushed code |
| `_private`, `__private` | Convention signaling "don't touch from outside" |
| `isFoo`, `hasFoo`, `canFoo` | Boolean — check name matches actual logic (often drifts) |
| `fooCount`, `numFoo` | Counter — check for off-by-one risk |
| `fooList`, `fooArr`, `foos` | Array — check for null/empty handling |

---

## Part 2: Common Legacy Code Smells and Their Origin Story

### The "God File"
**What it looks like:** One file, 1000+ lines, does everything related to a domain.
**How it happened:** Started small, every new feature got added to "the file that already
handles users" instead of creating new files. No one stopped to refactor.
**Risk:** Extremely high blast radius. Touching anything risks breaking everything.

### The "Mystery Constant"
**What it looks like:** `if (x > 47)` with no explanation.
**How it happened:** A business stakeholder said "make it 47" in a meeting. The developer
implemented it. Nobody wrote down why 47. The original context is lost forever.
**Risk:** Changing it might violate a business rule no one remembers. Don't change
without checking with business stakeholders, even if it seems arbitrary.

### The "Copy-Paste Family"
**What it looks like:** 3-5 functions that are 90% identical with small variations.
**How it happened:** Developer needed something similar to existing function, copy-pasted
instead of abstracting (often correctly, under time pressure), then both versions evolved
independently with bug fixes applied inconsistently.
**Risk:** Bug fixes applied to one copy but not others. Check ALL copies when fixing a bug
in one — the same bug likely exists in siblings.

### The "Half-Finished Migration"
**What it looks like:** Some code uses Pattern A, some uses Pattern B, doing the same thing.
**How it happened:** A migration/refactor was started (e.g., callbacks → promises, REST →
GraphQL, Moment.js → date-fns) but never finished. Common when developer left mid-project.
**Risk:** New code might use either pattern inconsistently. Check which is "current" before
adding new code.

### The "Defensive Programming Graveyard"
**What it looks like:** Excessive null checks, try/catch everywhere, redundant validation.
**How it happened:** Production incidents taught the team to be defensive. Each incident
added another check. The checks accumulated without anyone removing outdated ones.
**Risk:** Some checks may be protecting against conditions that can no longer occur
(upstream validation added later). Risky to remove without understanding history.

### The "Configuration Sprawl"
**What it looks like:** Config values scattered across .env, config.js, database settings
table, and hardcoded fallbacks — for the same setting.
**How it happened:** Configuration strategy changed over time without consolidating old approaches.
**Risk:** Changing a setting in one place might not actually change behavior if another
location takes precedence. Map ALL sources of a config value before changing it.

### The "Silent Fallback"
**What it looks like:** `const value = config.setting || 'default'`
**How it happened:** Developer wanted to prevent crashes from missing config.
**Risk:** Masks configuration errors. If `config.setting` should always exist but doesn't,
this silently uses a default instead of alerting anyone to the misconfiguration.

### The "Globally-Scoped Quick Fix"
**What it looks like:** `global.someState = value` or module-level mutable variable.
**How it happened:** Needed to share state between two distant parts of the code quickly,
didn't have time to properly thread it through function parameters.
**Risk:** Creates invisible coupling. Two unrelated-looking files are actually connected.
Always check for global reads/writes before changing either side.

### The "Comment That Lied"
**What it looks like:** A comment describing behavior that the code no longer matches.
**How it happened:** Code was changed, comment wasn't updated.
**Risk:** Trusting outdated comments leads to wrong assumptions. ALWAYS verify comments
against actual code behavior — never trust comments blindly.

---

## Part 3: Framework-Specific Legacy Patterns

### jQuery Era (2010-2018)
```javascript
$(document).ready(function() {
  $('.button').click(function() {
    $.ajax({
      url: '/api/data',
      success: function(data) { ... }
    })
  })
})
```
**Decode:** DOM-coupled event handling. Business logic mixed with DOM manipulation.
**Risk:** Hard to test (requires DOM). Hard to reuse logic outside the click handler.
**Migration path:** Extract the AJAX call and success handler into a separate function
that doesn't depend on DOM, then call it from the click handler.

### Callback Hell Era (Pre-2015 Node.js)
```javascript
getUser(id, function(err, user) {
  if (err) return callback(err)
  getOrders(user.id, function(err, orders) {
    if (err) return callback(err)
    calculateTotal(orders, function(err, total) {
      callback(null, total)
    })
  })
})
```
**Decode:** Sequential async operations before Promises were standard.
**Risk:** Error handling is repetitive and easy to miss a case. Hard to add new steps.
**Migration path:** Wrap in promisify, convert to async/await, but verify error handling
behavior is preserved exactly (each `if (err)` was doing something specific).

### Early Angular.js Era (2012-2018, AngularJS not Angular 2+)
```javascript
$scope.users = []
$http.get('/api/users').then(function(response) {
  $scope.users = response.data
  $scope.$apply()
})
```
**Decode:** Two-way binding with manual digest cycle triggers.
**Risk:** `$scope` pollution — hard to track what affects what. Digest cycle issues.
**Migration path:** This typically requires a full framework migration, not incremental fix.

### Class Components Era (React 2016-2019, before Hooks)
```javascript
class UserList extends React.Component {
  componentDidMount() {
    this.fetchUsers()
  }
  componentDidUpdate(prevProps) {
    if (prevProps.filter !== this.props.filter) {
      this.fetchUsers()
    }
  }
}
```
**Decode:** Lifecycle methods doing similar things in multiple places (DRY violation
built into the pattern itself).
**Risk:** Easy to forget to handle a lifecycle case. Logic split across multiple methods.
**Migration path:** Convert to functional component with useEffect — but carefully
verify all the lifecycle method logic is captured in dependency arrays correctly.

### Old PHP Era (Pre-2012, no framework or early frameworks)
```php
<?php
mysql_connect("localhost", "user", "pass");
mysql_select_db("mydb");
$result = mysql_query("SELECT * FROM users WHERE id = " . $_GET['id']);
```
**Decode:** Direct MySQL extension (removed from PHP 7+), no input sanitization.
**Risk:** SQL injection (CRITICAL), deprecated/removed functions won't run on modern PHP.
**Migration path:** Must migrate to PDO or mysqli with prepared statements. This is
not optional — mysql_* functions don't exist in PHP 7+.

---

## Part 4: Database Pattern Archaeology

### The "Status as String" Pattern
```sql
status VARCHAR(20)  -- values found in code: 'pending','active','done','cancel','cancelled'
```
**Decode:** Implicit enum, never formalized. Note: 'cancel' vs 'cancelled' inconsistency
suggests two different developers implemented similar features differently.
**Risk:** Typos create new "valid" statuses silently (e.g., 'pendnig'). No DB-level validation.

### The "Soft Delete Drift" Pattern
```sql
-- Some tables have deleted_at, others have is_deleted, others have status='deleted'
```
**Decode:** Soft delete strategy was never standardized across the team/time periods.
**Risk:** A query that filters `deleted_at IS NULL` won't catch rows where the OTHER
soft-delete pattern was used. Easy to accidentally show deleted data.

### The "Audit Trail Gap" Pattern
```sql
-- created_at exists, but updated_at was added later (NULL for old rows)
```
**Decode:** Schema evolved over time. Early rows lack fields added later.
**Risk:** Code assuming `updated_at` is never NULL will break on old data.

### The "Orphaned Foreign Key" Pattern
```sql
-- orders.customer_id references customers.id, but no FK constraint exists
```
**Decode:** Relationship is enforced only in application code, not database.
**Risk:** Data integrity depends entirely on application code being correct 100% of
the time. Orphaned records are likely to exist somewhere in production data.

---

## Part 5: Quick Reference — "What Does This Comment Mean?"

| Comment Found | Likely Real Meaning |
|---------------|---------------------|
| `// don't ask` | Developer knew it was bad but had no time to explain or fix |
| `// magic` | Developer doesn't fully understand why this works either |
| `// I'm sorry` | Developer knew this was a hack, apologizing to future readers |
| `// fixes prod issue` | Patches a specific incident — removing may reintroduce it |
| `// client requested` | Business requirement, not a coding choice — verify before removing |
| `// temporary` (with old date) | Permanent — "temporary" code often outlives "permanent" code |
| `// works on my machine` | Possible environment-specific bug never properly diagnosed |
| `// see ticket #1234` | Context exists but ticket system may no longer be accessible |
| (no comment at all on complex logic) | Either obvious to the original author or rushed — verify behavior carefully |
