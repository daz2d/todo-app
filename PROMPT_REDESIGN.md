# Prompt Design Changes

## Problem
Agents were copying code examples from prompts instead of thinking about the user's request. They kept building TODO apps regardless of what was asked for.

## Root Cause
**Example-based prompts bias agent behavior**
- Prompts contained 100+ lines of TODO app example code
- Agents pattern-matched on examples instead of understanding principles
- Led to inflexible, non-versatile behavior

## Solution
**Switched to principle-based prompts**

### What We Removed
❌ All code examples (def, class, import statements)
❌ All specific app references (TODO, calculator, etc.)
❌ Step-by-step implementation examples
❌ "Here's how to do X" patterns

### What We Added
✅ Design principles (e.g., "Start Simple", "Handle Errors Gracefully")
✅ Process guidelines (e.g., "Read SPEC → Design → Create Files → Test")
✅ Communication patterns (what to ask, when to escalate)
✅ Quality standards (what makes code good/acceptable)
✅ Tool usage rules (MUST call write_file, not describe it)

## New Prompt Structure

### PM Prompt
- **Focus**: Translating needs to testable SPEC
- **Principles**: Make criteria testable, prioritize ruthlessly, stay in your lane
- **No Examples**: Just SPEC template structure

### Backend Prompt
- **Focus**: Core logic and data structures
- **Principles**: Start simple, think about data, handle errors, make it testable
- **Critical**: Emphasizes USING tools, not describing them

### Frontend Prompt
- **Focus**: User interaction and experience
- **Principles**: Make it obvious, follow conventions, fail loudly, think about flow
- **Critical**: Wire to backend, create actual files

### Reviewer Prompt
- **Focus**: Quality gate using Definition of Done
- **Principles**: Be specific, be fair, be constructive
- **Decision**: Approve (with "APPROVED") or request changes (specific actions)

## Key Differences

| Before | After |
|--------|-------|
| "Here's a TODO app example" | "Design data structures for your problem" |
| "Create `todo.py` with this code" | "Use write_file() to create your solution" |
| "Import TodoStorage" | "Think about where data is stored" |
| Code-heavy (200+ lines examples) | Principle-heavy (70-100 lines guidelines) |
| Prescriptive (do exactly this) | Descriptive (consider these principles) |

## Expected Benefits

1. **Versatility**: Agents can build ANY app, not just TODO clones
2. **Creativity**: Agents think about the problem, not copy patterns
3. **Tool Usage**: Clear that tools MUST be called, not described
4. **Adaptability**: Principles apply to any project type
5. **Quality**: Focus on "what makes good code" not "copy this code"

## Testing Plan

Run diverse project types to verify versatility:
- ✅ Calculator app
- ✅ Dice roller app
- 🔄 Data processing script
- 🔄 Web scraper
- 🔄 File organizer

Success = agents build what's asked, not TODO variants
