<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg">
  <img alt="skills" src="docs/logo-light.svg" height="64">
</picture>

Agent skills I use with Claude Code and Codex, written to work for anyone.

## Skills

| Skill | What it does |
|---|---|
| [`chezmoi-edit`](skills/chezmoi-edit/SKILL.md) | Edit chezmoi-managed dotfiles through `chezmoi edit --apply` with a scripted editor you can dry-run first, with or without autoCommit/autoPush |
| [`instructions-setup`](skills/instructions-setup/SKILL.md) | Set up a repo's agent instructions: AGENTS.md as the one instructions file, CLAUDE.md importing it, a decision log, and optionally a GitHub Issues roadmap and a release system (release-please or hand-cut) |
| [`interview`](skills/interview/SKILL.md) | Interview the user through the harness's structured question tool before acting on anything that leaves room to guess |
| [`pr-body-md`](skills/pr-body-md/SKILL.md) | Write the body for a PR being opened, from the branch's commits, diff, and changelog or release notes |
| [`repo-setup`](skills/repo-setup/SKILL.md) | Create a repo, or put a local folder on GitHub, set up from its first commit: scaffold and one check command, license, README with a generated logo, CI, Dependabot, protected default branch, then `instructions-setup`; and take a private repo public later |

### The relay workflow

The `relay-*` skills build a repository in chunks: small, fully specified
briefs that fresh agent sessions pick up, build, review, and merge. Sessions
hand work to each other only through files in the repo (a status file, the
chunk briefs, a decision log, and review and brief checklists that grow with
every mistake a review catches), so any session can resume from a cold start
and every change arrives through a reviewed pull request.

| Skill | What it does |
|---|---|
| [`relay-setup`](skills/relay-setup/SKILL.md) | Set up the relay workflow in a repo: its AGENTS.md settings and process files, or adopt a repo's own planner/executor process |
| [`relay-project`](skills/relay-project/SKILL.md) | Shape an idea into settled design and an ordered delivery plan, and close the project when its work is accepted |
| [`relay-next`](skills/relay-next/SKILL.md) | Planner/reviewer: review the chunk in flight, merge accepted work, and cut the next chunk brief |
| [`relay-execute`](skills/relay-execute/SKILL.md) | Executor: build the chunk in flight unit by unit, with tests, on its own branch and draft PR, then hand it back for review |
| [`relay-release`](skills/relay-release/SKILL.md) | Cut a version: by hand from the changelog, or by reviewing and merging release-please's release PR, then verify what it publishes |

The relay layer sits on the instruction baseline `instructions-setup` writes,
and uses its choices: releases cut by hand or by release-please, and, when the
repo tracks its roadmap in GitHub Issues, issues as the source of ideas and
the home of follow-ups. Run `relay-setup` once per repo (it runs
`instructions-setup` first if the baseline is missing). It writes a **Relay
workflow** section into the repo's AGENTS.md with the settings the other
skills read (branches, the gate command, CI, where each file lives) and
scaffolds the process files. Then alternate `/relay-next` and `/relay-execute`
in fresh sessions, with `/relay-project` for anything bigger than one chunk and
`/relay-release` to cut a version.

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
