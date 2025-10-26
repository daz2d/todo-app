"""
LangGraph State Machine

Defines the agile team workflow: PM → Backend → Frontend → Reviewer → (loop or end).
Integrates memory and learning throughout the process.
"""

import os
from pathlib import Path
from typing import TypedDict, List, Annotated
from operator import add
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from .llm import get_chat_model, get_smart_model
from .tools import get_enabled_tools, reset_turn_counters, SANDBOX_DIR
from .roles import RolePrompts
from .memory import MemorySystem
import hashlib


# Team State Definition
class TeamState(TypedDict):
    """State shared across all agents in the team."""
    user_goal: str
    spec: str
    backend_notes: str
    frontend_notes: str
    review_notes: str
    qa_notes: str
    test_results: str
    approvals: Annotated[List[str], add]  # List of approvers
    turns: int
    approved: bool
    qa_approved: bool
    memories_retrieved: List[str]  # Relevant past experiences
    
    # Progress tracking to prevent loops
    last_backend_hash: str  # Hash of last backend output
    last_frontend_hash: str  # Hash of last frontend output
    stagnation_count: int  # Consecutive turns without progress
    files_created: List[str]  # Track which files have been created


# Configuration
MAX_TURNS = int(os.getenv('MAX_TURNS', '10'))


def detect_stagnation(state: TeamState, current_output: str, role: str) -> bool:
    """
    Detect if the agent is stuck in a loop or not making progress.
    
    Returns True if stagnation detected.
    """
    # Create hash of current output
    current_hash = hashlib.md5(current_output.encode()).hexdigest()
    
    # Check if this is the same as last time for this role
    if role == 'backend':
        last_hash = state.get('last_backend_hash', '')
        state['last_backend_hash'] = current_hash
    elif role == 'frontend':
        last_hash = state.get('last_frontend_hash', '') 
        state['last_frontend_hash'] = current_hash
    else:
        return False
    
    # If output is identical to last time, increment stagnation
    if current_hash == last_hash and last_hash != '':
        state['stagnation_count'] = state.get('stagnation_count', 0) + 1
        print(f"⚠️ {role.title()} output identical to previous turn! Stagnation count: {state['stagnation_count']}")
        return state['stagnation_count'] >= 2
    else:
        state['stagnation_count'] = 0
        return False


def get_dynamic_status_message(person: str, context: str) -> str:
    """Generate dynamic status messages for team members."""
    import random
    
    messages = {
        'jamie_backend': [
            "Jamie is probably refactoring code for the 3rd time today 🤦‍♂️",
            "Jamie's deep in thought - you can hear the keyboard clicking from here! ⌨️",  
            "Jamie just muttered something about 'elegant algorithms' - they're in the zone! 🧠",
            "Jamie's caffeinating before diving into the serious backend work ☕",
            "Jamie's testing their code locally - always the careful one! 🧪"
        ],
        'riley_frontend': [
            "Riley is probably agonizing over color schemes again 🎨",
            "Riley just asked 'Does this look intuitive?' for the 10th time today 😄",
            "Riley's sketching wireframes on napkins - true artist! ✏️",
            "Riley's testing the UI on their phone, tablet, AND laptop 📱",
            "Riley muttered 'User experience is everything' and went back to designing 💫"
        ]
    }
    
    key = f"{person}_{context}"
    options = messages.get(key, [f"{person} is working on {context}"])
    return random.choice(options)


def add_variety_context(state: TeamState, role: str) -> str:
    """
    Add dynamic context to make conversations more varied and prevent loops.
    """
    variety_prompts = {
        'backend': [
            "🔥 Jamie, Alex is expecting some serious backend magic this turn! Show off those algorithms!",
            "💪 Time to flex those backend muscles, Jamie! Riley is counting on you for solid APIs!",
            "🚀 Jamie, let's build something that'll make our college professors proud!",
            "⚡ Backend time! Jamie, remember that time you debugged that impossible recursive function? Channel that energy!",
            "🎯 Jamie, focus mode engaged! Let's write some clean, testable backend code!"
        ],
        'frontend': [
            "✨ Riley, time to make this interface absolutely gorgeous! Show Jamie how UI magic is done!",
            "🎨 Riley, channel your inner artist! Make this so pretty that even Morgan can't find fault with it!",
            "💫 Frontend wizardry time! Riley, let's create something users will actually enjoy using!",
            "🌟 Riley, remember our design class? Time to put those principles to work!",
            "🎭 Riley, make this interface so intuitive that even Casey's destructive testing can't break it!"
        ]
    }
    
    import random
    prompts = variety_prompts.get(role, [])
    if prompts and state.get('turns', 0) > 1:
        return f"\n🗣️ **Team Motivation**: {random.choice(prompts)}\n"
    return ""


