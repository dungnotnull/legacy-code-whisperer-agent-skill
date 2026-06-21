# Legacy Code Safety Checklists

Use the checklist matching your scenario.

---

## Checklist A: Joining a New Legacy Codebase

### Day 1
- [ ] Run full codebase analysis (Phase 1-7)
- [ ] Read CODEBASE_INTEL.md completely
- [ ] Read LANDMINE_REGISTRY.md completely — memorize the 💀 and 🔴 items
- [ ] Get the app running locally (follow ONBOARDING_GUIDE.md)
- [ ] Run the test suite — note pass/fail baseline

### Week 1
- [ ] Read BUSINESS_RULES.md — understand the domain
- [ ] Read DEPENDENCY_MAP.md — understand the architecture
- [ ] Trace through 2-3 main user flows manually in the code
- [ ] Identify which team members know which parts of the system
- [ ] Make your first change using the Type A (Pure Addition) pattern only

### Month 1
- [ ] Make your first Type C (Behavioral Modification) change
- [ ] Use CHANGE_PLAN.md template for any non-trivial change
- [ ] Contribute one fix to LANDMINE_REGISTRY.md (something you discovered)
- [ ] Add at least 3 characterization tests to a file you touched

---

## Checklist B: Before Any Change to Unfamiliar Code

- [ ] Run `pre_change_gate.py --file [target] --change-type [A-E]`
- [ ] If blocked: read the specific LANDMINE_REGISTRY.md entry
- [ ] If high blast radius: read DEPENDENCY_MAP.md for that file
- [ ] Confirm tests exist OR write characterization tests first
- [ ] Create a feature branch (never work directly on main)
- [ ] Note the rollback procedure BEFORE starting
- [ ] For database changes: confirm backup is recent

---

## Checklist C: Investigating "Why Does This Code Do That?"

- [ ] Check for comments (even outdated ones — they hint at history)
- [ ] Check git blame / git log for the specific lines
- [ ] Search codebase for all callers of the function
- [ ] Check if magic numbers match patterns in legacy-pattern-decoder.md
- [ ] Check test files for this function — test names often reveal intent
- [ ] Search commit messages for related keywords
- [ ] Check if there's a corresponding ticket/issue number in comments
- [ ] If truly unknown: write a characterization test to document
      actual behavior before forming theories about intended behavior

---

## Checklist D: Fixing a Bug in Legacy Code

- [ ] Reproduce the bug with a failing test FIRST
- [ ] Check LANDMINE_REGISTRY.md — is this area already flagged?
- [ ] Check if the same bug pattern exists elsewhere (copy-paste family check)
- [ ] Check DEPENDENCY_MAP.md — who else calls this code?
- [ ] Make the SMALLEST possible fix that makes the test pass
- [ ] Resist the urge to "clean up while you're in there" (separate PR)
- [ ] Verify the fix doesn't break any existing tests
- [ ] Document the bug and fix in commit message with context

---

## Checklist E: Adding a New Feature to Legacy Code

- [ ] Identify the Strangler Fig insertion point (new code, not modified old code)
- [ ] Check if similar features exist already (avoid copy-paste family pattern)
- [ ] Use CHANGE_PLAN.md template
- [ ] Write the new code in a NEW file/function where possible
- [ ] Only touch existing code at the minimal "switch" point
- [ ] Add tests for the new feature
- [ ] Verify existing tests still pass
- [ ] Update ONBOARDING_GUIDE.md if this changes a main flow

---

## Checklist F: Planning a Refactor

- [ ] Run REFACTOR_ROADMAP.md priority scoring
- [ ] Confirm test coverage exists for target module (write characterization
      tests if not)
- [ ] Map dependency order — refactor leaves before trunks
- [ ] Plan the Strangler Fig extraction (new module alongside old)
- [ ] Define rollback strategy for each extraction step
- [ ] Get team sign-off if blast radius > 10 files
- [ ] Schedule in small increments — never "the big refactor sprint"
- [ ] Define success criteria before starting

---

## Checklist G: Production Incident in Unfamiliar Code

- [ ] DON'T start making changes immediately — understand first
- [ ] Check LANDMINE_REGISTRY.md for the affected area
- [ ] Check recent deploys/commits to the affected files
- [ ] Check logs for the actual error (not assumptions)
- [ ] Identify: is this a known landmine manifesting, or something new?
- [ ] If known landmine: apply the documented fix from LANDMINE_REGISTRY.md
- [ ] If new: make the SMALLEST possible mitigation, full fix later
- [ ] After resolution: add this to LANDMINE_REGISTRY.md for next time
- [ ] After resolution: write a post-mortem with root cause

---

## Checklist H: Database Schema Change in Legacy System

- [ ] Confirm recent backup exists and is restorable
- [ ] Check DEPENDENCY_MAP.md for all code touching this table/column
- [ ] Write the DOWN migration before writing the UP migration
- [ ] Use the 3-deploy strategy for renames (never single-step rename)
- [ ] Use nullable/default-value columns for additions (never NOT NULL immediately)
- [ ] Never drop a column until confirmed zero references in code AND zero
      reads in production logs for 1+ week
- [ ] Test migration UP then DOWN then UP again — confirm no data loss
- [ ] Deploy migration separately from and BEFORE the code that depends on it

---

## Universal Red Flags — Stop and Get Help If You See:

- 🚨 A change that touches a file marked 💀 CURSED
- 🚨 A change with blast radius > 20 files
- 🚨 Any database migration involving financial/payment data without team review
- 🚨 Pressure to skip the safety checklist due to time pressure
      (this is exactly when mistakes happen)
- 🚨 You don't understand WHY the current code works the way it does
      (write a characterization test before changing anything)
- 🚨 The "fix" requires changing 5+ files simultaneously
      (this usually means you're fighting the architecture — pause and reconsider approach)
