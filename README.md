# Claude Code × CMUX 初始配置

> 这是 Claude Code（终端 AI 编程助手）配合 CMUX 工作流的初始环境配置，包含三项最实用的设置。
>
> 刚装好 Claude Code？照着下面的步骤设一遍，开发体验会顺畅很多。

---

## 1. cc alias（快速启动命令）

**这是什么？**

Claude Code 默认启动命令很长，每次都要先 cd 到项目目录再输入 `claude`。这个 alias 把它缩写成一行 `cc`，自动进入项目、关掉终端闪烁，一键启动。

**怎么用？**

在 `~/.zshrc` 里加一行：

```bash
alias cc='cd ~/你的專案路徑 && CLAUDE_CODE_NO_FLICKER=1 claude'
```

然后运行 `source ~/.zshrc`。之后打开终端直接输入 `cc` 就启动了。

---

## 2. 安全三件套

**为什么需要？**

Claude Code 是 AI 帮你写代码的工具，它会执行 Bash 命令。万一 AI 理解错了，跑了一条 `rm -rf` 删了重要文件就麻烦了。这三件事让你安心让 AI 帮忙干活。

### ① 垃圾桶（安全删除）

**作用：** 用 `trash` 替代 `rm`。删错的文件可以从废纸篓找回来，不像 `rm` 那样直接永久删除。

```bash
brew install trash
# 在 ~/.zshrc 添加
alias rm='trash'
```

### ② 危险指令黑名单

**作用：** 告诉 Claude Code 绝对不要执行这些危险命令，即使用户没发现 AI 想执行它。

在 `~/.claude/settings.json` 的 `permissions.deny` 中加入：

```json
"permissions": {
  "deny": [
    "Bash(rm -rf)",           // 递归删除整个目录
    "Bash(git push --force)", // 强制推送，会覆盖远程历史
    "Bash(git reset --hard)", // 丢弃所有未提交的改动
    "Bash(git checkout -- *)",// 重置所有文件
    "Bash(git clean -fd)",    // 删除未跟踪的文件
    "Bash(git branch -D)",    // 强制删除分支
    "Bash(git rebase --abort)",
    "Bash(sudo)",             // 以管理员权限执行
    "Bash(dd)",               // 直接写磁盘，极度危险
    "Bash(mkfs)",             // 格式化磁盘
    "Bash(apt-get remove)",   // 卸载系统包
    "Bash(brew uninstall)"    // 卸载 Homebrew 包
  ]
}
```

### ③ 权限模式（自己选）

**作用：** 决定 Claude Code 执行命令时，要不要先问你。

在 `settings.json` 中设置 `permissions.defaultMode`，三个选项：

| 模式 | 体验 | 适合谁 |
|------|------|--------|
| `default` | 每条命令都弹窗确认，最安全但很烦 | 新手，刚开始用 |
| `bypassPermissions` | 白名单里的命令自动执行，黑名单阻止（推荐） | 日常使用，效率最高 |
| `acceptEdits` | 文件修改自动接受 | 需要配合其他模式使用 |

**推荐：** `bypassPermissions` + 上面的黑名单，既能流畅干活，又不会误操作。

---

## 3. Claude Code 状态栏（HUD）

**这是什么？**

给终端底部加一个信息栏，随时看到当前用的模型、Context 用量、Git 分支、项目名称等信息。不用猜"我现在在哪个分支？改了什么东西？"

**安装：**

在 Claude Code 里输入：

```
/plugin install claude-hud
```

来源: `jarrodwatts/claude-hud`

**效果：**

装好后终端底部会出现两行信息：

| 元素 | 含义 |
|------|------|
| 🐱 | 自定义 emoji，一眼认出是你的环境 |
| Opus 4.6 (1M context) | 当前使用的 AI 模型和 context 窗口大小 |
| 进度条 19% | 对话上下文用量，快到上限时会变红警告 |
| 2H2m 76% | 5 小时使用额度还剩多少 |
| 1D3H 57% | 7 天（一周）使用额度还剩多少 |
| main* | Git 分支名，* 表示有未提交的修改 |
| CHUEH-Agent | 当前项目名称 |

**配置文件：**

`~/.claude/plugins/claude-hud/config.json`，语言设为 `en` 英文，布局用 `Compact + Separators`（单行紧凑排列）。
