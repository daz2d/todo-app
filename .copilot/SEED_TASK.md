# LangTeam Build Validation Checklist

This checklist ensures the LangTeam repository is correctly built according to the specification.

## File Creation

- [ ] All root configuration files created
  - [ ] README.md with comprehensive documentation
  - [ ] BOOTSTRAP.md with step-by-step setup instructions
  - [ ] pyproject.toml with minimal project metadata
  - [ ] requirements.txt with all dependencies
  - [ ] .env.example with all configuration variables
  - [ ] .gitignore with appropriate exclusions

- [ ] Configuration directory (`config/`)
  - [ ] settings.yaml with environment binding
  - [ ] mcp_servers.json with filesystem server default

- [ ] Prompts directory (`prompts/`)
  - [ ] policies/safety.md with shell and security guardrails
  - [ ] policies/dos_and_donts.md with team norms
  - [ ] policies/definition_of_done.md with clear DoD criteria
  - [ ] system/pm.md with Product Manager persona and protocol
  - [ ] system/staff_backend.md with Backend Engineer persona
  - [ ] system/staff_frontend.md with Frontend Engineer persona
  - [ ] system/reviewer.md with Code Reviewer persona and approval protocol

- [ ] Source directory (`src/`)
  - [ ] __init__.py as package initializer
  - [ ] llm.py with provider abstraction and model selection
  - [ ] tools.py with HTTP, shell, and git tools plus safety checks
  - [ ] mcp_bridge.py with discovery and extensibility stub
  - [ ] memory.py with learning and persistent memory system
  - [ ] roles.py with prompt loading utilities
  - [ ] graph.py with TeamState, nodes, edges, and termination logic
  - [ ] run_team.py as CLI entrypoint

- [ ] Tests directory (`tests/`)
  - [ ] test_boot.py verifying imports and wiring
  - [ ] test_graph.py verifying single iteration execution

## Git Initialization

- [ ] Git repository initialized
- [ ] All files added to staging
- [ ] Initial commit created with descriptive message

## Dependency Installation

- [ ] requirements.txt dependencies install without conflicts
- [ ] All required packages present:
  - [ ] langchain
  - [ ] langgraph
  - [ ] langchain-community
  - [ ] python-dotenv
  - [ ] pydantic
  - [ ] requests
  - [ ] tqdm
  - [ ] rich
  - [ ] ollama
  - [ ] websocket-client
  - [ ] pyyaml

## Configuration Validation

- [ ] .env.example has default model configured (codellama via Ollama)
- [ ] LLM_PROVIDER defaults to "ollama"
- [ ] LLM_MODEL defaults to "codellama:latest"
- [ ] MAX_TURNS has reasonable default (10)
- [ ] MAX_SHELL_CMDS_PER_TURN has safety limit (5)
- [ ] HTTP_TIMEOUT_SECONDS has reasonable default (30)
- [ ] LEARNING_ENABLED defaults to true
- [ ] MEMORY_DB_PATH specified (./memory.db)

## End-to-End Execution

- [ ] Entrypoint can be invoked: `python -m src.run_team "demo a TODO app"`
- [ ] Graph completes without Python exceptions
- [ ] Console output includes all expected sections:
  - [ ] SPEC section with numbered acceptance criteria
  - [ ] BACKEND NOTES section with implementation details
  - [ ] FRONTEND NOTES section with UI/SDK approach
  - [ ] REVIEW NOTES section with feedback or "APPROVED"
  - [ ] APPROVALS section (list, may be empty or contain reviewer)
  - [ ] STATISTICS section with turn count and metrics
- [ ] Memory database created at specified path
- [ ] Turn count displayed is ≤ MAX_TURNS

## Safety Validation

- [ ] Shell tool restricts commands to ./sandbox directory
- [ ] Dangerous patterns (rm -rf, sudo, etc.) are blocked
- [ ] Per-turn shell command limit is enforced
- [ ] HTTP requests use configured timeout
- [ ] Secrets are redacted in logs (if any credentials present)

