# Claude Code Commands

This repository implements GitHub Action workflows to automate issue management using Claude Code.

## Available Issue Commands

Comment on any Issue (team members only) with the following commands:

- `/triage`: Analyzes the issue context and suggests next steps or missing info.
- `/reprex`: Attempts to reproduce the issue on a GitHub runner Linux environment.
- `/issue-fix`: Automatically writes a fix, runs tests, and creates a Pull Request.
- `/duplicate`: Searches for duplicate or similar issues.

## Demo Code

A demonstration module with a bug is located in [math_utils.py](math_utils.py), tested by [tests/test_math_utils.py](tests/test_math_utils.py).
