---
name: super-productivity
description: Read and manage the user's Super Productivity tasks (todo list) through the app's built-in local REST API — list projects/tasks, see today's list, add todos (with project, planned day, deadline, estimate, subtasks), mark done, edit. Use whenever the user mentions Super Productivity, SP, 待办/代办/todo/任务 they keep in it, or asks to add/check/complete tasks.
---

# Super Productivity (local REST API)

The desktop app (v19+, macOS/Windows/Linux) exposes a REST API at `http://127.0.0.1:3876`, only while the app is
running and **Settings → Misc → "Enable local REST API (desktop only)"** is on. The access token is stored in the app's
data folder as `local-rest-api-token`; the helper script finds it automatically. Never ask the user to paste the token
or echo it back. "Enable assistant access (MCP)" is NOT needed — it only allows adding to Inbox.

## Helper script (prefer this)

`scripts/sp.py` lives next to this file (Python 3, stdlib only). Run it by its path relative to this skill's
directory, e.g. `python3 <skill-dir>/scripts/sp.py health`. Use `python` instead of `python3` on Windows if needed.

| Command | What it does |
|---|---|
| `health` | Check the API is up |
| `projects` / `tags` | List ids + titles |
| `tasks [--project X] [--today] [--query TXT] [--include-done] [--source active\|archived\|all] [--json]` | List tasks (undone by default) |
| `add "Title" [--project X] [--due YYYY-MM-DD] [--deadline YYYY-MM-DD] [--estimate 1h30m] [--notes TXT] [--today] [--parent ID]` | Create a task; `--parent` makes a subtask (inherits project) |
| `done ID` | Mark complete |
| `update ID '{"title":"..."}'` | PATCH any writable field |
| `raw METHOD /path ['{json}']` | Anything else |

`--project` accepts an id or a unique, case-insensitive substring of the project title. Omit it to put the task in
Inbox.

If the token can't be found (unusual install location), the script lists the paths it tried; the user can set
`SP_TOKEN_FILE` (path to the token file) or `SP_API_TOKEN`. `SP_API_URL` overrides the base URL.

## Workflow

1. Run `sp.py health`. If it can't connect: tell the user to open Super Productivity and turn on the local REST API
   setting (and if the status says the port is in use, toggle it off/on). Do not edit the app's IndexedDB or backup
   files instead — the running app would overwrite or corrupt them.
2. If the request mentions projects, run `sp.py projects` once to map names to ids.
3. Turn relative dates ("Friday", "tomorrow", "周五") into `YYYY-MM-DD` using today's date. "deadline / due by / 截止"
   → `--deadline`; "do it on / plan for" → `--due`. If unclear, use `--due`.
4. Create each task, then report back a short list of what was created (title, project, date).
5. Before `done`, deleting, or bulk edits, list the matching tasks and confirm with the user if the match is not
   exact.

## Raw API reference

All requests need `Authorization: Bearer <token>`; responses are `{"ok": true, "data": ...}` or
`{"ok": false, "error": {...}}`.

- `GET /health`, `GET /status`, `GET /projects`, `GET /tags`
- `GET /tasks?query=&projectId=&tagId=&includeDone=true&source=active|archived|all` — `tagId=TODAY` = Today list
- `POST /tasks` — body: `title` (required) + optional `notes, isDone, timeEstimate(ms), timeSpent, projectId, tagIds,
  dueDay("YYYY-MM-DD"), dueWithTime(ms epoch), plannedAt, deadlineDay, deadlineWithTime, deadlineRemindAt, parentId`.
  Send `"isIgnoreShortSyntax": true` so `#tag`/`+project`/`@date` in titles aren't parsed. `deadlineDay` and
  `deadlineWithTime` are mutually exclusive. Subtasks: create parent first, then `POST /tasks` with `parentId`
  (don't send projectId/tagIds for subtasks).
- `GET /tasks/:id`, `PATCH /tasks/:id` (same fields, no parentId/subTaskIds), `DELETE /tasks/:id`
- `POST /tasks/:id/archive`, `POST /tasks/:id/restore`, `POST /tasks/:id/start` (start time tracking)
- `GET /task-control/current`, `POST /task-control/current`, `POST /task-control/stop`, `GET /focus`

## Fallback for read-only questions

If the API is off and the user only wants to *read*, the app writes full JSON backups every few minutes to
`<data-folder>/backups/` (newest file = latest; keys `task`, `project`, `tag`, ...; each has `entities`). Data folder:
macOS `~/Library/Application Support/superProductivity`, Windows `%APPDATA%\superProductivity`, Linux
`~/.config/superProductivity` (Snap/Flatpak differ). Say it may be a few minutes stale. Never write to these files.
