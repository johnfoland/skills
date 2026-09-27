# <Project name>

Instructions for coding agents. Codex reads this file; Claude Code reads it
through `CLAUDE.md`'s `@AGENTS.md` import.<Humans: see CONTRIBUTING.md.>

<One paragraph: what the project is, what it does, and for whom. Then where to
look: README.md for usage, CONTRIBUTING.md for the layout and release process,
docs/ for design.>

## Before you start

- Read `docs/decisions.md`. Those questions are settled: don't reopen one
  unless the user asks. When the user settles a new one, add an entry.
- <Check the roadmap: `gh issue list`.>

## Commands

- `<setup command>`: set up a fresh checkout.
- `<check command>`: everything CI checks. Run it before every push.
- `<narrow command>`: <one test, one package, one linter, for the loop while
  working.>

## Workflow

- One branch and pull request per change. Don't commit to `<default branch>`
  directly<; release-please is the only thing that does>.
- <Commit convention: Conventional Commits, as *Releases* describes | short
  imperative subjects, a body that says why.>
- CI must pass before a merge; don't bypass a failing required check (no
  `gh pr merge --admin`).
- Keep <README.md, CONTRIBUTING.md, the help text, …> in step with any
  behavior change, in the same pull request.

<## Releases — from the template for the chosen release system.>

<## Roadmap: GitHub Issues — from its template, if chosen.>

<## Conventions — where behavior lives and why ("put behavior in `ops.py`; the
CLI and the TUI both call it"), and rules a linter cannot enforce.>

<## Testing notes — the seams and fakes to use, and the traps a new test falls
into.>

<## Rules — things never to do in this repo, each with the reason (an incident,
a real user's data, a production system).>
