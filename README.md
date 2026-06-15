# Claude Code Commands

This repository implements a GitHub Actions workflow to automate issue management using Claude Code.

## Available Issue Commands

Comment on any Issue (team members only) with the following commands:

- `/triage`: Analyzes the issue context and suggests next steps or missing info.
- `/reprex`: Attempts to reproduce the issue on a GitHub runner Linux environment.
- `/issue-fix`: Automatically writes a fix, runs tests, and creates a Pull Request.
- `/duplicate`: Searches for duplicate or similar issues.

The commands are handled by `.github/workflows/commands.yml`. Report-only commands run with read-only repository access plus issue commenting permissions; `/issue-fix` is the only command with repository and pull request write permissions.

## Demo Code

A demonstration module with a bug is located in [math_utils.py](math_utils.py), tested by [tests/test_math_utils.py](tests/test_math_utils.py).
