# Claude Code × CMUX 配置

> 这是 Claude Code（终端 AI 编程助手）配合 CMUX 工作流的初始环境配置。
>
> 适用于 macOS 新机快速搭建开发工作流，刚装好系统？照着做一遍就能安心让 AI 帮你写代码。

---

## 前置要求

新电脑请先安装以下基础工具：

```bash
# 1. Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Node.js（Claude Code 依赖）
brew install node

# 3. Claude Code CLI
npm i -g @anthropic-ai/claude-code

# 4. 登录 Claude Code
claude login

# 5. Bun（claude-hud 状态栏需要）
brew install oven-sh/bun/bun

# 6. trash（安全删除，替代 rm）
brew install trash

# 7. （可选）GitHub CLI
brew install gh
```

> **CMUX** 是一款面向 macOS 的免费开源终端，采用 Swift + AppKit 原生开发，支持垂直标签页、窗口分割、嵌入式网页浏览等特性，适合同时运行多个 Claude Code 会话。官网：[cmux.com](https://cmux.com/zh-CN)

---

## 一、cc alias（快速启动）

**这是什么？**

Claude Code 默认需要先 `cd` 到项目目录再输入 `claude`。这个 alias 把步骤合并成一行 `cc`，关掉终端闪烁，一键启动。

**怎么用？**

在 `~/.zshrc` 里加一行：

```bash
alias cc='cd ~/你的项目路径 && CLAUDE_CODE_NO_FLICKER=1 claude'
```

把 `~/你的项目路径` 替换为实际工作目录。

```bash
source ~/.zshrc
```

**验证**：终端输入 `cc`，应自动进入项目并启动 Claude Code。输入 `/exit` 退出，不会关闭终端窗口。

---

## 二、安全配置

Claude Code 会帮你执行 Bash 命令，万一 AI 理解错了，跑了一条 `rm -rf` 就麻烦了。这几件事让你安心让 AI 干活。

### 2.1 垃圾桶（安全删除）

前面已经用 `brew install trash` 装好了，在 `~/.zshrc` 加上：

```bash
alias rm='trash'
```

```bash
source ~/.zshrc
```

**验证**：`trash --version` 应显示版本号。

### 2.2 危险指令黑名单 + 偏好设置

创建或编辑 `~/.claude/CLAUDE.md`，写入以下内容：

```markdown
# Claude Code Preferences

## Communication

- Chinese by default (中文回复), concise and direct

## Code Style

- TypeScript + strict mode, named exports over default
- Functional components + hooks (React)
- CSS: Tailwind CSS only (no CSS-in-JS / CSS Modules unless project already uses them)
- Commits: Conventional Commits + Chinese scope, e.g. `feat(auth): 添加登录页面的表单验证`

## Tools

- New projects: Vite + Tailwind CSS

## Workflow

- Run tests before AND after changes
- Never commit or push unless explicitly asked
- Ask before destructive operations (delete, overwrite, force push)
- Bug fixes: reproduce first, focus on root cause, don't clean up surrounding code

## Design

- **ui-ux-pro-max** for design decisions (style, color, industry adaptation)
- **impeccable** for building UI components from scratch
- Avoid generic AI aesthetic. Maintain WCAG AA contrast and clear typography hierarchy.

## HUD

- Plugin: claude-hud v0.0.12
- Use default layout configuration

## Project Context

Frontend web apps, web games, UI/UX prototyping.
```

创建或编辑 `~/.claude/settings.json`，写入以下内容：

```json
{
  "permissions": {
    "allow": [],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Bash(git push -f:*)",
      "Bash(git reset --hard:*)",
      "Bash(git checkout -- *:*)",
      "Bash(git clean -fd:*)",
      "Bash(git branch -D:*)",
      "Bash(git rebase --abort:*)",
      "Bash(dd:*)",
      "Bash(mkfs:*)",
      "Bash(apt-get remove:*)",
      "Bash(brew uninstall:*)",
      "Bash(sudo:*)"
    ],
    "defaultMode": "allow"
  },
  "model": "sonnet[1m]",
  "enableAllProjectMcpServers": true,
  "extraKnownMarketplaces": {
    "claude-hud": {
      "source": {
        "source": "github",
        "repo": "jarrodwatts/claude-hud"
      }
    }
  },
  "effortLevel": "medium",
  "skipDangerousModePermissionPrompt": true
}
```

**说明：**

- `defaultMode: "allow"` — 默认允许执行，仅拦截 deny 列表（黑名单模式），日常效率最高
- `enableAllProjectMcpServers: true` — 启用所有项目级 MCP 服务器
- `model: "sonnet[1m]"` — 使用 1M context 的 Sonnet 模型
- 黑名单比仓库原版少了 `curl | bash` 和 `chmod 777`，因为日常开发偶尔会用到（比如安装脚本）

**验证**：在 Claude Code 中让 AI 执行 `rm -rf /tmp/test`，应被拦截。

### 2.3 Claude Code Proxy 配置

如果你也使用代理连接 LLM API，创建或编辑 `~/.config/claude-code-proxy/config.json`：

```json
{
  "baseURL": "<YOUR_PROXY_BASE_URL>",
  "modelMapping": {
    "small_model": "claude-sonnet-4-6",
    "model": "claude-sonnet-4-6",
    "opus_model": "claude-sonnet-4-6"
  },
  "apiKey": "<YOUR_API_KEY>"
}
```

**说明：** 三档模型全部使用 `claude-sonnet-4-6`。`baseURL` 和 `apiKey` 根据你自己的代理配置填写。

---

## 三、终端状态栏（claude-hud）

**这是什么？**

给终端底部加一个信息栏，实时显示模型名称、Context 用量、Git 分支、项目名称等。不用猜"我现在在哪个分支？Context 还剩多少？"

### 3.1 安装

**步骤 1：注册 marketplace**（在 Claude Code 终端内输入）

```
/plugin marketplace add jarrodwatts/claude-hud
```

**步骤 2：安装插件**

```
/plugin install claude-hud
```

**步骤 3：配置状态栏**

```
/claude-hud:setup
```

完成后重启 Claude Code，底部就会出现状态栏。

> 来源：[jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud)

### 3.2 配置

编辑 `~/.claude/plugins/claude-hud/config.json`：

```json
{
  "language": "zh",
  "layout": "compact+separators"
}
```

### 3.3 效果

底部状态栏实时显示：

| 元素 | 含义 |
|------|------|
| 模型名 + 1M context | 当前 AI 模型和 context 窗口大小 |
| 进度条 19% | 对话上下文用量，快到上限时会变红警告 |
| main* | Git 分支名，* 表示有未提交的修改 |
| 项目名称 | 当前工作目录名称 |

---

## 四、验证清单

全部配置完成后，逐一验证：

| 步骤 | 验证命令 | 预期结果 |
|------|----------|----------|
| Claude Code | `claude --version` | 显示版本号 |
| 快捷启动 | `cc` | 进入项目并启动 Claude Code |
| 回收站 | `trash --version` | 显示版本号 |
| 黑名单 | 在 Claude Code 中执行 `rm -rf /tmp/test` | 被拦截并提示拒绝 |
| HUD 插件 | 打开 Claude Code | 底部显示状态栏 |

---

## 五、文件结构

```
~/.claude/
├── CLAUDE.md              # AI 偏好与行为规则
├── settings.json          # 全局配置（权限、黑名单、插件）
├── plugins/
│   └── claude-hud/
│       └── config.json    # HUD 插件配置
├── keybindings.json       # 自定义快捷键
└── scheduled_tasks.json   # 定时任务

~/.config/
└── claude-code-proxy/
    └── config.json        # 代理配置（如使用）
```

---

## 六、推荐安装的 Skills

以下 Skills 是我日常在用的，按需安装：

### 设计 & UI

| Skill | 用途 |
|-------|------|
| `ui-ux-pro-max` | UI/UX 设计智能 |
| `impeccable` | 前端界面生成 |
| `shape` | UX/UI 规划 |
| `layout` | 布局与间距优化 |
| `colorize` | 色彩增强 |
| `animate` | 界面动画增强 |
| `audit` | 技术质量检查 |

### 代码 & 安全

| Skill | 用途 |
|-------|------|
| `code-review-skill` | 多语言代码审查 |
| `security-review`（trailofbits-security） | 安全审计 |
| `simplify` | 代码审查与优化 |
| `claude-api` | Claude API / SDK 开发 |

### 自定义 Slash Commands

| 命令 | 用途 |
|------|------|
| `/review` | PR 审查 |
| `/security-review` | 安全审查 |
| `/design-audit` | 设计审计 |
| `/feature-complete` | 功能完整性检查 |

### MCP 推荐

| MCP | 用途 |
|-----|------|
| `context7` | 最新库文档查询 |

---

<!--
  ============================================================
  For AI Assistant — 以下是指令区，加载此文件时自动生效
  当 AI 读取此文件时，应将以下规则应用到后续所有操作中
  ============================================================
-->

## For AI Assistant

当你作为 Claude Code AI 加载此配置时，以下规则生效：

### 安全规则
- **禁止执行**：`rm -rf`、`git push --force`、`git reset --hard`、`git checkout -- *`、`git clean -fd`、`git branch -D`、`git rebase --abort`、`sudo`、`dd`、`mkfs`、`apt-get remove`、`brew uninstall`
- **删除文件**：使用 `trash` 而非 `rm`，操作前先确认
- **修改配置**：编辑 `settings.json` 前必须先读取当前内容，仅做增量修改
- **git 操作**：
  - 不自动 commit/push，除非用户明确要求
  - 不 skip hooks（`--no-verify`）
  - 不 force push 到 main/master
  - commit 使用 Conventional Commits 格式（feat/fix/chore/refactor/docs/test），scope 用中文

### 沟通规则
- 默认使用中文回复
- 回答简洁直接，不说废话
- 不确定时先询问再操作
- 代码注释用英文
- 文件名和变量命名遵循项目现有约定

### 编码风格
- 优先 TypeScript + strict mode
- Named exports over default exports
- React 使用函数式组件 + hooks
- camelCase 变量/函数名，PascalCase 组件/类型
- CSS 只用 Tailwind CSS
- 不添加项目已有功能以外的抽象和封装
- 不为了"好看"而过度重构

### 工作流
- 改代码前先读代码
- Bug 修复：先复现问题，再定位根因，最后修复。不顺手清理周围代码
- 改动前后都运行测试
- 新创建的 commit 和 PR 需要用户明确同意
