# LangTeam Bootstrap Guide

Complete step-by-step instructions to get LangTeam running on your system.

## Prerequisites

Before starting, ensure you have:
- **Python 3.11 or higher** installed
- **Git** installed and configured
- **Internet connection** for downloading dependencies and models
- **5GB+ disk space** for models and dependencies
- **8GB+ RAM** recommended for local model execution

## Step 1: Install Ollama

Ollama provides local LLM hosting for cost-effective execution.

### Windows
Download and run the installer from: https://ollama.ai/download

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

After installation, verify Ollama is running:
```bash
ollama --version
```

## Step 2: Pull Code Llama Model

Download the Code Llama model for code generation:

```bash
ollama pull codellama:latest
```

This downloads approximately 3.8GB. For faster/lighter alternatives:
- `codellama:7b` - Smaller, faster (3.8GB)
- `codellama:13b` - Balanced (7.3GB)
- `codellama:34b` - Larger, more capable (19GB)

Verify the model is available:
```bash
ollama list
```

## Step 3: Clone or Navigate to Repository

If you haven't already:
```bash
cd c:\Users\minaa\Documents\Projects\todo-app
```

## Step 4: Create Python Virtual Environment

### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt when activated.

## Step 5: Install Dependencies

With your virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- LangChain and LangGraph for agent orchestration
- Ollama client for model interaction
- Rich and tqdm for beautiful console output
- Requests for HTTP tools
- Pydantic for data validation
- Python-dotenv for environment management
- SQLite (included with Python) for memory storage

Installation takes 2-5 minutes depending on your connection.

## Step 6: Configure Environment

Copy the example environment file:

### Windows
```cmd
copy .env.example .env
```

### macOS/Linux
```bash
cp .env.example .env
```

The default `.env` values work out-of-box with Ollama and Code Llama:

```env
LLM_PROVIDER=ollama
LLM_MODEL=codellama:latest
MAX_TURNS=10
MAX_SHELL_CMDS_PER_TURN=5
HTTP_TIMEOUT_SECONDS=30
LEARNING_ENABLED=true
MEMORY_DB_PATH=./memory.db
```

**Optional customizations:**
- Increase `MAX_TURNS` for more complex projects (try 15-20)
- Lower `MAX_SHELL_CMDS_PER_TURN` for stricter safety (try 3)
- Enable other providers by setting API keys

## Step 7: Create Sandbox Directory

The shell tool requires a sandbox directory for safe command execution:

### Windows
```cmd
mkdir sandbox
```

### macOS/Linux
```bash
mkdir -p sandbox
```

## Step 8: Run Your First Team Session

Start the agile team with a simple task:

```bash
python -m src.run_team "Build a simple TODO app with CLI interface"
```

### What to Expect

The console will show:
1. **Initialization**: Loading configuration and models
2. **PM Phase**: Product manager creates SPEC with acceptance criteria
3. **Backend Phase**: Staff engineer designs and implements backend
4. **Frontend Phase**: Staff engineer builds interface
5. **Review Phase**: Code reviewer checks against Definition of Done
6. **Iteration**: Loop continues until approved or MAX_TURNS reached

### Example Output Sections

```
=== SPEC ===
Generated specification with numbered acceptance criteria

=== BACKEND NOTES ===
Architecture decisions, implementation details, commands to reproduce

=== FRONTEND NOTES ===
UI/UX approach, integration points, usage instructions

=== REVIEW NOTES ===
Code review feedback, change requests, or APPROVED status

=== APPROVALS ===
List of reviewers who approved (if any)

=== STATISTICS ===
Total turns: X
Execution time: Y seconds
Memory entries: Z
```

## Step 9: Sanity Check

### Successful Run Indicators

✅ **SPEC section appears** with numbered acceptance criteria
✅ **Backend and Frontend notes** show implementation work
✅ **Review notes** contain either "APPROVED" or specific change requests
✅ **Turn count** is displayed (should be ≤ MAX_TURNS)
✅ **No Python exceptions** or error tracebacks
✅ **Memory database created** at `./memory.db` (if learning enabled)

### Expected First Run

First runs typically take 5-10 turns:
- Turn 1-2: PM gathers requirements and creates SPEC
- Turn 3-5: Backend implements core logic
- Turn 6-8: Frontend adds interface
- Turn 9-10: Review and approval (or change requests)

## Troubleshooting

### Issue: "Model not found" or Ollama connection error

**Solution:**
1. Verify Ollama is running: `ollama list`
2. Re-pull the model: `ollama pull codellama:latest`
3. Check Ollama service: `ollama serve` (should already be running)
4. Verify model name in `.env` matches `ollama list` output

