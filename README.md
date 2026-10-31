# super-productivity-skill

English | [简体中文](README.zh-CN.md)

An [Agent Skill](https://agentskills.io) that lets AI coding agents — Claude Code, Codex, OpenCode, and any other agent
that can run shell commands — read and manage your [Super Productivity](https://super-productivity.com/) tasks through
the app's **built-in local REST API**: list projects and tasks, add todos (project, planned day, deadline, estimate,
subtasks), mark them done, edit them, start time tracking.

No MCP server or plugin to install, and it never touches the app's database files.

```
You:   Add "Run baseline experiments" to my Research project, deadline Friday, estimate 2h
Agent: created t4uSMIIo…  Run baseline experiments  [Research]  deadline 2026-11-06
```

The task shows up in the running app immediately.

## Requirements

- Super Productivity **desktop app, v19 or newer** (macOS, Windows or Linux — the REST API is desktop only)
- Python 3 (standard library only)
- The REST API switched on: **Settings → Misc → "Enable local REST API (desktop only)"**. When the status below it
  reads `Running at http://127.0.0.1:3876`, you're set.

You do **not** need "Enable assistant access (MCP)" — that only allows adding tasks to the Inbox.

## Install

The repo folder must be named `super-productivity` (it has to match the skill's `name`).

**Claude Code**

```bash
git clone https://github.com/chu-jiaming/super-productivity-skill ~/.claude/skills/super-productivity
```

**Codex, OpenCode and other agents that follow the Agent Skills spec** (shared user-level folder)

```bash
git clone https://github.com/chu-jiaming/super-productivity-skill ~/.agents/skills/super-productivity
```

OpenCode also reads `~/.config/opencode/skills/` and `~/.claude/skills/`. To use one checkout from several agents,
clone it once and symlink it into the other folders. For a single project instead of your whole account, use
`.claude/skills/` or `.agents/skills/` inside the project.

**Agents without skill support** (Cursor rules, Copilot instructions, `AGENTS.md`, …)

Clone anywhere and add a line like this to the agent's instructions file:

```markdown
To read or change my Super Productivity tasks, run `python3 /path/to/super-productivity-skill/scripts/sp.py`.
Follow /path/to/super-productivity-skill/SKILL.md for usage and workflow.
```

Then ask your agent something like "what's on my list today?" or "add X to project Y, due Friday".

## The helper script

`scripts/sp.py` is a small CLI the agent calls; you can also use it directly:

```bash
python3 scripts/sp.py health
python3 scripts/sp.py projects
python3 scripts/sp.py tasks --project research --today
python3 scripts/sp.py add "Read the COLMAP paper" --project research --due 2026-11-06 --estimate 1h30m
python3 scripts/sp.py done <TASK_ID>
```

| Command | What it does |
|---|---|
| `health` | Check the API is running |
| `projects` / `tags` | List ids and titles |
| `tasks [--project X] [--today] [--query TXT] [--include-done] [--source active\|archived\|all] [--json]` | List tasks (undone only by default) |
| `add "Title" [--project X] [--due YYYY-MM-DD] [--deadline YYYY-MM-DD] [--estimate 1h30m] [--notes TXT] [--today] [--parent ID]` | Create a task; `--parent` creates a subtask |
| `done ID` | Mark complete |
| `update ID '{"title":"..."}'` | Change any writable field |
| `raw METHOD /path ['{json}']` | Call any endpoint directly |

`--project` takes a project id or any unique, case-insensitive part of its title. Leave it out to use the Inbox.

### Where the token comes from

The script reads `local-rest-api-token` from the app's data folder:

| Platform | Data folder |
|---|---|
| macOS | `~/Library/Application Support/superProductivity` |
| Windows | `%APPDATA%\superProductivity` |
| Linux | `~/.config/superProductivity` (also checks the Snap and Flatpak locations) |

If yours lives elsewhere, set one of these environment variables:

| Variable | Purpose |
|---|---|
| `SP_TOKEN_FILE` | Path to the token file |
| `SP_API_TOKEN` | The token itself |
| `SP_API_URL` | Base URL (default `http://127.0.0.1:3876`) |

## Security

- The API listens on `127.0.0.1` only, and every request needs the token.
- The token is read at run time. It is never written into this repo or into the agent's conversation.
- While the API is on, any program running as you on that computer can read and change your tasks. Turn the switch off
  when you don't need it, and use **Regenerate Access Token** if you think the token was exposed.
- The skill never edits IndexedDB or backup files. For read-only questions while the API is off, it may read the
  app's automatic JSON backups (which can be a few minutes old).

## Contributing

Issues and PRs are welcome — especially confirmation of the token paths on Windows and Linux, and support for other
agents.

## License

[MIT](LICENSE)
