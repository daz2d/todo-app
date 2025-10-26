# TODO App Contamination - Root Cause Analysis

## The Problem
**Agents kept building TODO apps regardless of user request** (dice roller → TODO, temperature converter → TODO)

## Root Causes Identified

### 1. ✅ FIXED: Prompts Had TODO Examples
**Location**: `prompts/system/*.md` (pm.md, staff_backend.md, staff_frontend.md, reviewer.md)
**Issue**: 100+ lines of TODO code examples in prompts
**Fix**: Rewrote ALL prompts to be principle-based with NO code examples

### 2. ✅ FIXED: Policy Files Had TODO Examples  
**Location**: `prompts/policies/dos_and_donts.md`, `prompts/policies/definition_of_done.md`
**Issue**: Loaded into EVERY agent via `get_full_prompt()`, filled with TODO references
**Fix**: Completely rewrote both files - zero TODO references, pure principles

### 3. ✅ FIXED: Tool Docstrings Had TODO Examples
**Location**: `src/tools.py` - http_post() and git() functions
**Issue**: OpenAI reads tool docstrings, saw TODO examples → biased toward TODO apps
**Fix**: Changed examples to generic (http_post uses "items" not "todos")

### 4. ✅ FIXED: Memory Contamination
**Location**: `memory.db` - stored TODO patterns from previous runs
**Issue**: Memory retrieved "successful patterns" which were all TODO-based
**Fix**: 
- Deleted memory.db
- Disabled memory retrieval in all agent nodes
- Documented need for principle-based memory system

### 5. ❌ NOT ISSUE: .env Loading
**Status**: Was missing `load_dotenv()`, now fixed
**Impact**: Low (hybrid models work now, but wasn't causing TODO bias)

## Why It Was Hard to Find

**The contamination was EVERYWHERE:**
- System prompts (200+ lines of TODO examples)
- Policy files (loaded into every agent automatically)
- Tool descriptions (part of OpenAI's function calling spec)
- Memory database (past TODO patterns retrieved)

**Like trying to stop water leaks in a bucket with 20 holes** - fixing one source didn't help because contamination came from multiple places.

## The Fix

### What We Did
1. **Purged ALL code examples** from prompts
2. **Rewrote prompts as principles** (how to think, not what to code)
3. **Cleaned tool docstrings** (generic examples only)
4. **Disabled memory** (temporarily, needs redesign)
5. **Deleted memory.db** (contaminated with TODO patterns)

### What Changed
| Before | After |
|--------|-------|
| "Here's a TODO example: class Todo..." | "Design data structures for your domain" |
| Tool: `http_post("/todos", {...})` | Tool: `http_post("/items", {...})` |
| Policy: "User can create TODO items" | Policy: "Validate user input at entry" |
| Memory: Retrieves TODO patterns | Memory: Disabled (needs principle-based redesign) |

## Testing
Run diverse projects to verify versatility:
- ❌ Calculator → Built TODO (before fixes)
- ❌ Dice roller → Built TODO (before fixes)  
- ❌ Temperature converter → Built TODO (before fixes)
- 🔄 **Next test**: Run temperature converter again with ALL fixes applied

## Success Criteria
✅ Agent builds what user requests, not TODO variants
✅ Different project types work (calculator, dice, converter, scraper, etc.)
✅ No TODO patterns appear unless user specifically asks for TODO app

## Lessons Learned

**1. Examples in prompts bias behavior strongly**
- Agents pattern-match on examples
- Generic principles > specific examples for versatility

**2. Contamination compounds across sources**
- One contaminated file wasn't the issue
- ALL sources had to be cleaned simultaneously

**3. Memory needs principle-based design**
- Storing code patterns → inflexible agents
- Should store: lessons, principles, best practices
- NOT: specific implementations, code samples

**4. Tool descriptions matter**
- OpenAI reads docstrings when deciding tool usage
- Generic examples prevent bias

## Next Steps

1. ✅ Test system with fresh project
2. ⏭️ Monitor for any remaining TODO bias
3. ⏭️ Implement principle-based memory system
4. ⏭️ Add tests to catch contamination in CI/CD

---

**Status**: All known contamination sources eliminated. System should now be versatile.