# Agent Node Functions

def pm_node(state: TeamState) -> TeamState:
    """
    Product Manager node: Creates and maintains SPEC.
    
    Responsibilities:
    - Gather requirements if user_goal is vague
    - Create/update SPEC.md with acceptance criteria
    - Break down work into tasks for engineers
    - Incorporate review feedback
    """
    print(f"\n🎯{'='*58}🎯")
    print(f"  📋 PM ALEX IS ON THE CASE (Turn {state['turns'] + 1}) 📋")
    print(f"🎯{'='*58}🎯")
    
    # Reset turn counters for tools
    reset_turn_counters()
    
    # Load prompts and memory
    prompts = RolePrompts()
    memory = MemorySystem()
    
    # DISABLED: Memory retrieval temporarily disabled
    # Re-enable with principle-based memory
    # past_specs = memory.retrieve(
    #     query=state['user_goal'],
    #     memory_type='episodic',
    #     tags=['pm'],
    #     success_only=True,
    #     limit=3
    # )
    
    past_context = ""
    # past_context = "\n\n".join([
    #     f"PAST EXPERIENCE:\n{m.content}\nCONTEXT: {m.context}"
    #     for m in past_specs
    # ]) if past_specs else "No directly relevant past experiences."
    
    # Build context message
    context = f"""
USER GOAL: {state['user_goal']}

CURRENT SPEC:
{state['spec'] if state['spec'] else '[No SPEC yet - create one]'}

BACKEND NOTES:
{state['backend_notes'] if state['backend_notes'] else '[No backend work yet]'}

FRONTEND NOTES:
{state['frontend_notes'] if state['frontend_notes'] else '[No frontend work yet]'}

REVIEW FEEDBACK:
{state['review_notes'] if state['review_notes'] else '[No review yet]'}

PAST EXPERIENCES:
{past_context}

TURN: {state['turns'] + 1} of {MAX_TURNS}

INSTRUCTIONS:
{prompts.get_pm_prompt()}

Your task:
1. If this is turn 1 and SPEC is empty: Create detailed SPEC with numbered acceptance criteria
2. If review feedback exists: Update SPEC or provide clear guidance to engineers
3. Break down remaining work into concrete tasks with priorities (P0/P1/P2)
4. Handoff to Backend and Frontend engineers with specific action items

Output your response as PM notes.
"""
    
    # Get LLM response (PM doesn't need tools, use fast local model)
    model = get_smart_model(needs_tools=False)
    response = model.invoke([
        SystemMessage(content=prompts.get_full_prompt('pm')),
        HumanMessage(content=context)
    ])
    
    pm_output = response.content
    
    # Improved SPEC extraction - handle various formats and provide debugging
    spec_extracted = False
    
    # Method 1: Look for formal SPEC headers
    if "# SPEC" in pm_output or "## Goal" in pm_output or "### Goal" in pm_output:
        spec_lines = []
        in_spec = False
        for line in pm_output.split('\n'):
            if any(header in line for header in ['# SPEC', '# Specification', '## Goal', '### Goal']):
                in_spec = True
            if in_spec:
                spec_lines.append(line)
        
        if spec_lines:
            state['spec'] = '\n'.join(spec_lines)
            spec_extracted = True
            print(f"✓ SPEC extracted using formal headers ({len(spec_lines)} lines)")
    
    # Method 2: If no formal SPEC found, but PM mentions goals/criteria, extract those sections
    if not spec_extracted and ("Acceptance Criteria" in pm_output or "Tasks" in pm_output):
        # Extract key sections even without formal headers
        lines = pm_output.split('\n')
        spec_lines = []
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in ['Goal', 'Acceptance Criteria', 'Tasks', '**P0', '**P1']):
                # Include this line and context
                start_idx = max(0, i-1)
                end_idx = min(len(lines), i+10)  # Include next 10 lines for context
                spec_lines.extend(lines[start_idx:end_idx])
                break
        
        if spec_lines:
            state['spec'] = f"# SPEC: {state['user_goal']}\n\n" + '\n'.join(spec_lines)
            spec_extracted = True
            print(f"✓ SPEC extracted using content analysis ({len(spec_lines)} lines)")
    
    # Method 3: If still no SPEC, use the entire PM output as informal SPEC
    if not spec_extracted and state['turns'] == 0:  # First turn, PM should create SPEC
        state['spec'] = f"# SPEC: {state['user_goal']}\n\n{pm_output}"
        spec_extracted = True
        print(f"⚠ Using entire PM output as SPEC (no formal structure found)")
    
    # Validation
    if not spec_extracted:
        print(f"⚠ WARNING: No SPEC extracted from PM output on turn {state['turns'] + 1}")
    elif len(state['spec']) < 50:
        print(f"⚠ WARNING: SPEC seems too short ({len(state['spec'])} chars)")
    else:
        print(f"✓ SPEC successfully stored ({len(state['spec'])} characters)")
    
    # Save SPEC to file for visibility and debugging
    if spec_extracted and state['spec']:
        try:
            # Create docs directory in current working directory (project directory)
            docs_dir = Path.cwd() / "docs"
            docs_dir.mkdir(exist_ok=True)
            spec_file = docs_dir / "SPEC.md"
            spec_file.write_text(state['spec'], encoding='utf-8')
            print(f"✓ SPEC saved to {spec_file}")
        except Exception as e:
            print(f"⚠ Failed to save SPEC to file: {e}")
    
    # Store in memory
    memory.store_conversation(
        role='pm',
        turn=state['turns'] + 1,
        notes=pm_output,
        context=f"User goal: {state['user_goal'][:100]}"
    )
    
    print(pm_output)
    
    state['turns'] += 1
    return state


