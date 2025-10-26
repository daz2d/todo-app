# URGENT: Rename Parent Directory

## The Issue
The parent directory is called `todo-app` which is contaminating the LLM's context.

## Why This Matters
Even though we removed TODO from:
- ✅ All system prompts
- ✅ All policy files  
- ✅ Tool docstrings
- ✅ Memory database

The directory path `C:\Users\minaa\Documents\Projects\todo-app` appears in:
- Tool execution paths (`Path.cwd()` returns this)
- Error messages (if path validation fails)
- Shell command working directories
- Potentially visible to the LLM's context

## Evidence
Agents keep building CRUD apps with "items" (generic TODO pattern) even when asked for calculators.

## Action Required

### Step 1: Close VS Code
Close this workspace completely to release file locks.

### Step 2: Rename Directory
```powershell
cd C:\Users\minaa\Documents\Projects
Move-Item todo-app ai-dev-team
```

### Step 3: Reopen in VS Code
```powershell
cd ai-dev-team
code .
```

### Step 4: Test
```powershell
python -m src.run_team "Build a number guessing game"
```

Expected: Should build game logic, NOT CRUD items/todos

## Alternative Names
- `ai-dev-team`
- `langteam`
- `agent-team`
- `dev-agents`
- Anything that doesn't have domain-specific bias!

## Why We Didn't Catch This Earlier
The contamination was everywhere:
1. Prompts had TODO examples → Fixed
2. Policies had TODO examples → Fixed
3. Tools had TODO examples → Fixed
4. Memory had TODO patterns → Fixed
5. **Directory name is "todo-app"** ← Current issue!

Each fix helped but wasn't sufficient because contamination came from multiple sources simultaneously.

---

**DO THIS NOW**: Close VS Code, rename directory, reopen, test with fresh project.
