# LangTeam: Multi-Agent Agile Software Team

A multi-agent system built with LangGraph that simulates an agile software development team. Supports hybrid LLM deployment (OpenAI for tools, Ollama for text).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (choose one approach):

# Option A: Hybrid (OpenAI for tools, Ollama for text) - Recommended
cp .env.example .env
# Edit .env:
#   LLM_PROVIDER_TOOLS=openai
#   LLM_MODEL_TOOLS=gpt-4o-mini
#   LLM_PROVIDER_TEXT=ollama
#   LLM_MODEL_TEXT=llama3.2:latest
#   OPENAI_API_KEY=sk-...

# Option B: All OpenAI (simplest, most reliable)
# Edit .env:
#   LLM_PROVIDER=openai
#   LLM_MODEL=gpt-4o-mini
#   OPENAI_API_KEY=sk-...

# Option C: All Local (free, requires tool-capable model)
# Edit .env:
#   LLM_PROVIDER=ollama
#   LLM_MODEL=llama3.2:latest

# 3. Run
python -m src.run_team "Build a todo app"
```

Projects are created in `./projects/<name>-<timestamp>/` with isolated directories.

## Key Features

✅ **Real file creation** - Agents use `write_file()` to create actual code
✅ **Project isolation** - Each project in timestamped subdirectory
✅ **Hybrid LLMs** - OpenAI for tools, local models for text (cost optimization)
✅ **Learning system** - Remembers patterns and improves over time
✅ **Safety** - Sandboxed execution, blocked patterns, path traversal protection

## Architecture

### Agents
- **PM**: Creates SPEC, breaks down tasks
- **Backend**: Implements architecture, creates files
- **Frontend**: Builds UI, wires components
- **Reviewer**: Enforces Definition of Done, approves or requests changes

### Workflow
```
User Goal → PM → Backend → Frontend → Reviewer → [APPROVED or loop]
```

### Tools Available to Agents
- `write_file(path, content)` - **Create actual source files** (agents MUST use this!)
- `read_file(path)` - Read files
- `list_files(dir)` - List directory
- `shell(cmd)` - Execute commands in project directory
- `http_get/post(url)` - API calls
- `git(message)` - Commit changes

**Important**: Agents create files using `write_file()` in `src/` directory, not by describing code.

## Configuration

### Hybrid Setup (Recommended)
```bash
# .env
LLM_PROVIDER_TOOLS=openai      # Backend/Frontend use OpenAI (reliable tools)
LLM_MODEL_TOOLS=gpt-4o-mini
LLM_PROVIDER_TEXT=ollama        # PM/Reviewer use local (free text gen)
LLM_MODEL_TEXT=llama3.2:latest
OPENAI_API_KEY=sk-...
PROJECTS_ROOT=./projects
MAX_TURNS=10
```

### Key Settings
- `PROJECTS_ROOT` - Where projects are created (default: ./projects)
- `MAX_TURNS` - Iteration limit (default: 10)
- `MAX_SHELL_CMDS_PER_TURN` - Command safety limit (default: 5)
- `LEARNING_ENABLED` - Enable memory/learning (default: true)

Central configuration that reads from environment variables:
- LLM provider and model selection
- Turn and command limits
- Tool toggles (allow_shell, allow_http, allow_git, allow_fs, allow_mcp)
- HTTP timeout settings
- Learning and memory configuration

### MCP Servers (config/mcp_servers.json)

Configure external tool integrations:
```json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "root": "."
    }
  ]
}
```

Add additional servers for expanded capabilities:
- Jira integration for ticket management
- GitHub API for repository operations
- Browser automation for UI testing
- Database tools for data operations

## Memory and Learning System

LangTeam includes a sophisticated memory system that enables the team to learn from past experiences:

### Features
- **Persistent Memory**: SQLite database stores all interactions, decisions, and outcomes
- **Mistake Tracking**: Automatically captures failed attempts and their resolutions
- **Pattern Recognition**: Identifies recurring issues and suggests preventive measures
- **Context Retrieval**: Pulls relevant past experiences for current tasks
- **Success Metrics**: Tracks approval rates, iteration counts, and improvement trends
- **Knowledge Base**: Builds a searchable repository of solutions and approaches

### Memory Types
1. **Episodic Memory**: Complete conversation histories and decision trails
2. **Semantic Memory**: Extracted patterns, best practices, and anti-patterns
3. **Procedural Memory**: Successful workflows and solution templates
4. **Error Memory**: Failed approaches with root causes and fixes

### Learning Capabilities
- Analyzes review feedback to improve future iterations
- Remembers which architectures work well for specific problem types
- Learns from debugging sessions to avoid similar issues
- Adapts communication patterns based on effectiveness
- Builds domain knowledge over time

## Quick Start

See [BOOTSTRAP.md](BOOTSTRAP.md) for detailed installation and setup instructions.

**Quick summary:**
1. Install Python 3.11+, Ollama
2. Pull Code Llama: `ollama pull codellama:latest`
3. Create virtual environment and install dependencies
4. Copy `.env.example` to `.env`
5. Run: `python -m src.run_team "Build a TODO app"`

## Safety and Guardrails

### Shell Safety
- Commands restricted to `./sandbox` directory by default
- Blocked patterns: `rm -rf`, `sudo`, `chmod -R`, system modifications
- Per-turn command limits enforced
- Runtime caps prevent infinite loops

### Secret Protection
- Tokens and keys automatically redacted in logs
- No full secret printing in reports
- Environment-based credential management

### Approval Loop
- Reviewer enforces Definition of Done
- Explicit approval required before completion
- Turn limits prevent infinite iterations
- Clear change requests when work needs revision

### Confirmation Protocol
- Irreversible actions require explicit user confirmation
- Destructive operations clearly flagged
- Audit trail of all agent actions

## Extensibility

### Adding New LLM Providers
1. Update `src/llm.py` with new provider logic
2. Add required client library to `requirements.txt`
3. Update `.env.example` with provider-specific variables
4. Test with simple query before full integration

### Adding New Tools
1. Implement tool function in `src/tools.py`
2. Add safety guardrails and validation
3. Document in README and system prompts
4. Update agent bindings in `src/graph.py`
5. Test in isolation before team integration

### Expanding MCP Integration
1. Add server configuration to `config/mcp_servers.json`
2. Implement transport handler in `src/mcp_bridge.py`
3. Map server operations to LangChain tools
4. Update agent prompts with new capabilities
5. Document usage in README

### Adding New Agents
1. Create system prompt in `prompts/system/<agent>.md`
2. Define node function in `src/graph.py`
3. Update state type with agent-specific fields
4. Wire into graph edges and routing logic
5. Update tests to cover new agent paths

### Customizing Memory
1. Extend `src/memory.py` with new storage backends
2. Add custom embedding models for semantic search
3. Implement domain-specific memory indexes
4. Configure retention policies and cleanup
5. Export/import capabilities for knowledge transfer

## Project Structure

```
langteam/
├── config/              # Configuration files
│   ├── settings.yaml    # Central settings (reads from env)
│   └── mcp_servers.json # MCP server definitions
├── prompts/             # Agent behavior definitions
│   ├── system/          # Agent personas and goals
│   └── policies/        # Safety, DoD, guidelines
├── src/                 # Source code
│   ├── llm.py          # LLM provider abstraction
│   ├── tools.py        # Agent tool implementations
│   ├── mcp_bridge.py   # MCP server integration
│   ├── memory.py       # Learning and memory system
│   ├── roles.py        # Prompt loading utilities
│   ├── graph.py        # LangGraph state machine
│   └── run_team.py     # CLI entrypoint
├── tests/              # Test suite
├── .env.example        # Environment template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

### Graph doesn't complete
- Increase `MAX_TURNS` in `.env`
- Check reviewer prompts for clarity
- Verify acceptance criteria are testable

### Shell commands fail
- Ensure `./sandbox` directory exists
- Check command patterns against blocked list
- Verify per-turn limit not exceeded

### HTTP requests timeout
- Increase `HTTP_TIMEOUT_SECONDS`
- Check network connectivity and firewall
- Verify target URLs are accessible

### Model responses are poor
- Lower temperature for more deterministic output
- Switch to larger/better model
- Refine system prompts for clarity
- Check if model is appropriate for task

### Memory not persisting
- Verify `LEARNING_ENABLED=true` in `.env`
- Check write permissions for `MEMORY_DB_PATH`
- Ensure SQLite is properly installed
- Review memory.py logs for errors

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Follow existing code style and structure
2. Add tests for new features
3. Update documentation
4. Ensure safety guardrails are maintained
5. Test with default Code Llama model

## Support

For issues, questions, or contributions:
- File issues on GitHub repository
- Check BOOTSTRAP.md for common setup problems
- Review system prompts for agent behavior
- Consult memory database for historical solutions