def backend_node(state: TeamState) -> TeamState:
    """
    Backend Engineer node: Implements backend/infrastructure.
    
    Responsibilities:
    - Design architecture with trade-offs
    - Implement backend slices incrementally
    - Use tools (shell, http, git) as needed
    - Document implementation and next steps
    """
    print(f"\n🔧{'='*58}🔧")
    print(f"  💻 BACKEND JAMIE REPORTING FOR DUTY (Turn {state['turns']}) 💻")
    print(f"🔧{'='*58}🔧")
    
    # VALIDATION: Ensure SPEC exists before proceeding
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("🤦‍♂️ Yo Alex, where's my SPEC dude?!")
        print("🍺 Can't code without knowing what I'm building - you know this!")
        print("☕ Go grab a coffee and write me something to work with 😄")
        
        # Store error and request PM intervention
        error_msg = f"Jamie to Alex: Dude, seriously? Turn {state['turns']} and still no SPEC? 😂 Get your act together buddy! I need requirements to build this thing properly. You've got this! 💪"
        state['backend_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"🎉 Sweet! Alex came through with a solid SPEC ({len(state['spec'])} chars) - let's build this thing! 🚀")
    
    reset_turn_counters()
    
    prompts = RolePrompts()
    memory = MemorySystem()
    
    # DISABLED: Memory retrieval was contaminating agents with TODO patterns
    # TODO: Re-enable with principle-based memory (best practices, not code)
    # patterns = memory.retrieve(
    #     query=state['spec'][:200] if state['spec'] else state['user_goal'],
    #     memory_type='procedural',
    #     success_only=True,
    #     limit=2
    # )
    # 
    # errors = memory.retrieve(
    #     query=state['spec'][:200] if state['spec'] else state['user_goal'],
    #     memory_type='error',
    #     limit=2
    # )
    
    past_context = ""
    # if patterns:
    #     past_context += "\n\nSUCCESSFUL PATTERNS:\n" + "\n---\n".join([p.content for p in patterns])
    # if errors:
    #     past_context += "\n\nPAST MISTAKES TO AVOID:\n" + "\n---\n".join([e.content for e in errors])
    
    context = f"""
🎯 ALEX'S REQUIREMENTS (The Gospel According to PM):
==========================================
{state['spec']}
==========================================

💪 Jamie's Mission: Build EXACTLY what Alex specified above (no creative liberties this time! 😄)

💻 MY PREVIOUS BACKEND WORK:
{state['backend_notes'] if state['backend_notes'] else '[Clean slate - time to build something awesome! 🚀]'}

🎨 RILEY'S FRONTEND ADVENTURES:
{state['frontend_notes'] if state['frontend_notes'] else '[Riley is probably still choosing the perfect color scheme 🎭]'}

🔍 MORGAN'S BRUTALLY HONEST FEEDBACK:
{state['review_notes'] if state['review_notes'] else '[Morgan hasn\'t shredded my code yet - I must be doing something right! 😅]'}

{past_context}

🏃‍♂️ TURN {state['turns']} of {MAX_TURNS} - Let's make magic happen!

Jamie's Epic To-Do List:
1. 📖 Read Alex's SPEC like it's the holy scripture
2. 🔧 Build backend logic that would make my professors proud  
3. 🧪 Write tests so Casey doesn't find bugs to mock me about
4. 📝 Document everything so Riley can work their frontend magic
5. 🎯 Stay focused (no rabbit holes this time!)

Output your implementation notes, architecture decisions, and deliverables.
"""
    
    # Get model with tools (Backend needs tools - use smart routing)
    model = get_smart_model(needs_tools=True)
    tools = get_enabled_tools()
    
    # Try to use tools, but fall back to no tools if not supported
    try:
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke([
            SystemMessage(content=prompts.get_full_prompt('backend')),
            HumanMessage(content=context)
        ])
        
        # Execute tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"\n🔧 Executing {len(response.tool_calls)} tool call(s)...")
            
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                
                print(f"  → {tool_name}({', '.join(f'{k}={v[:50]}...' if len(str(v)) > 50 else f'{k}={v}' for k, v in tool_args.items())})")
                
                # Find and execute the tool
                for tool in tools:
                    if tool.name == tool_name:
                        try:
                            result = tool.func(**tool_args)
                            print(f"    ✓ Result: {result[:100]}..." if len(str(result)) > 100 else f"    ✓ Result: {result}")
                        except Exception as e:
                            print(f"    ✗ Error: {e}")
                        break
            
            print()
        
    except Exception as e:
        if "does not support tools" in str(e):
            print(f"⚠️  Note: Model doesn't support tools. Using without tool binding.")
            response = model.invoke([
                SystemMessage(content=prompts.get_full_prompt('backend')),
                HumanMessage(content=context)
            ])
        else:
            raise
    
    backend_output = response.content
    
    # Check for stagnation
    if detect_stagnation(state, backend_output, 'backend'):
        backend_output += "\n\n🔄 **JAMIE'S FRUSTRATION**: Ugh, I think I'm repeating myself! Let me try a different approach..."
        backend_output += "\n💡 **NEW STRATEGY**: Let me focus on the core requirements and build something minimal but functional."
    
    # Add variety context for next round
    variety_context = add_variety_context(state, 'backend')
    if variety_context:
        backend_output += variety_context
    
    # Append to backend notes
    if state['backend_notes']:
        state['backend_notes'] += f"\n\n--- Turn {state['turns']} ---\n{backend_output}"
    else:
        state['backend_notes'] = backend_output
    
    # Store in memory
    memory.store_conversation(
        role='backend',
        turn=state['turns'],
        notes=backend_output,
        context=state['spec'][:200] if state['spec'] else state['user_goal'][:200]
    )
    
    print(backend_output)
    
    return state


def frontend_node(state: TeamState) -> TeamState:
    """
    Frontend Engineer node: Implements UI/UX and developer experience.
    
    Responsibilities:
    - Build user interfaces and interactions
    - Wire LLM tools and LangGraph components
    - Focus on usability and polish
    - Document usage and examples
    """
    print(f"\n🎨{'='*58}🎨")
    print(f"  ✨ FRONTEND RILEY MAKING IT PRETTY (Turn {state['turns']}) ✨")
    print(f"🎨{'='*58}🎨")
    
    # VALIDATION: Ensure SPEC exists before proceeding
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("🤷‍♀️ Alex, sweetie, where's my SPEC? I can't make magic without knowing what we're building!")
        print("💅 You know I need those requirements to make this thing user-friendly!")
        print("🎭 Come on, give me something to work with - make it snappy! 😉")
        
        error_msg = f"Riley to Alex: Babe, it's turn {state['turns']} and I'm still waiting for a SPEC! 😅 You know I can't build a gorgeous UI without knowing what it should DO! Help a girl out here! 💖"
        state['frontend_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"🌟 Perfect! Alex delivered the goods - {len(state['spec'])} chars of pure requirements gold! Time to make this beautiful! 💎")
    
    reset_turn_counters()
    
    prompts = RolePrompts()
    memory = MemorySystem()
    
    # DISABLED: Memory retrieval temporarily disabled
    # Re-enable with principle-based memory
    # patterns = memory.retrieve(
    #     query='UI UX CLI interface',
    #     memory_type='procedural',
    #     success_only=True,
    #     limit=2
    # )
    
    past_context = ""
    # if patterns:
    #     past_context = "\n\nSUCCESSFUL UI PATTERNS:\n" + "\n---\n".join([p.content for p in patterns])
    
    context = f"""
✨ ALEX'S VISION (Time to Make It Pretty!):
==========================================
{state['spec']}
==========================================

🎨 Riley's Mission: Make this UI so gorgeous Alex cries happy tears! (But follow the SPEC exactly 😉)

🔧 JAMIE'S BACKEND UPDATES:
{state['backend_notes'] if state['backend_notes'] else get_dynamic_status_message('jamie', 'backend')}

💅 MY PREVIOUS FRONTEND WORK:
{state['frontend_notes'] if state['frontend_notes'] else '[Fresh canvas - time to paint something beautiful! 🎨]'}

🔍 MORGAN'S DESIGN CRITIQUE:
{state['review_notes'] if state['review_notes'] else '[Morgan hasn\'t judged my UI choices yet - fingers crossed! 🤞]'}

{past_context}

⚡ TURN {state['turns']} of {MAX_TURNS} - Let's make this interface sing!

Riley's Fabulous Checklist:
1. 📖 Study Alex's SPEC like it's the latest fashion magazine
2. 🔌 Connect to Jamie's brilliant backend work (they better have documented it!)
3. ✨ Create an interface so intuitive even our professors could use it
4. 🧪 Write some UI tests so Casey can't complain about broken buttons
5. 💫 Add that special Riley touch (but stay within SPEC bounds!)
4. Use tools as needed (shell, git, http)
5. Focus on user experience and clear error messages

Output your implementation notes, UX decisions, and deliverables.
"""
    
    model = get_smart_model(needs_tools=True)
    tools = get_enabled_tools()
    
    # Try to use tools, but fall back to no tools if not supported
    try:
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke([
            SystemMessage(content=prompts.get_full_prompt('frontend')),
            HumanMessage(content=context)
        ])
        
        # Execute tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"\n🔧 Executing {len(response.tool_calls)} tool call(s)...")
            
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                
                print(f"  → {tool_name}({', '.join(f'{k}={v[:50]}...' if len(str(v)) > 50 else f'{k}={v}' for k, v in tool_args.items())})")
                
                # Find and execute the tool
                for tool in tools:
                    if tool.name == tool_name:
                        try:
                            result = tool.func(**tool_args)
                            print(f"    ✓ Result: {result[:100]}..." if len(str(result)) > 100 else f"    ✓ Result: {result}")
                        except Exception as e:
                            print(f"    ✗ Error: {e}")
                        break
            
            print()
        
    except Exception as e:
        if "does not support tools" in str(e):
            print(f"⚠️  Note: Model doesn't support tools. Using without tool binding.")
            response = model.invoke([
                SystemMessage(content=prompts.get_full_prompt('frontend')),
                HumanMessage(content=context)
            ])
        else:
            raise
    
    frontend_output = response.content
    
    # Check for stagnation
    if detect_stagnation(state, frontend_output, 'frontend'):
        frontend_output += "\n\n🎨 **RILEY'S REALIZATION**: Wait, I think I'm in a creative loop! Let me step back and focus on the essentials..."
        frontend_output += "\n✨ **FRESH PERSPECTIVE**: Time to build something simple that actually works first, then make it pretty!"
    
    # Add variety context for next round
    variety_context = add_variety_context(state, 'frontend')
    if variety_context:
        frontend_output += variety_context
    
    # Append to frontend notes
    if state['frontend_notes']:
        state['frontend_notes'] += f"\n\n--- Turn {state['turns']} ---\n{frontend_output}"
    else:
        state['frontend_notes'] = frontend_output
    
    # Store in memory
    memory.store_conversation(
        role='frontend',
        turn=state['turns'],
        notes=frontend_output,
        context=state['spec'][:200] if state['spec'] else state['user_goal'][:200]
    )
    
    print(frontend_output)
    
    return state


def reviewer_node(state: TeamState) -> TeamState:
    """
    Code Reviewer node: Enforces Definition of Done.
    
    Responsibilities:
    - Check all DoD criteria
    - Validate against SPEC acceptance criteria
    - Approve (include "APPROVED") or request changes
    - Provide explicit, actionable feedback
    """
    print(f"\n🔍{'='*58}🔍")
    print(f"  🕵️ CODE REVIEWER MORGAN ON THE HUNT (Turn {state['turns']}) 🕵️")
    print(f"🔍{'='*58}🔍")
    
    # VALIDATION: Ensure SPEC exists for proper review
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("🤨 Hold up team! Can't review code against thin air - Alex, where's that SPEC?!")
        error_msg = f"Morgan to Alex: Buddy, turn {state['turns']} and I still don't have a proper SPEC to review against! 😤 You know I can't do my job without knowing what we're supposed to be building! Get me those requirements! 📋"
        state['review_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"🎯 Excellent! Got {len(state['spec'])} chars of solid requirements - time to see what Jamie and Riley built! 🔎")
    
    reset_turn_counters()
    
    prompts = RolePrompts()
    memory = MemorySystem()
    
    # DISABLED: Memory retrieval temporarily disabled
    # Re-enable with principle-based memory
    # past_reviews = memory.retrieve(
    #     memory_type='episodic',
    #     tags=['reviewer'],
    #     limit=2
    # )
    
    past_context = ""
    # if past_reviews:
    #     past_context = "\n\nPAST REVIEW PATTERNS:\n" + "\n---\n".join([
    #         f"{r.content[:300]}..." for r in past_reviews
    #     ])
    
    context = f"""
🎯 PRIMARY SPECIFICATION TO VALIDATE AGAINST:
==========================================
{state['spec']}
==========================================

❗ CRITICAL REVIEWER INSTRUCTIONS:
1. Check that EVERY acceptance criteria in the above SPEC is met
2. Verify that the implementation matches the specified requirements
3. Ensure no generic functionality was built that doesn't match the SPEC
4. Only approve if the deliverables satisfy the EXACT requirements above

BACKEND DELIVERABLES:
{state['backend_notes'] if state['backend_notes'] else '[No backend work to review]'}

FRONTEND DELIVERABLES:
{state['frontend_notes'] if state['frontend_notes'] else '[No frontend work to review]'}

PREVIOUS REVIEW:
{state['review_notes'] if state['review_notes'] else '[No previous review]'}

{past_context}

TURN: {state['turns']} of {MAX_TURNS}
APPROACHING LIMIT: {'YES - prioritize core P0 functionality' if state['turns'] >= MAX_TURNS - 2 else 'No'}

INSTRUCTIONS:
{prompts.get_reviewer_prompt()}

Your task:
1. Read Definition of Done criteria carefully
2. Check each SPEC acceptance criterion
3. Review code quality, tests, documentation
4. APPROVE (include word "APPROVED") if DoD met, OR
5. Request specific changes with actionable items

IMPORTANT: Include the word "APPROVED" (case-insensitive) in your review if ready to ship.

Output your code review with decision.
"""
    
    model = get_smart_model(needs_tools=False)
    
    response = model.invoke([
        SystemMessage(content=prompts.get_full_prompt('reviewer')),
        HumanMessage(content=context)
    ])
    
    review_output = response.content
    
    # Check for approval
    if 'approved' in review_output.lower():
        state['approved'] = True
        state['approvals'].append(f"Reviewer (Turn {state['turns']})")
        
        # Record success in memory
        memory.record_statistic('turns_to_approval', float(state['turns']), state['user_goal'][:100])
        
        # Store successful workflow
        memory.store_success_pattern(
            pattern_name=f"Successful workflow for: {state['user_goal'][:50]}",
            description=f"Completed in {state['turns']} turns",
            implementation=f"SPEC:\n{state['spec'][:500]}\n\nApproach worked well.",
            context=state['user_goal'][:200],
            tags=['workflow', 'approved', f'turns-{state["turns"]}']
        )
    else:
        # Not approved - potential learning opportunity
        if state['turns'] > 5:  # Multiple iterations without approval
            memory.learn_from_failure(
                failure_description=f"Project not approved after {state['turns']} turns",
                root_cause="Unclear requirements, complex scope, or missed DoD criteria",
                solution=review_output[:500],
                context=state['user_goal'][:200],
                tags=['iteration', 'approval', 'review']
            )
    
    # Append to review notes
    if state['review_notes']:
        state['review_notes'] += f"\n\n--- Turn {state['turns']} Review ---\n{review_output}"
    else:
        state['review_notes'] = review_output
    
    # Store in memory
    memory.store_conversation(
        role='reviewer',
        turn=state['turns'],
        notes=review_output,
        context=state['user_goal'][:200]
    )
    
    print(review_output)
    
    return state


def qa_tester_node(state: TeamState) -> TeamState:
    """
    QA Tester node: Creates and runs comprehensive tests.
    
    Responsibilities:
    - Analyze SPEC requirements for testability
    - Write comprehensive test suites (unit, integration, e2e)
    - Execute tests and validate code meets all acceptance criteria
    - Report test results and coverage
    - Identify any gaps between implementation and requirements
    """
    print(f"\n🧪{'='*58}🧪")
    print(f"  🔬 QA TESTER CASEY BREAKING THINGS (Turn {state['turns']}) 🔬")
    print(f"🧪{'='*58}🧪")
    
    # VALIDATION: Ensure SPEC exists before testing
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("🤦‍♂️ Oh come ON Alex! How am I supposed to test this thing without a SPEC?!")
        print("🧪 I can't break what doesn't have requirements! Give me something to validate against!")
        print("💥 You know I live to find bugs, but I need to know what's supposed to work first! 😂")
        
        error_msg = f"Casey to Alex: Dude, it's turn {state['turns']} and I'm sitting here with my testing hat on and NO SPEC! 🤪 I can't write tests to verify requirements if there ARE no requirements! Help me help you! 🧪💪"
        state['qa_notes'] = error_msg
        state['test_results'] = "BLOCKED: Casey can't test without requirements (come on Alex!) 😅"
        state['qa_approved'] = False
        print(error_msg)
        return state
    
    print(f"🎯 Sweet! Alex came through with {len(state['spec'])} chars of testable requirements! Time to see if Jamie and Riley's code can survive my tests! 😈")
    
    reset_turn_counters()
    
    prompts = RolePrompts()
    memory = MemorySystem()
    
    # Build context for QA tester
    context = f"""
🎯 SPECIFICATION TO TEST AGAINST:
===============================
{state['spec']}
===============================

📋 BACKEND IMPLEMENTATION NOTES:
{state.get('backend_notes', 'No backend notes available')}

📋 FRONTEND IMPLEMENTATION NOTES:
{state.get('frontend_notes', 'No frontend notes available')}

📋 CODE REVIEW FEEDBACK:
{state.get('review_notes', 'No review notes available')}

🎯 YOUR MISSION:
Create comprehensive tests that verify every acceptance criteria in the SPEC is met.
Write tests, execute them, and report results. Be thorough and critical.
"""
    
    # Get QA model (use smart model for testing work)
    model = get_smart_model()
    if not model:
        print("⚠️ Using text-only model: ollama/llama3.2:latest")
        model = get_chat_model()
    else:
        print("🔧 Using tool-capable model: openai/gpt-4o-mini")
    
    # Create QA message
    messages = [
        SystemMessage(content=prompts.get_full_prompt('qa_tester')),
        HumanMessage(content=context.strip())
    ]
    
    # Get tools if available  
    tools = get_enabled_tools()
    if tools and hasattr(model, 'bind_tools'):
        model_with_tools = model.bind_tools(tools)
        qa_output = model_with_tools.invoke(messages).content
    else:
        qa_output = model.invoke(messages).content
    
    print(qa_output)
    
    # Simple approval heuristic for QA (look for test pass indicators)
    qa_approved = any([
        "all tests pass" in qa_output.lower(),
        "✅" in qa_output and "test" in qa_output.lower(),
        "requirements met" in qa_output.lower(),
        "acceptance criteria satisfied" in qa_output.lower(),
        "quality approved" in qa_output.lower()
    ])
    
    state['qa_approved'] = qa_approved
    
    if qa_approved:
        print("\n🎉 BOOM! Casey's seal of approval - all tests passed! Jamie and Riley, you didn't disappoint! 🥳")
        approval_msg = f"Casey (Turn {state['turns']}): Holy cow, everything works! 🧪✅ You two actually built something that doesn't break! 😱"
        state['approvals'].append(approval_msg)
    else:
        print("\n💥 Uh oh... Casey found some issues! Time for round 2, team! 🔧")
    
    # Store QA results
    if state['qa_notes']:
        state['qa_notes'] += f"\n\n--- Turn {state['turns']} QA Report ---\n{qa_output}"
    else:
        state['qa_notes'] = qa_output
    
    # Extract test results section if present
    test_results = "Tests executed - see QA notes for details"
    if "TEST EXECUTION RESULTS" in qa_output:
        try:
            results_start = qa_output.index("TEST EXECUTION RESULTS")
            results_section = qa_output[results_start:results_start+500]
            test_results = results_section
        except:
            pass
    
    state['test_results'] = test_results
    
    # Store in memory
    memory.store_conversation(
        role='qa_tester',
        turn=state['turns'],
        notes=qa_output[:1000],  # Truncate for memory storage
        context=f"Testing: {state['user_goal'][:100]}"
    )
    
    return state


# Routing Logic

def should_continue(state: TeamState) -> str:
    """
    Decide whether to continue iteration or end.
    
    Returns:
        'end' if both code review AND QA approved, or MAX_TURNS reached, otherwise 'continue'.
    """
    # Check for stagnation (team stuck in loops)
    stagnation_count = state.get('stagnation_count', 0)
    if stagnation_count >= 3:
        print(f"\nSTAGNATION DETECTED! The team seems stuck in a loop!")
        print(f"After {stagnation_count} identical outputs, let's wrap this up and ship what we have.")
        print(f"Sometimes done is better than perfect - great work team!")
        return 'end'
    
    # Require both code review approval AND QA approval
    if state['approved'] and state.get('qa_approved', False):
        print(f"\n🎉🎊 BOOM! BOTH MORGAN AND CASEY SIGNED OFF! 🎊🎉")
        print(f"🍻 Time to celebrate - this baby is SHIPPED! Great work team! 🚀")
        return 'end'
    
    if state['turns'] >= MAX_TURNS:
        print(f"\n⏰ Alright team, we've hit the {MAX_TURNS} turn limit - time to wrap this up!")
        print(f"📋 Morgan's Review: {'✅ Approved!' if state['approved'] else '❌ Still needs work'}")
        print(f"🧪 Casey's Tests: {'✅ All passed!' if state.get('qa_approved', False) else '❌ Found issues'}")
        print(f"☕ Maybe grab some coffee and tackle the remaining issues next sprint? 😅")
        return 'end'
    
    # Show current approval status
    if state['approved'] and not state.get('qa_approved', False):
        print(f"\n🎯 Morgan approved the code! Waiting on Casey to finish testing... 🧪⏳")
    elif not state['approved'] and state.get('qa_approved', False):
        print(f"\n🧪 Casey's tests all passed! Waiting on Morgan's code review... 🔍⏳")
    else:
        encouragements = [
            f"Round {state['turns']} - let's make this even more awesome!",
            f"Turn {state['turns']} - team, let's show what we've got!",
            f"Iteration {state['turns']} - almost there, keep pushing!",
            f"Turn {state['turns']} - polish time, make it shine!"
        ]
        import random
        print(f"\n{random.choice(encouragements)}")
    
    return 'continue'


# Graph Construction

def create_team_graph():
    """
    Create and compile the LangGraph workflow.
    
    Returns:
        Compiled LangGraph application.
    """
    workflow = StateGraph(TeamState)
    
    # Add nodes
    workflow.add_node("pm", pm_node)
    workflow.add_node("backend", backend_node)
    workflow.add_node("frontend", frontend_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("qa_tester", qa_tester_node)
    
    # Add edges (workflow sequence)
    workflow.set_entry_point("pm")
    workflow.add_edge("pm", "backend")
    workflow.add_edge("backend", "frontend")
    workflow.add_edge("frontend", "reviewer")
    workflow.add_edge("reviewer", "qa_tester")
    
    # Conditional edge: qa_tester → continue (back to PM) or end
    workflow.add_conditional_edges(
        "qa_tester",
        should_continue,
        {
            "continue": "pm",
            "end": END
        }
    )
    
    return workflow.compile()


# Extensibility: To add new agents:
# 1. Define agent_node function following the pattern above
# 2. Add node to workflow: workflow.add_node("agent_name", agent_node)
# 3. Add edges to connect agent in sequence
# 4. Update TeamState if agent needs new fields
# 5. Create prompt file in prompts/system/<agent_name>.md
