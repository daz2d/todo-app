# Principle-Based Memory System Design

## Problem
The current memory system stores **specific implementations** (TODO code, calculator patterns) which contaminates agents' thinking. When building a dice roller, agents retrieve TODO patterns and copy them.

**This is like a programmer who can only copy-paste old code, never learning principles.**

## Solution: Store Meta-Knowledge, Not Code

### What to Store

#### ✅ Good (Principles & Lessons)
- **Design Principles**: "Start with in-memory storage before adding persistence"
- **Error Handling Lessons**: "Always validate user input at entry point, not deep in logic"
- **Architecture Patterns**: "Separate data models from business logic for testability"
- **Common Mistakes**: "Don't load all data eagerly - caused performance issues"
- **Testing Insights**: "Edge cases to always test: empty input, invalid types, boundary values"
- **UX Principles**: "Show clear error messages with actionable fix suggestions"

#### ❌ Bad (Specific Code)
- Actual TODO class implementations
- Specific function signatures
- Concrete file names and structures
- Language/framework-specific code

### Memory Types Redesign

#### 1. Procedural Memory (Patterns & Practices)
**Before** (contaminating):
```
PATTERN: TODO Storage
SOLUTION: class TodoStorage with save_todos() and load_todos()
```

**After** (transferable):
```
PRINCIPLE: Persistence Strategy
LESSON: Start simple (JSON file) before complex (database)
WHEN TO USE: When data fits in memory, needs human readability
TRADE-OFFS: Simple to implement, but doesn't scale to 100K+ items
ANTI-PATTERN: Starting with database for 10-item use case
```

#### 2. Error Memory (Failures & Solutions)
**Before** (specific):
```
ERROR: test_add_todo() failed
FIX: Change self.todos.append(item) to self.todos.append(Todo(item))
```

**After** (general):
```
MISTAKE: Type Confusion
SYMPTOM: Function expects object but receives primitive
ROOT CAUSE: Didn't validate types at API boundary
PRINCIPLE: Strong typing at boundaries prevents deep errors
LESSON: Use type hints and validate at entry points
```

#### 3. Episodic Memory (Experiences & Outcomes)
**Before** (full conversation):
```
Turn 5 - Backend: [500 lines of TODO implementation]
```

**After** (insights only):
```
PROJECT OUTCOME: Calculator app approved in 4 turns
KEY DECISIONS:
- Used argument parsing library (faster than manual parsing)
- Implemented error handling first (caught divide-by-zero early)
- Wrote tests alongside implementation (found bugs immediately)
WHAT WORKED: Incremental delivery (add, subtract first, then multiply/divide)
WHAT DIDN'T: Tried fancy UI first - reviewer rejected for missing core functionality
```

#### 4. Semantic Memory (Domain Knowledge)
NEW type for cross-cutting knowledge:
```
DOMAIN: Error Handling
BEST PRACTICES:
- Fail fast: Validate at entry, not deep in call stack
- Be specific: "Invalid email format" beats "Invalid input"
- Suggest fixes: "Use format: name@domain.com"
- Log context: Include user input in error logs

DOMAIN: Testing
BEST PRACTICES:
- Test edge cases: empty, null, zero, negative, max values
- Test error paths: ensure errors are caught and reported
- Test integration: components work together
- Keep tests independent: no shared state between tests
```

### Implementation Changes

#### 1. Update `store_success_pattern()` signature:
```python
def store_principle(
    principle_name: str,        # "Input Validation"
    lesson_learned: str,        # "Always validate at API boundary"
    when_to_apply: str,         # "When accepting user/external input"
    trade_offs: str,           # "Adds overhead but prevents deep errors"
    anti_patterns: List[str],  # ["Validating in business logic"]
    tags: List[str]            # ["error-handling", "architecture"]
)
```

#### 2. Update `learn_from_failure()` to extract principles:
```python
def learn_from_failure(
    mistake_category: str,     # "Type Error", "Performance", "UX"
    symptom: str,              # What went wrong?
    root_cause: str,           # Why did it happen?
    general_principle: str,    # What's the transferable lesson?
    prevention: str,           # How to avoid in future?
    tags: List[str]
)
```

#### 3. Update retrieval to be domain-based:
```python
# Instead of: memory.retrieve(query="TODO app")
# Use: memory.retrieve(domain="persistence", principle_type="storage-patterns")
# Or: memory.retrieve(domain="error-handling", context="user-input")
```

### Agent Integration

#### PM Node:
```python
# Retrieve: Project scoping lessons
principles = memory.get_principles(domain="requirements", tags=["scoping", "prioritization"])
# E.g., "Start with P0 only - teams often over-scope MVP"
```

#### Backend Node:
```python
# Retrieve: Architecture & testing principles
principles = memory.get_principles(domain="architecture", context="starting-new-project")
principles += memory.get_principles(domain="error-handling")
# E.g., "Separate data models from business logic"
```

#### Frontend Node:
```python
# Retrieve: UX & interface principles
principles = memory.get_principles(domain="ux", tags=["error-messages", "usability"])
# E.g., "Show actionable error messages with suggested fixes"
```

#### Reviewer Node:
```python
# Retrieve: Quality & common mistakes
principles = memory.get_principles(domain="code-quality")
mistakes = memory.get_common_mistakes(tags=["testing", "documentation"])
# E.g., "Check if error paths are tested, not just happy path"
```

### Migration Plan

1. ✅ **Phase 1: Disable Current Memory** (DONE)
   - Temporarily disable memory retrieval to stop contamination
   - Delete contaminated memory.db

2. **Phase 2: Update Memory Schema**
   - Add principle-specific tables/fields
   - Add domain categorization
   - Remove/deprecate implementation-specific storage

3. **Phase 3: Update Storage Functions**
   - Change `store_success_pattern()` to `store_principle()`
   - Update `learn_from_failure()` to extract general lessons
   - Add `store_domain_knowledge()` function

4. **Phase 4: Update Retrieval**
   - Change retrieval to be domain/principle-based
   - Filter out any remaining implementation-specific content
   - Add relevance scoring based on principle match, not text similarity

5. **Phase 5: Re-enable in Agents**
   - Update agent nodes to request principles by domain
   - Test that agents get lessons, not code
   - Monitor for any contamination

### Success Criteria

**Good Memory Session:**
```
Agent: Building dice roller
Memory provides: 
- "Use random number generation for unpredictability"
- "Validate input range (1-100 dice is reasonable, 10000 isn't)"
- "Consider edge case: rolling 0 dice"
Agent builds: Dice roller with good practices ✓
```

**Bad Memory Session (Current):**
```
Agent: Building dice roller
Memory provides:
- "class TodoStorage with save_todos()"
- "def add_todo(title, description)"
Agent builds: TODO app ✗
```

### Benefits

1. **Versatility**: Principles apply to any project type
2. **Learning**: Agents improve over time without becoming rigid
3. **Transferability**: Lessons from calculator help with dice roller
4. **Cleanliness**: No code pollution across projects
5. **Human-like**: Like experienced engineers who learned principles, not memorized code

---

**Next Steps:**
1. Implement new memory schema
2. Create principle extraction logic
3. Populate with initial domain knowledge (error handling, testing, etc.)
4. Re-enable memory with new approach
5. Monitor and validate agents stay versatile
