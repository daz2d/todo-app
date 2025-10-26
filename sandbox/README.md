# Sandbox Directory

This directory is used by the shell tool for safe command execution.

## Purpose

All shell commands executed by agents run within this directory by default. This provides:
- **Isolation**: Commands cannot affect system files outside this directory
- **Safety**: Prevents accidental deletion or modification of critical files
- **Cleanup**: Easy to reset by deleting and recreating this directory

## Usage

Agents can use the `shell()` tool to execute commands:
- `cd` is not needed - working directory is automatically set to sandbox
- File paths are relative to this directory
- Output files are created here

## Contents

This directory will contain:
- Agent-generated code files
- Test data and fixtures
- Build artifacts
- Temporary files

## Cleanup

To reset the sandbox:
```cmd
rmdir /s /q sandbox
mkdir sandbox
```

Or on macOS/Linux:
```bash
rm -rf sandbox
mkdir -p sandbox
```

## Note

This directory is in `.gitignore` - its contents are not tracked by git.
