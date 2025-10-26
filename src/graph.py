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


# Configuration
MAX_TURNS = int(os.getenv('MAX_TURNS', '10'))


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
    print(f"\n{'='*60}\n  PM (Turn {state['turns'] + 1})\n{'='*60}")
    
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
    print(f"\n{'='*60}\n  BACKEND ENGINEER (Turn {state['turns']})\n{'='*60}")
    
    # VALIDATION: Ensure SPEC exists before proceeding
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("❌ ERROR: No valid SPEC found!")
        print("Backend engineer cannot proceed without PM specification.")
        print("Requesting PM to create detailed SPEC first...")
        
        # Store error and request PM intervention
        error_msg = f"Backend engineer blocked: No SPEC available on turn {state['turns']}. PM must create specification before backend work can begin."
        state['backend_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"✓ SPEC validation passed ({len(state['spec'])} characters)")
    
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
🎯 PROJECT SPECIFICATION (THIS IS YOUR PRIMARY REQUIREMENT):
==========================================
{state['spec']}
==========================================

❗ CRITICAL: You must implement EXACTLY what is specified above. 
Do not build generic applications or assume different requirements.
Follow the acceptance criteria and tasks precisely.

PREVIOUS BACKEND WORK:
{state['backend_notes'] if state['backend_notes'] else '[No previous backend work]'}

FRONTEND WORK SO FAR:
{state['frontend_notes'] if state['frontend_notes'] else '[No frontend work yet]'}

REVIEW FEEDBACK:
{state['review_notes'] if state['review_notes'] else '[No review yet]'}

{past_context}

TURN: {state['turns']} of {MAX_TURNS}

Your task:
1. Review SPEC acceptance criteria
2. Design/implement backend slice for this turn
3. Use tools as needed (shell, git, http)
4. Document what you built and next steps

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
    print(f"\n{'='*60}\n  FRONTEND ENGINEER (Turn {state['turns']})\n{'='*60}")
    
    # VALIDATION: Ensure SPEC exists before proceeding
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("❌ ERROR: No valid SPEC found!")
        print("Frontend engineer cannot proceed without PM specification.")
        
        error_msg = f"Frontend engineer blocked: No SPEC available on turn {state['turns']}. PM must create specification before frontend work can begin."
        state['frontend_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"✓ SPEC validation passed ({len(state['spec'])} characters)")
    
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
🎯 PROJECT SPECIFICATION (THIS IS YOUR PRIMARY REQUIREMENT):
==========================================
{state['spec']}
==========================================

❗ CRITICAL: You must implement UI/UX EXACTLY for what is specified above. 
Do not build generic interfaces or assume different requirements.
Follow the acceptance criteria and tasks precisely.

BACKEND IMPLEMENTATION:
{state['backend_notes'] if state['backend_notes'] else '[No backend work yet]'}

PREVIOUS FRONTEND WORK:
{state['frontend_notes'] if state['frontend_notes'] else '[No previous frontend work]'}

REVIEW FEEDBACK:
{state['review_notes'] if state['review_notes'] else '[No review yet]'}

{past_context}

TURN: {state['turns']} of {MAX_TURNS}

Your task:
1. Review SPEC acceptance criteria for UI/UX requirements
2. Build frontend/interface slice for this turn
3. Wire with backend components
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
    print(f"\n{'='*60}\n  CODE REVIEWER (Turn {state['turns']})\n{'='*60}")
    
    # VALIDATION: Ensure SPEC exists for proper review
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("❌ ERROR: Cannot conduct proper review without detailed SPEC!")
        error_msg = f"Code reviewer cannot validate deliverables against requirements without PM specification. Turn {state['turns']}"
        state['review_notes'] = error_msg
        print(error_msg)
        return state
    
    print(f"✓ SPEC validation passed for review ({len(state['spec'])} characters)")
    
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
    print(f"\n{'='*60}\n  QA TESTER (Turn {state['turns']})\n{'='*60}")
    
    # VALIDATION: Ensure SPEC exists before testing
    if not state.get('spec') or len(state['spec'].strip()) < 20:
        print("❌ ERROR: No valid SPEC found!")
        print("QA Tester cannot create tests without PM specification.")
        
        error_msg = f"QA Tester blocked: No SPEC available on turn {state['turns']}. PM must create specification before testing can begin."
        state['qa_notes'] = error_msg
        state['test_results'] = "BLOCKED: No specification available"
        state['qa_approved'] = False
        print(error_msg)
        return state
    
    print(f"✓ SPEC validation passed ({len(state['spec'])} characters)")
    
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
        print("\n🎉 QA APPROVED - All tests passed!")
        approval_msg = f"QA Tester (Turn {state['turns']}): Tests pass, requirements verified"
        state['approvals'].append(approval_msg)
    else:
        print("\n⚠️ QA CONCERNS - Issues found in testing")
    
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
    # Require both code review approval AND QA approval
    if state['approved'] and state.get('qa_approved', False):
        print(f"\n✅ PROJECT FULLY APPROVED - Code Review ✓ and QA Testing ✓")
        return 'end'
    
    if state['turns'] >= MAX_TURNS:
        print(f"\n⚠️  MAX_TURNS ({MAX_TURNS}) reached without full approval")
        print(f"Code Review: {'✅' if state['approved'] else '❌'}")
        print(f"QA Testing: {'✅' if state.get('qa_approved', False) else '❌'}")
        return 'end'
    
    # Show current approval status
    if state['approved'] and not state.get('qa_approved', False):
        print(f"\n📋 Code Review ✅ approved, waiting for QA Testing...")
    elif not state['approved'] and state.get('qa_approved', False):
        print(f"\n📋 QA Testing ✅ approved, waiting for Code Review...")
    else:
        print(f"\n📋 Waiting for approvals - Code Review: ❌, QA Testing: ❌")
    
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
