# Claude Code Commands

A reusable GitHub Actions workflow that adds AI-powered slash commands to your issue tracker. Comment `/triage`, `/reprex`, `/duplicate`, or `/issue-fix` on any issue and Claude handles it.

## Available Commands

Comment on any issue (team members only):

| Command | What it does | Permissions |
|---|---|---|
| `/triage` | Analyzes the issue, reads the codebase, suggests labels and next steps | Read-only |
| `/reprex` | Attempts to reproduce the issue on a Linux runner | Read-only |
| `/duplicate` | Searches for duplicate or similar issues | Read-only |
| `/issue-fix` | Writes a fix, runs tests, and creates a Pull Request | Write |

You can also pass extra instructions after the command:

```
/triage focus on the authentication flow
/issue-fix only modify files in src/auth/
```

## Installation (for other repos)

### 1. Install the Claude GitHub App

Install it on your repository: https://github.com/apps/claude

### 2. Add a secret

Add **one** of these to your repo's Settings → Secrets → Actions:

| Secret | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code subscription |

### 3. Copy the caller workflow

Copy [`examples/caller.yml`](examples/caller.yml) to your repo at `.github/workflows/claude-commands.yml`.

Edit the file:
- Replace `your-org/claude-code-commands` with the actual owner/repo that hosts this reusable workflow.
- Uncomment the secret you're using in each job's `secrets:` block.

### 4. Tag the reusable workflow repo

The reusable workflow is pinned to `@v1`. Make sure the host repo has a `v1` tag pointing to a stable release.

## How secrets work

This workflow does **not** use `secrets: inherit`. The reusable workflow's repo secrets are never exposed to your workflow runs. You must add your own `ANTHROPIC_API_KEY` (or `CLAUDE_CODE_OAUTH_TOKEN`) in your repo's settings.

## Optional: GitHub App for CI triggers

If you want Claude's commits to trigger your CI workflows (the default `GITHUB_TOKEN` cannot trigger downstream workflows), create a GitHub App, install it on your repo, and add `APP_ID` + `APP_PRIVATE_KEY` to your secrets. Then uncomment the `app_id` / `app_private_key` lines in each job.

## Customization

The caller workflow passes these inputs to the reusable workflow:

| Input | Default | Description |
|---|---|---|
| `command` | (required) | `triage`, `reprex`, `duplicate`, or `issue-fix` |
| `issue_number` | (required) | Issue number to act on |
| `comment_id` | (optional) | Comment ID to react to |
| `prompt_suffix` | `""` | Extra text from the user appended to the prompt |
| `model` | `claude-sonnet-4-6` | Claude model to use |
| `max_turns` | 25 or 40 | Max conversation turns (per-command default) |
| `runner` | `ubuntu-latest` | GitHub Actions runner label |

To customize, pass overrides in the caller's `with:` block:

```yaml
uses: your-org/claude-code-commands/.github/workflows/commands.yml@v1
with:
  command: triage
  issue_number: ${{ fromJSON(needs.parse.outputs.issue_number) }}
  model: claude-sonnet-4-5
  max_turns: 50
```

## Repo structure

```
.github/workflows/
  commands.yml           ← reusable workflow (workflow_call)
  claude-commands.yml    ← internal caller for this repo's demo
examples/
  caller.yml             ← copy this to your repo
math_utils.py            ← demo code with a bug
tests/
  test_math_utils.py     ← demo tests
```

## Demo

This repo includes a demo module (`math_utils.py`) with a known bug, tested by `tests/test_math_utils.py`. Open an issue describing the bug, then comment `/issue-fix` to see Claude fix it and open a PR.
