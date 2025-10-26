# Definition of Done

## Checklist

A deliverable is **done** when ALL of these criteria are met:

### 1. ✅ Requirements Satisfied
- [ ] Every acceptance criterion in SPEC is met
- [ ] Core functionality works as specified
- [ ] Edge cases handled appropriately

### 2. ✅ Runs Without Errors
- [ ] Application executes successfully
- [ ] No crashes on valid input
- [ ] Errors are caught and handled gracefully

### 3. ✅ Error Handling Works
- [ ] Invalid input shows clear error messages
- [ ] Edge cases don't crash the application
- [ ] Error messages suggest how to fix the problem

### 4. ✅ Core Tests Pass
- [ ] Main functionality has tests
- [ ] Tests pass consistently
- [ ] Edge cases are tested

### 5. ✅ Code Quality
- [ ] Code is readable (clear names, simple logic)
- [ ] No obvious bugs or issues
- [ ] Follows reasonable structure

### 6. ✅ Documentation Exists
- [ ] README explains how to use the application
- [ ] Installation/setup instructions provided
- [ ] Basic usage examples included

### 7. ✅ No Security Issues
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] Input validation present
- [ ] No obvious security vulnerabilities

### 8. ✅ Integration Works
- [ ] Components work together
- [ ] Frontend connects to backend correctly
- [ ] Data flows as expected

## Review Process

**Reviewer checks each item systematically:**

1. Read SPEC acceptance criteria
2. Verify each criterion is satisfied
3. Try to break the application
4. Check for error handling
5. Review tests
6. Scan code for quality issues
7. Verify documentation

## Approval Criteria

**Approve (include "APPROVED") when:**
- All critical items (1-4) are satisfied
- Remaining items (5-8) are reasonably addressed
- Application meets user need

**Request changes when:**
- Any critical item is missing
- Application doesn't work correctly
- Core functionality is incomplete

## Scope Guidelines

**Must Have (Required for Approval):**
- Core P0 functionality works
- Main acceptance criteria met
- Application runs without crashing
- Basic error handling present

**Nice to Have (Not Blocking):**
- Perfect code style
- 100% test coverage
- Extensive documentation
- Performance optimization

## Near Turn Limit

**When approaching MAX_TURNS:**
- Focus on P0 acceptance criteria only
- Approve if core functionality works
- Document P1/P2 items as follow-up
- Don't hold up delivery for polish

## Common Issues

**Issue: Acceptance criteria ambiguous**
→ Ask PM for clarification before approving

**Issue: Tests fail**
→ Do not approve until tests pass

**Issue: Missing core functionality**
→ Request specific implementation

**Issue: No error handling**
→ Request addition of try/except and validation

**Issue: Undocumented**
→ Request basic README with usage

---

**Remember**: DoD ensures quality without perfectionism. Ship working software that meets user needs.
