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