### Issue: Graph runs but hits MAX_TURNS without approval

**Solution:**
1. Increase `MAX_TURNS=15` in `.env`
2. Check `prompts/policies/definition_of_done.md` - ensure criteria are clear
3. Review `prompts/system/reviewer.md` - reviewer should look for testable completion
4. Try a simpler initial task to verify setup

### Issue: Shell commands are blocked

**Solution:**
1. Verify `./sandbox` directory exists
2. Check blocked patterns in `src/tools.py`
3. Review error message for specific pattern that triggered block
4. Ensure command operates only within sandbox

### Issue: HTTP requests fail or timeout

**Solution:**
1. Check internet connectivity
2. Increase `HTTP_TIMEOUT_SECONDS=60` in `.env`
3. Verify no firewall blocking Python
4. Test URL directly in browser first
5. Check proxy settings if behind corporate firewall

### Issue: Poor quality responses or hallucinations

**Solution:**
1. Lower temperature in `src/llm.py` (try 0.1 for more deterministic)
2. Switch to larger model: `ollama pull codellama:13b`, update `.env`
3. Refine system prompts to be more specific
4. Add more examples to prompts
5. Check memory database for conflicting past learnings

### Issue: Memory database errors

**Solution:**
1. Check write permissions for `MEMORY_DB_PATH` directory
2. Delete existing `memory.db` to reset (backup first!)
3. Set `LEARNING_ENABLED=false` to disable temporarily
4. Check disk space availability
5. Review `src/memory.py` logs for specific SQLite errors

### Issue: Slow execution

**Solution:**
1. Use smaller model: `codellama:7b`
2. Reduce `MAX_TURNS` for faster iteration
3. Close other applications to free RAM
4. Consider GPU acceleration if available
5. Check if Ollama is using CPU vs GPU (`nvidia-smi` on Linux/Windows)

### Issue: Import errors or missing modules

**Solution:**
1. Verify virtual environment is activated (see `(venv)` in prompt)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check Python version: `python --version` (must be 3.11+)
4. Try upgrading pip: `pip install --upgrade pip`

## Advanced Configuration

### Using Alternative Models

#### Together AI (cloud)
1. Get API key from https://together.ai
2. Update `.env`:
   ```
   LLM_PROVIDER=together
   LLM_MODEL=codellama/CodeLlama-34b-Instruct-hf
   TOGETHER_API_KEY=your_key_here
   ```
3. Install client: `pip install together`

#### Hugging Face (cloud)
1. Get token from https://huggingface.co
2. Update `.env`:
   ```
   LLM_PROVIDER=hf
   LLM_MODEL=codellama/CodeLlama-7b-hf
   HF_API_TOKEN=your_token_here
   ```
3. Install client: `pip install huggingface_hub`

### Adjusting Safety Limits

Edit `.env` for stricter or more permissive behavior:

**Stricter (for sensitive environments):**
```env
MAX_TURNS=5
MAX_SHELL_CMDS_PER_TURN=2
HTTP_TIMEOUT_SECONDS=15
```

**More Permissive (for complex projects):**
```env
MAX_TURNS=20
MAX_SHELL_CMDS_PER_TURN=10
HTTP_TIMEOUT_SECONDS=60
```

### Enabling Debug Logging

For detailed execution traces, set environment variable:

### Windows
```cmd
set LANGCHAIN_DEBUG=1
```

### macOS/Linux
```bash
export LANGCHAIN_DEBUG=1
```

## Next Steps

1. **Try different tasks**: Experiment with various project types
2. **Customize prompts**: Edit files in `prompts/` to tune behavior
3. **Add MCP servers**: Extend `config/mcp_servers.json` for new integrations
4. **Explore memory**: Query `memory.db` to see what the team has learned
5. **Monitor iterations**: Track which tasks approve quickly vs need many turns
6. **Build knowledge base**: Let the system learn from multiple projects

## Getting Help

If you encounter issues not covered here:
1. Check `README.md` for detailed feature documentation
2. Review system prompts in `prompts/system/` for agent behavior
3. Inspect memory database for past similar errors
4. Enable debug logging for detailed trace
5. File an issue with full error message and environment details

## Sanity Check Summary

A properly configured LangTeam should:
- ✅ Start without import errors
- ✅ Connect to Ollama successfully
- ✅ Generate a SPEC with numbered criteria
- ✅ Show backend and frontend implementation notes
- ✅ Produce review feedback
- ✅ Complete within MAX_TURNS or approve
- ✅ Create memory database entries
- ✅ Display turn count and statistics

If all checks pass, you're ready to build with your AI agile team! 🚀
