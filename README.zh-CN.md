# super-productivity-skill

[English](README.md) | 简体中文

一个 [Agent Skill](https://agentskills.io)：让 Claude Code、Codex、OpenCode 以及其他能执行 shell 命令的 AI agent，通过
[Super Productivity](https://super-productivity.com/) 桌面版**自带的本地 REST API** 读取和管理你的待办，包括查看项目和任务、
添加任务（可设项目、计划日期、截止日期、预估时长、子任务）、标记完成、修改任务、开始计时。

不需要另外装 MCP 服务器或插件，也不会碰应用的数据库文件。

```
你：    在 Research 项目里加「跑 baseline 实验」，周五截止，预估 2 小时
Agent：created t4uSMIIo…  跑 baseline 实验  [Research]  deadline 2026-11-06
```

任务会马上出现在正在运行的应用里。

## 前置条件

- Super Productivity **桌面版 v19 或更高**（macOS / Windows / Linux 都行，REST API 只有桌面端有）
- Python 3（只用标准库）
- 打开 REST API：**设置 → Misc → 勾选「Enable local REST API (desktop only)」**。下方状态显示 `Running at http://127.0.0.1:3876` 就说明开好了

「Enable assistant access (MCP)」**不需要打开**，它只能往 Inbox 里加任务。

## 安装

clone 下来的文件夹必须叫 `super-productivity`，要和 skill 的 `name` 对得上。

**Claude Code**

```bash
git clone https://github.com/chu-jiaming/super-productivity-skill ~/.claude/skills/super-productivity
```

**Codex、OpenCode 等遵循 Agent Skills 规范的 agent**（用户级的通用目录）

```bash
git clone https://github.com/chu-jiaming/super-productivity-skill ~/.agents/skills/super-productivity
```

OpenCode 还会读 `~/.config/opencode/skills/` 和 `~/.claude/skills/`。如果好几个 agent 都要用，clone 一份，再用软链接链到其他目录就行。
只想在某个项目里用的话，放到项目里的 `.claude/skills/` 或 `.agents/skills/` 下面。

**不支持 skill 的 agent**（Cursor rules、Copilot instructions、`AGENTS.md` 等）

随便 clone 到一个位置，然后在 agent 的说明文件里加上类似这样的一段：

```markdown
要读取或修改我的 Super Productivity 任务，运行 `python3 /path/to/super-productivity-skill/scripts/sp.py`。
用法和流程见 /path/to/super-productivity-skill/SKILL.md。
```

装好之后，直接问 agent「今天有哪些待办？」或者「在 Y 项目里加个 X，周五截止」就行。

## 辅助脚本

`scripts/sp.py` 是给 agent 调用的小命令行工具，你也可以自己直接用：

```bash
python3 scripts/sp.py health
python3 scripts/sp.py projects
python3 scripts/sp.py tasks --project research --today
python3 scripts/sp.py add "读 COLMAP 论文" --project research --due 2026-11-06 --estimate 1h30m
python3 scripts/sp.py done <TASK_ID>
```

| 命令 | 作用 |
|---|---|
| `health` | 检查 API 是否在运行 |
| `projects` / `tags` | 列出 id 和名称 |
| `tasks [--project X] [--today] [--query TXT] [--include-done] [--source active\|archived\|all] [--json]` | 列出任务，默认只列未完成的 |
| `add "标题" [--project X] [--due YYYY-MM-DD] [--deadline YYYY-MM-DD] [--estimate 1h30m] [--notes TXT] [--today] [--parent ID]` | 添加任务；带 `--parent` 就是添加子任务 |
| `done ID` | 标记完成 |
| `update ID '{"title":"..."}'` | 修改任意可写字段 |
| `raw METHOD /path ['{json}']` | 直接调用任意接口 |

`--project` 可以填项目 id，也可以填项目名里的一段（不分大小写），只要能唯一匹配就行。不填就放进 Inbox。

### token 从哪里来

脚本会去应用的数据文件夹里读 `local-rest-api-token` 文件：

| 平台 | 数据文件夹 |
|---|---|
| macOS | `~/Library/Application Support/superProductivity` |
| Windows | `%APPDATA%\superProductivity` |
| Linux | `~/.config/superProductivity`（也会找 Snap 和 Flatpak 的位置） |

如果你的不在这些位置，可以设置下面的环境变量：

| 变量 | 作用 |
|---|---|
| `SP_TOKEN_FILE` | token 文件的路径 |
| `SP_API_TOKEN` | 直接填 token |
| `SP_API_URL` | API 地址（默认 `http://127.0.0.1:3876`） |

## 安全说明

- API 只监听本机的 `127.0.0.1`，每次请求都要带 token
- token 是运行时才读的，不会写进仓库，也不会出现在和 agent 的对话里
- 开着 API 的时候，这台电脑上以你的身份运行的程序都能读写你的任务。不用时把开关关掉就行；怀疑 token 泄露了，就点 **Regenerate Access Token** 换一个
- 这个 skill 不会修改 IndexedDB 或备份文件。API 没开、又只是想查看的时候，可能会去读应用的自动备份 JSON（数据可能晚几分钟）

## 参与贡献

欢迎提 issue 和 PR，尤其欢迎帮忙确认 Windows 和 Linux 上的 token 路径，以及适配更多 agent。

## License

[MIT](LICENSE)
