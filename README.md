<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg">
  <img alt="skills" src="docs/logo-light.svg" height="64">
</picture>

Agent skills I use with Claude Code and Codex, written to work for anyone.

| Skill | What it does |
|---|---|
| [`chezmoi-edit`](skills/chezmoi-edit/SKILL.md) | Edit chezmoi-managed dotfiles through `chezmoi edit --apply` with a scripted editor you can dry-run first, with or without autoCommit/autoPush |
| [`interview`](skills/interview/SKILL.md) | Interview the user through the harness's structured question tool before acting on anything that leaves room to guess |
| [`pr-body-md`](skills/pr-body-md/SKILL.md) | Write the body for a PR being opened, from the branch's commits, diff, and changelog or release notes |

## Layout

One directory per skill under `skills/`, each with a `SKILL.md` and any
supporting files beside it — the layout Claude Code, Codex, and `npx skills`
all understand.

## Install

With [`npx skills`](https://github.com/vercel-labs/skills):

```sh
npx skills add johnfoland/skills
```

Or link a skill into your agent's skills directory by hand:

```sh
git clone https://github.com/johnfoland/skills.git
ln -s "$PWD/skills/skills/interview" ~/.claude/skills/interview   # Claude Code
ln -s "$PWD/skills/skills/interview" ~/.agents/skills/interview   # Codex
```

## Conventions

Skills say *how* to do something and stay generic. Anything personal — a
repo name, a machine path, a preference — belongs in the user's own
instructions (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`), and a skill that
needs such a fact defers to them rather than naming it.
