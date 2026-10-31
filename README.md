# super-productivity-skill

一个 [Claude Code](https://claude.com/claude-code) skill，让 Claude 通过 [Super Productivity](https://super-productivity.com/) 桌面端**自带的本地 REST API** 读取和管理你的待办：查看项目和任务、添加任务（可指定项目、计划日期、截止日期、预估时长、子任务）、标记完成、修改任务。

不需要额外装 MCP 服务器或插件，也不会直接改应用的数据库。

> A Claude Code skill that manages Super Productivity tasks through the app's built-in local REST API (desktop, v19+). No MCP server or plugin required.

## 效果

```
你：在 VGGT-Splat 下加「跑 baseline 实验」，周五截止，预估 2 小时
Claude：created t4uSMIIo…  跑 baseline 实验  [VGGT-Splat]  deadline 2026-11-06
```

任务会立刻出现在正在运行的应用里，不需要重启。

## 前置条件

- macOS 上的 Super Productivity **桌面版 v19 或更高**（REST API 只有桌面端有）
- Python 3（只用标准库）
- 在应用里打开 REST API：**设置 → Misc → 勾选「Enable local REST API (desktop only)」**，下方状态显示 `Running at http://127.0.0.1:3876` 就说明开好了

下面那个「Enable assistant access (MCP)」**不需要打开**：它只能往 Inbox 里加任务，REST API 的功能更全。

## 安装

```bash
git clone https://github.com/chu-jiaming/super-productivity-skill ~/.claude/skills/super-productivity
```

装好后，在 Claude Code 里提到 Super Productivity 或待办，这个 skill 就会自动触发。

## 辅助脚本 `scripts/sp.py`

Claude 会优先调用这个脚本，你也可以在终端里直接用：

```bash
python3 ~/.claude/skills/super-productivity/scripts/sp.py health
python3 ~/.claude/skills/super-productivity/scripts/sp.py projects
python3 ~/.claude/skills/super-productivity/scripts/sp.py tasks --project 毕设 --today
python3 ~/.claude/skills/super-productivity/scripts/sp.py add "读 COLMAP 论文" --project VGGT --due 2026-11-06 --estimate 1h30m
python3 ~/.claude/skills/super-productivity/scripts/sp.py done <TASK_ID>
```

| 命令 | 作用 |
|---|---|
| `health` | 检查 API 是否在运行 |
| `projects` / `tags` | 列出项目 / 标签的 id 和名称 |
| `tasks [--project X] [--today] [--query TXT] [--include-done] [--source active\|archived\|all] [--json]` | 列出任务，默认只列未完成的 |
| `add "标题" [--project X] [--due YYYY-MM-DD] [--deadline YYYY-MM-DD] [--estimate 1h30m] [--notes TXT] [--today] [--parent ID]` | 添加任务；带 `--parent` 就是添加子任务 |
| `done ID` | 标记完成 |
| `update ID '{"title":"..."}'` | 修改任意可写字段 |
| `raw METHOD /path ['{json}']` | 直接调用任意接口 |

`--project` 可以填项目 id，也可以填项目名里的一段（不分大小写），只要能唯一匹配就行。不填的话，任务会放进 Inbox。

## 安全说明

- API 只监听本机的 `127.0.0.1:3876`，每次请求都要带 token
- 脚本从 `~/Library/Application Support/superProductivity/local-rest-api-token` 读取 token，**不会把它写进代码、仓库或对话**
- 开启之后，这台电脑上以你的身份运行的程序都能读写你的任务。不用的时候，在设置里把开关关掉就行；怀疑 token 泄露时，点 **Regenerate Access Token** 换一个新的
- 这个 skill 不会修改 IndexedDB 或备份文件。只读的时候如果 API 没开，会退回去读自动备份（数据可能晚几分钟）

## 其他平台

脚本里写的是 macOS 的数据路径。Linux / Windows 上需要把 `TOKEN_FILE` 改成对应位置，一般是 `~/.config/superProductivity/` 或 `%APPDATA%\superProductivity\`。

## License

MIT
