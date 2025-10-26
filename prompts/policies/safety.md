# Safety Guardrails and Security Policy

## Shell Command Execution

### Sandbox Restriction
- **All shell commands MUST execute only within the `./sandbox` directory by default**
- Commands attempting to access parent directories (`..`), root (`/`), or system paths are **BLOCKED**
- Working directory is automatically set to `./sandbox` before any command execution
- No exceptions unless explicitly approved by user with confirmation

### Prohibited Patterns

The following command patterns are **STRICTLY FORBIDDEN** and will be blocked:

#### Destructive Operations
- `rm -rf` - Recursive forced deletion
- `mv /* ` - Moving root files
- `del /f /s /q` - Windows recursive deletion
- `format ` - Disk formatting
- `mkfs` - Filesystem creation
- `dd if=` - Low-level disk operations

#### Privilege Escalation
- `sudo ` - Superuser execution
- `su ` - Switch user
- `doas ` - Privilege escalation (OpenBSD)

#### Permission Manipulation
- `chmod -R` - Recursive permission changes
- `chmod 777` - Unsafe permission grants
- `chown -R` - Recursive ownership changes

#### System Manipulation
- `> /dev/` - Writing to device files
- `/dev/sda` - Direct disk access
- `systemctl` - System service control
- `service ` - Service management

#### Malicious Patterns
- `:(){ :|:& };:` - Fork bomb
- `curl | bash` - Arbitrary code execution from web
- `wget -O- | sh` - Arbitrary code execution from web
- `eval $(curl` - Code injection from web

### Per-Turn Command Limits

- Maximum commands per agent per turn: **Configurable via `MAX_SHELL_CMDS_PER_TURN`** (default: 5)
- Exceeding limit results in **BLOCK** with clear error message
- Counter resets at start of each agent turn
- Prevents runaway execution and resource exhaustion

### Runtime Constraints

- Maximum execution time per command: **30 seconds**
- Commands exceeding timeout are **TERMINATED** with error message
- Combined stdout/stderr captured (max 10KB per command)
- Exit codes preserved and reported

## HTTP Request Safety

### Timeout Enforcement
- All HTTP requests MUST respect `HTTP_TIMEOUT_SECONDS` (default: 30)
- Prevents hanging on unresponsive endpoints
- Timeout errors clearly reported to agent

### User-Agent Requirement
- All requests include user-agent: `LangTeam/1.0`
- Identifies traffic source for server administrators
- Enables blocking if necessary

### Response Size Limits
- JSON responses: Pretty-printed up to 50KB
- Text responses: Truncated at 50KB with indication
- Binary responses: Not supported, error returned

### Blocked Domains (Optional Extension Point)
- Add domain blacklist in future for enterprise deployments
- Currently no restrictions (trust agent reasoning)

## Secret Protection

### Automatic Redaction

The following patterns are **AUTOMATICALLY REDACTED** in all logs and output:

- `api_key`, `api-key`, `apikey` and their values
- `token`, `auth_token`, `access_token` and their values
- `password`, `passwd`, `pwd` and their values
- `secret`, `client_secret`, `api_secret` and their values
- `bearer ` followed by token string
- Any content matching `-----BEGIN * PRIVATE KEY-----`

### Redaction Format
- Sensitive values replaced with `[REDACTED]`
- Partial display for verification: First 4 characters + `***`
- Example: `sk-1234***` instead of `sk-1234567890abcdef`

### Environment Variable Protection
- `.env` file is in `.gitignore` by default
- Never print full `.env` content
- API keys loaded from environment, never hardcoded
- Git commits automatically scanned (future enhancement)

## Git Operations Safety

### Auto-Staging Constraints
- Only stages files within repository root
- Excludes `.env`, `memory.db`, and other gitignored files
- Verifies git repository exists before operation

### Commit Message Requirements
- Must be non-empty and descriptive
- Prefixed with `[LangTeam]` for traceability
- No sensitive information in commit messages

### Branch Protection
- Cannot force-push by default
- Cannot delete branches without confirmation
- Cannot modify remote branches directly

## Turn Limits

### Maximum Iterations
- Total PM → Backend → Frontend → Reviewer cycles: **Configurable via `MAX_TURNS`** (default: 10)
- Prevents infinite loops when consensus not reached
- Clear termination message when limit hit
- User can override with higher limit if needed

### Termination Conditions

**Normal Termination:**
- Reviewer includes "APPROVED" (case-insensitive) in review notes
- All acceptance criteria marked complete
- Definition of Done satisfied

**Forced Termination:**
- `MAX_TURNS` exceeded
- User interrupts (Ctrl+C)
- Unrecoverable error (model unavailable, etc.)

## User Confirmation Protocol

### Destructive Operations Requiring Confirmation

The following actions **MUST** receive explicit user approval before execution:

1. **Deleting files or directories** (even in sandbox)
2. **Overwriting existing files** with substantial content changes
3. **Making HTTP POST/PUT/DELETE requests** to production URLs
4. **Committing and pushing to remote repositories**
5. **Executing commands with `--force` or `--yes` flags**

### Confirmation Format
```
⚠️  CONFIRMATION REQUIRED ⚠️
Action: [Description of destructive operation]
Target: [What will be affected]
Impact: [Consequences of action]

Type 'yes' to proceed or 'no' to cancel:
```

### Timeout on Confirmation
- User has 60 seconds to respond
- Default action: **CANCEL** if no response
- Agent notified of cancellation and must adapt

## Incident Response

### Blocked Command Handling
- Clear message explaining why command was blocked
- Suggest safe alternative if available
- Example: "Blocked: `rm -rf /tmp`. Try: `rm file.txt` in sandbox."

### Rate Limiting (Future)
- Track failed/blocked attempts per session
- Escalate to admin if excessive (>10 blocks in 5 minutes)
- Temporarily disable tools if abuse detected

### Audit Trail
- All tool invocations logged with timestamp
- Blocked attempts logged with pattern matched
- User confirmations logged with decision
- Logs stored in `langteam.log` if `SAVE_LOGS=true`

## Memory and Learning Safety

### Database Security
- Memory database (`memory.db`) excluded from git
- No sensitive data stored in memory (secrets redacted first)
- Regular cleanup of old entries (configurable retention)

### Pattern Learning Constraints
- Never learn patterns that bypass safety guardrails
- Error memory includes only safe reproduction steps
- Procedural memory validated before reuse

## Responsibility

**Agents are responsible for:**
- Respecting all safety constraints without exception
- Asking for user confirmation when uncertain
- Reporting blocked attempts honestly
- Suggesting safe alternatives proactively

**Users are responsible for:**
- Reviewing confirmation requests carefully
- Setting appropriate limits in `.env`
- Monitoring logs for suspicious activity
- Keeping `.env` and memory.db secure

---

**Last Updated:** October 2025  
**Policy Version:** 1.0  
**Review Frequency:** Quarterly or after security incidents