## Documentation Completeness

- [ ] README.md explains:
  - [ ] Purpose and architecture overview
  - [ ] All four agent roles and responsibilities
  - [ ] Available tools with safety notes
  - [ ] Configuration options (env vars, YAML, JSON)
  - [ ] Memory and learning capabilities
  - [ ] Quick start summary referencing BOOTSTRAP.md
  - [ ] Safety and guardrails section
  - [ ] Extensibility instructions for models, tools, MCP, agents

- [ ] BOOTSTRAP.md includes:
  - [ ] Prerequisites (Python 3.11+, Git, Ollama)
  - [ ] Ollama installation instructions
  - [ ] Model pull command: `ollama pull codellama:latest`
  - [ ] Virtual environment creation and activation
  - [ ] Dependency installation from requirements.txt
  - [ ] .env file setup from .env.example
  - [ ] Sandbox directory creation
  - [ ] Example run command with trivial goal
  - [ ] "Sanity Check" section describing expected console output
  - [ ] Troubleshooting section with common issues and solutions

## Behavioral Acceptance Criteria

- [ ] A) Running entrypoint produces:
  - [ ] Generated SPEC with numbered acceptance criteria
  - [ ] Backend notes describing proposed/implemented slices and next steps
  - [ ] Frontend notes describing UI/SDK work and next steps
  - [ ] Reviewer notes with "APPROVED" or explicit change requests
  - [ ] Approvals list (array, empty or containing reviewer)
  - [ ] Turn count integer

- [ ] B) Safety mechanisms:
  - [ ] Shell commands restricted to ./sandbox by default
  - [ ] Disallowed patterns yield "blocked" message
  - [ ] Per-turn shell command cap enforced and configurable
  - [ ] HTTP requests use timeout from env
  - [ ] Secrets redacted in logs/reports

- [ ] C) Configurability:
  - [ ] Switching model/provider requires only .env edit
  - [ ] MAX_TURNS adjustable via .env
  - [ ] Per-turn shell cap adjustable via .env
  - [ ] Adding MCP servers requires only config/mcp_servers.json edit

- [ ] D) Developer Experience:
  - [ ] README and BOOTSTRAP provide clear zero-to-first-run path
  - [ ] Tests execute in fresh environment
  - [ ] Tests complete quickly (under 60 seconds)
  - [ ] All files present with correct names and locations

## Extensibility Features

- [ ] Memory system implemented:
  - [ ] SQLite database for persistent storage
  - [ ] Episodic memory (conversation histories)
  - [ ] Semantic memory (patterns and best practices)
  - [ ] Procedural memory (successful workflows)
  - [ ] Error memory (failed approaches with fixes)

- [ ] Learning capabilities:
  - [ ] Analyzes review feedback
  - [ ] Remembers successful architectures
  - [ ] Learns from debugging sessions
  - [ ] Builds domain knowledge over time
  - [ ] Context retrieval from past experiences

- [ ] Easy extensibility paths documented:
  - [ ] Adding new LLM providers
  - [ ] Adding new tools
  - [ ] Expanding MCP integration
  - [ ] Adding new agents
  - [ ] Customizing memory system

## Final Validation

- [ ] Run test suite: all tests pass
- [ ] No outstanding TODOs in critical paths (memory and graph logic complete)
- [ ] Code follows consistent style (readable, documented)
- [ ] No hardcoded secrets or credentials
- [ ] Default configuration works out-of-box with Ollama

## Success Criteria

✅ All checklist items complete
✅ System runs end-to-end with default configuration
✅ Memory database persists and retrieves context
✅ Agents learn from mistakes across sessions
✅ Documentation enables new users to get started in under 10 minutes
✅ Safety guardrails prevent dangerous operations
✅ Extensibility points are clear and documented

---

**Note to Copilot Agent Mode**: Follow this checklist to validate that all components of the LangTeam system have been correctly implemented according to the specification. Ensure each item is addressed before marking the build as complete.
