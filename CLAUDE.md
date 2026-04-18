# Claude Code 配置

## 沟通偏好

- 中文回复，简洁直接
- 代码风格: TypeScript + strict mode，函数式组件 + hooks
- CSS: 仅 Tailwind CSS
- 提交: Conventional Commits + 中文描述
- 变更前先跑测试，不主动 commit/push

## 权限策略

- 模式: `bypassPermissions`（白名单自动执行）
- 黑名单: `rm -rf`、`git push --force`、`git reset --hard`、`git checkout -- *`、`git clean -fd`、`git branch -D`、`git rebase --abort`、`sudo`、`dd`、`mkfs`、`apt-get remove`、`brew uninstall`

## HUD 状态栏

- 插件: claude-hud v0.0.12
- 语言: en
- 布局: Compact + Separators（单行）
- 显示: 模型名 + Context 进度条 + 5h/7d 用量 + Git 分支（含脏标记）+ 项目名称 + 会话名称
- `modelOverride`: "🐱🐱 Qwen3.6-Plus"

## 项目上下文

前端 Web 应用、Web 游戏、UI/UX 原型设计。
