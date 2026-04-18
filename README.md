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

# 5. （可选）GitHub CLI
brew install gh
```

> **CMUX** 是一款面向 macOS 的免费开源终端，采用 Swift + AppKit 原生开发，支持垂直标签页、窗口分割、嵌入式网页浏览等特性，适合同时运行多个 Claude Code 会话。官网：[cmux.com](https://cmux.com/zh-CN)

---

## 一、cc alias（快速启动）

**这是什么？**

Claude Code 默认启动需要先 `cd` 到项目目录再输入 `claude`。这个 alias 把步骤合并成一行 `cc`，自动进入项目、关掉终端闪烁，一键启动。

**怎么用？**

在 `~/.zshrc` 里加一行：

```bash
alias cc='cd ~/你的项目路径 && CLAUDE_CODE_NO_FLICKER=1 claude'
```

把 `~/你的项目路径` 替换为实际工作目录，例如 `~/Projects/my-app`。

```bash
source ~/.zshrc
```

**验证**：终端输入 `cc`，应自动进入项目目录并启动 Claude Code。输入 `/exit` 退出，不会关闭终端窗口。

---

## 二、安全三件套

**为什么需要？**

Claude Code 是 AI 帮你写代码的工具，它会执行 Bash 命令。万一 AI 理解错了，跑了一条 `rm -rf` 删了重要文件就麻烦了。这三件事让你安心让 AI 帮忙干活。

### 2.1 垃圾桶（安全删除）

**作用：** 用 `trash` 替代 `rm`。删错的文件可以从废纸篓找回来。

```bash
brew install trash
# 在 ~/.zshrc 添加
alias rm='trash'
```

**验证**：`trash --version` 应显示版本号。

### 2.2 危险指令黑名单

**作用：** 告诉 Claude Code 绝对不要执行这些危险命令。

在 `~/.claude/settings.json` 中写入：

```json
{
  "permissions": {
    "defaultMode": "allow",
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force)",
      "Bash(git reset --hard *)",
      "Bash(git checkout -- *)",
      "Bash(git clean -fd)",
      "Bash(git branch -D)",
      "Bash(git rebase --abort)",
      "Bash(sudo *)",
      "Bash(dd if=*)",
      "Bash(mkfs.*)",
      "Bash(apt-get remove *)",
      "Bash(brew uninstall *)",
      "Bash(curl * | bash)",
      "Bash(wget * -O - | *)",
      "Bash(chmod -R 777 *)"
    ]
  }
}
```

**验证**：在 Claude Code 中让 AI 执行 `rm -rf /tmp/test`，应被拦截。

### 2.3 权限模式

**作用：** 决定 Claude Code 执行命令时，要不要先问用户。

在 `settings.json` 中设置 `permissions.defaultMode`：

| 模式 | 体验 | 适合谁 |
|------|------|--------|
| `default` | 每条命令都弹窗确认，最安全但效率低 | 新手入门 |
| `allow` | 默认允许执行，仅拦截 deny 列表（黑名单模式） | 信任 AI 后日常使用 |
| `bypassPermissions` | 默认拦截所有命令，需要手动确认（白名单模式） | 对安全要求极高的场景 |

**推荐**：日常使用 `allow` + 上面的黑名单组合（黑名单模式，效率最高）。对安全要求更高的场景用 `bypassPermissions`，对已信任的命令可在 Claude Code 界面中选择 "Always allow"。

> **文件权限（可选）**：保护配置文件不被意外修改：`chmod 444 ~/.claude/settings.json`，需要编辑时临时改回 `chmod 644`。

---

## 三、终端状态栏（claude-hud）

**这是什么？**

给终端底部加一个信息栏，实时显示模型名称、Context 用量、Git 分支、项目名称等。不用猜"我现在在哪个分支？Context 还剩多少？"

### 3.1 安装

打开 Claude Code 终端，输入：

```
claude plugin install claude-hud@claude-hud
```

> **注意**：不要输入 `/plugin install claude-hud`，这是旧版语法。正确命令需要指定 marketplace：`claude plugin install claude-hud@claude-hud`。
>
> 安装后重启 Claude Code 生效。

### 3.2 配置

编辑 `~/.claude/plugins/claude-hud/config.json`：

```json
{
  "language": "en",
  "layout": "compact+separators"
}
```

### 3.3 效果

底部状态栏实时显示：

| 元素 | 含义 |
|------|------|
| 🐱 | 自定义 emoji |
| Opus 4.6 (1M context) | 当前 AI 模型和 context 窗口大小 |
| 进度条 19% | 对话上下文用量，快到上限时会变红警告 |
| 2H2m 76% | 5 小时使用额度剩余 |
| 1D3H 57% | 7 天（一周）使用额度剩余 |
| main* | Git 分支名，* 表示有未提交的修改 |
| CHUEH-Agent | 当前项目名称 |

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
├── settings.json          # Claude Code 全局配置（权限、黑名单）
├── settings.local.json    # 本地覆盖配置
├── plugins/
│   └── claude-hud/
│       └── config.json    # HUD 插件配置
├── keybindings.json       # 自定义快捷键
└── scheduled_tasks.json   # 定时任务
```

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
- **禁止执行**：`rm -rf`、`git push --force`、`git reset --hard`、`git checkout -- *`、`git clean -fd`、`git branch -D`、`git rebase --abort`、`sudo`、`dd`、`mkfs`、`apt-get remove`、`brew uninstall`、`curl | bash`、`chmod 777`
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
