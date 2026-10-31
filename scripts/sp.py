#!/usr/bin/env python3
"""Minimal client for Super Productivity's built-in local REST API.

Usage:
  sp.py health
  sp.py projects
  sp.py tags
  sp.py tasks [--project NAME_OR_ID] [--today] [--query TEXT] [--include-done] [--source active|archived|all]
  sp.py add "Title" [--project NAME_OR_ID] [--due YYYY-MM-DD] [--deadline YYYY-MM-DD]
                    [--estimate 1h30m] [--notes TEXT] [--parent TASK_ID] [--today]
  sp.py done TASK_ID
  sp.py update TASK_ID '{"title": "..."}'
  sp.py raw METHOD /path ['{"json": "body"}']

The token is read from the app's data folder, so it never needs to be pasted anywhere.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:3876"
TOKEN_FILE = Path.home() / "Library/Application Support/superProductivity/local-rest-api-token"
TODAY_TAG = "TODAY"


def token():
    try:
        return TOKEN_FILE.read_text().strip()
    except FileNotFoundError:
        sys.exit(f"Token file not found at {TOKEN_FILE}. Enable 'local REST API' in Super Productivity settings.")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token()}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {BASE} ({e.reason}). Is Super Productivity running with the local REST API enabled?")


def data(resp):
    if not resp or not resp.get("ok"):
        sys.exit(json.dumps(resp, ensure_ascii=False, indent=2))
    return resp["data"]


def resolve_project(name_or_id):
    projects = data(call("GET", "/projects"))
    for p in projects:
        if p["id"] == name_or_id:
            return p["id"]
    matches = [p for p in projects if name_or_id.lower() in p["title"].lower()]
    if len(matches) == 1:
        return matches[0]["id"]
    titles = ", ".join(p["title"] for p in (matches or projects))
    sys.exit(f"Project '{name_or_id}' is {'ambiguous' if matches else 'not found'}. Candidates: {titles}")


def parse_duration(s):
    """'1h30m' / '45m' / '2h' -> milliseconds."""
    m = re.fullmatch(r"(?:(\d+(?:\.\d+)?)h)?\s*(?:(\d+)m)?", s.strip())
    if not m or not any(m.groups()):
        sys.exit(f"Bad duration '{s}', use e.g. 1h30m, 45m, 2h")
    hours = float(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    return int((hours * 60 + minutes) * 60_000)


def fmt_task(t, projects):
    bits = [t["title"]]
    if t.get("projectId"):
        bits.append(f"[{projects.get(t['projectId'], t['projectId'])}]")
    if t.get("dueDay"):
        bits.append(f"due {t['dueDay']}")
    if t.get("deadlineDay"):
        bits.append(f"deadline {t['deadlineDay']}")
    if t.get("isDone"):
        bits.append("(done)")
    return f"{t['id']}  " + "  ".join(bits)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    sub.add_parser("projects")
    sub.add_parser("tags")

    p = sub.add_parser("tasks")
    p.add_argument("--project")
    p.add_argument("--today", action="store_true")
    p.add_argument("--query")
    p.add_argument("--include-done", action="store_true")
    p.add_argument("--source", choices=["active", "archived", "all"])
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("add")
    p.add_argument("title")
    p.add_argument("--project")
    p.add_argument("--due", help="YYYY-MM-DD (planned day)")
    p.add_argument("--deadline", help="YYYY-MM-DD (hard deadline)")
    p.add_argument("--estimate", help="e.g. 1h30m")
    p.add_argument("--notes")
    p.add_argument("--parent", help="parent task id -> creates a subtask")
    p.add_argument("--today", action="store_true", help="add to Today list")

    p = sub.add_parser("done")
    p.add_argument("task_id")

    p = sub.add_parser("update")
    p.add_argument("task_id")
    p.add_argument("changes", help="JSON object of fields to change")

    p = sub.add_parser("raw")
    p.add_argument("method")
    p.add_argument("path")
    p.add_argument("body", nargs="?")

    a = ap.parse_args()

    if a.cmd == "health":
        print(json.dumps(call("GET", "/health"), ensure_ascii=False))
    elif a.cmd == "projects":
        for pr in data(call("GET", "/projects")):
            if not pr.get("isArchived"):
                print(f"{pr['id']}  {pr['title']}")
    elif a.cmd == "tags":
        for t in data(call("GET", "/tags")):
            print(f"{t['id']}  {t['title']}")
    elif a.cmd == "tasks":
        q = {}
        if a.project:
            q["projectId"] = resolve_project(a.project)
        if a.today:
            q["tagId"] = TODAY_TAG
        if a.query:
            q["query"] = a.query
        if a.include_done:
            q["includeDone"] = "true"
        if a.source:
            q["source"] = a.source
        path = "/tasks" + ("?" + urllib.parse.urlencode(q) if q else "")
        tasks = data(call("GET", path))
        if a.json:
            print(json.dumps(tasks, ensure_ascii=False, indent=2))
            return
        projects = {pr["id"]: pr["title"] for pr in data(call("GET", "/projects"))}
        for t in tasks:
            indent = "    " if t.get("parentId") else ""
            print(indent + fmt_task(t, projects))
        print(f"-- {len(tasks)} task(s)")
    elif a.cmd == "add":
        body = {"title": a.title, "isIgnoreShortSyntax": True}
        if a.parent:
            body["parentId"] = a.parent
        elif a.project:
            body["projectId"] = resolve_project(a.project)
        if a.due:
            body["dueDay"] = a.due
        if a.deadline:
            body["deadlineDay"] = a.deadline
        if a.estimate:
            body["timeEstimate"] = parse_duration(a.estimate)
        if a.notes:
            body["notes"] = a.notes
        if a.today and not a.parent:
            body["tagIds"] = [TODAY_TAG]
        t = data(call("POST", "/tasks", body))
        projects = {pr["id"]: pr["title"] for pr in data(call("GET", "/projects"))}
        print("created " + fmt_task(t, projects))
    elif a.cmd == "done":
        t = data(call("PATCH", f"/tasks/{a.task_id}", {"isDone": True}))
        print(f"done {t['id']}  {t['title']}")
    elif a.cmd == "update":
        t = data(call("PATCH", f"/tasks/{a.task_id}", json.loads(a.changes)))
        print(json.dumps(t, ensure_ascii=False, indent=2))
    elif a.cmd == "raw":
        body = json.loads(a.body) if a.body else None
        print(json.dumps(call(a.method.upper(), a.path, body), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (used by `tasks`)
    main()
