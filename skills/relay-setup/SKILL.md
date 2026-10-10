---
name: relay-setup
description: Set up, update, or adopt the relay workflow in a repository, the planner/executor process run by relay-project, relay-next, relay-execute, and relay-release. Builds on the repo's instruction baseline from instructions-setup (running it first when missing), then writes the "Relay workflow" section of AGENTS.md (branches, gate command, CI, how releases and GitHub Issues fit in, authority docs, file paths), git-ignores the local .relay/ directory, and scaffolds the status file, chunk directory, review and brief checklists, and project registry in it. Also moves a repo's committed relay process files out of git into .relay/. Use when the user wants to start working in chunks, set up the planner/executor or relay workflow, "set up relay", adopt the relay skills in a repo, migrate a repo's own planner/executor skills onto them, change a relay setting, or stop committing the relay's process files; and whenever another relay skill stops because AGENTS.md has no relay section.
---

# Set up the relay workflow

The relay workflow builds a repository in **chunks**: small, fully specified
briefs that fresh agent sessions pick up, build, review, and merge, handing off
to one another only through local process files and the pull requests. Four
skills run it:

- `relay-project` shapes an idea into settled design and an ordered delivery
  plan.
- `relay-next` (planner/reviewer) reviews the chunk in flight and cuts the next
  brief.
- `relay-execute` (executor) builds a brief unit by unit on its own branch and
  draft pull request.
- `relay-release` cuts a version.

The relay layer sits on the repo's instruction baseline: AGENTS.md with its
commands and workflow, a decision log, and optionally a **Releases** section
and a GitHub Issues **Roadmap** section. `instructions-setup` writes that
baseline. This skill adds a **Relay workflow** section to AGENTS.md, holding
the settings the relay skills read, and the relay's own process files. The
other relay skills refuse to run without the section.

## Process files stay out of git

The relay's process files (the status file, chunk briefs, project records, and
the review and brief checklists) are working state, not part of the product.
They live in `.relay/` at the root of the repository's main working tree, which
`.gitignore` excludes (`/.relay/`), and they are never committed:

- There is one copy, whatever branch is checked out. A session in a linked
  worktree reads and writes the main working tree's `.relay/` (the first path
  `git worktree list` prints), not one of its own.
- The pull request is the remote record of a chunk: its body carries the
  executor's report, and the reviewer posts the review on it.
- Tracked files never cite process files: code, authority docs, the decision
  log, the changelog, and pull request titles cite authority sections,
  decision IDs, issues, and pull requests, never a chunk ID, a review finding,
  or a checklist entry. Someone with only the remote cannot follow those.
- Everything else the relay touches stays tracked: AGENTS.md, the authority
  docs, the decision log, the changelog, and `tools/`.
- `git clean -x` (or `-X`) deletes `.relay/`, and nothing else holds a copy.
  The files live on one machine, so a handoff between sessions needs the same
  checkout.

## 0. Orient

Read AGENTS.md, CLAUDE.md, the README, and any docs index.

- **No baseline** (no AGENTS.md, or one without a decision log): run
  `instructions-setup` first, following that skill, then come back here. If it
  is not installed, create the baseline yourself: AGENTS.md as the one
  instructions file, a CLAUDE.md containing `@AGENTS.md`, and a decision log.
- **A relay section already exists:** this is an update. Show the current
  settings, ask what should change, and go to §3. If git tracks any of its
  process files, the update includes moving them out of git (§3), whether or
  not the user asked for anything else.

Then detect what you can instead of asking for it:

- **Branches.** The default branch, and any other long-lived branch such as
  `develop` (`git branch -r`). Branch protection, where visible:
  `gh api repos/{owner}/{repo}/branches/<branch>/protection` (a 404 means
  unprotected or no admin access).
- **Gate candidates.** A single command that runs every check. AGENTS.md's
  *Commands* section may already name it; otherwise look for a Makefile
  `check` or `test` target, `package.json` scripts, a `justfile`, `tox` or
  `nox`, `cargo`, `go test ./...`.
- **CI.** `.github/workflows/*.yml`: which workflow runs the checks, on which
  events (`pull_request` types, whether drafts are skipped, pushes to which
  branches), and whether it accepts `workflow_dispatch`.
- **Releases and Issues.** What the baseline's *Releases* and *Roadmap*
  sections say, if they exist.
- **Authority docs.** A spec, design docs, architecture notes, ADRs.
- **Existing machinery.** A planner/executor process of the repo's own: local
  skills in `.agents/skills/` or `.claude/skills/`, a status file with an
  In-flight block, chunk briefs, review checklists. Note which of them git
  tracks (`git ls-files`): committed process files are a migration (§3).

## 1. Choose the settings

Every relay skill reads these from the section. Infer what you can, then
interview the user for the rest with the harness's structured question tool
(the `interview` skill, if available, says how), leading each question with the
detected value as the recommended answer. Always confirm the branch model, the
gate, and the authority docs, even when detection looks certain: a wrong guess
here misdirects every later session.

| Setting | What it holds | Default |
|---|---|---|
| Integration branch | Where chunk and planning pull requests squash-merge. | The default branch. |
| Release branch | The same branch, or a separate one the integration branch reaches through a merge-commit release pull request (hand-cut releases only). | Same as integration. |
| Gate | One command that runs every check the repo has, and must pass before every unit commit. Whether CI runs the same targets. | The baseline's check command. |
| CI | The workflow that runs the gate, and when it does not run (drafts, pushes to the integration branch). | Detected, or `none`. |
| Releases | How the relay fits the baseline's release system: release-please, hand-cut, or none. | The baseline's choice. |
| Issues | Whether relay files follow-ups and ideas as GitHub issues and starts work from them. | On when the baseline has a Roadmap section. |
| Authority | The docs that define behavior, in order. | `README.md` and the code's own documentation. |
| Status, Chunks, Review checklist, Brief checklist, Projects | Where each local process file lives. Always under `.relay/`. | `.relay/status.md`, `.relay/chunks/`, `.relay/review-checklist.md`, `.relay/brief-checklist.md`, `.relay/projects/`. |
| Decision log, Tools | Where the tracked decision log and review tools live, and the decision log's ID prefix. | The baseline's decision log (`docs/decisions.md`, `DEC-n`), `tools/`. |
| Review extras | Repo-specific checks every review runs. | none |
| Environment | What a session must set up first (a `PATH` entry, a toolchain). | none |

Do not invent a gate. If the repo has no single command that runs its checks,
record the closest existing command, and offer to make "add a gate command
that runs every check, and wire it into CI" the first maintenance chunk.

**Releases.** If the baseline has no release system and the user wants one,
run the release step of `instructions-setup` (its §4) first. Hand-cut releases
need the relay; release-please works with or without it. A separate release
branch goes only with hand-cut releases: release-please manages a single
branch.

## 2. Reconcile with the baseline

The relay changes a few things the baseline says. Edit the baseline sections so
AGENTS.md never states two rules for the same thing:

- **Workflow.** "One branch and pull request per change" becomes one chunk
  branch and pull request per chunk, plus `plan/<slug>` branches for planning
  changes. Code changes arrive through chunks.
- **release-please.** If the baseline requires Conventional Commits for every
  commit message, narrow it to pull request titles: those become the squash
  commits release-please reads, while unit commits on a chunk branch keep their
  relay titles (`P0002-C03-a: …`) and never reach the integration branch on
  their own.
- **Issues.** If the Roadmap section says work is tracked only in issues,
  refine it: ideas, bugs, and follow-ups are issues; the design and delivery
  plan for anything bigger than one chunk live in a project file, and each
  chunk in its brief, both linking the issues they come from. Change the status
  template's *Follow-ups not yet scheduled* text to say follow-ups are filed as
  issues.
- **Decision log.** The relay cites decisions by ID. If the baseline's log has
  no IDs, give its entries IDs once (the `instructions-setup` format), unless
  it is a table with its own IDs, which the relay skills read as is. The log
  stays tracked; its entries name their origin by date and pull request, not
  by chunk.

## 3. Adopting existing machinery

When the repo already runs its own planner/executor variant, or an earlier
relay setup that committed its process files, this is a migration, and four
rules keep it safe:

- **Map the tracked files, don't move them.** Point the decision-log and tools
  settings at the existing files and keep their ID prefixes: a decision log at
  `docs/open-questions.md` cited as `(OQ-n)` stays exactly that. Renaming
  breaks every citation in the docs and the code. Compare the existing
  In-flight block and its state names with the relay shape (in
  `templates/status.md`); if they differ, convert the block once, in this
  change. Existing release and versioning docs become the baseline's
  *Releases* section in its hand-cut form, pointing at them.
- **Sort every repo-specific rule into a home.** Read the repo's own skills
  line by line. Each rule that is not generic procedure the relay skills
  already carry goes to one of: a setting; **Review extras**; **Environment**;
  the *Releases* section (a docs snapshot list, artifact checks); a rule
  elsewhere in AGENTS.md; an entry in one of the checklists, keeping its
  provenance; or the design doc that owns it. Worked examples and incident
  history that only justified a generic rule can go. List anything that fits
  nowhere and ask the user about it before deleting anything.
- **Move the process files out of git.** Status file, chunk briefs, project
  records, and checklists go to `.relay/` (their old names map onto the
  defaults; keep their contents and ID schemes), and git stops tracking the
  old paths. At a different path, a checkout of an older commit cannot
  overwrite the local copies, and switching back cannot delete them. Before
  touching anything, archive the old files outside the repo (a dated tarball)
  and say where it is. Do the migration when no chunk is `executing` or
  `awaiting review`: an open chunk branch that edits the old status file would
  conflict with its removal. Then, in the setup branch (§6):
  1. Copy the files into `.relay/` and add `/.relay/` to `.gitignore`.
  2. `git rm -r --cached` the old paths, then delete them from the working
     tree, and confirm `git ls-files .relay` prints nothing.
  3. Fix every tracked file that links to or describes the old paths (a docs
     index, a branching or release doc, AGENTS.md): a link becomes plain text
     or goes, and a description of committed handoffs is rewritten for local
     files. Leave existing *citations* of chunks and checklist entries in code
     and docs alone: they are history, and the rule against new ones is
     enough. Grep with
     `git grep -n -E 'status\.md|chunks/|projects/|review-checklist|brief-checklist'`.
  4. In the moved files, bring the explanatory text that describes committing
     them or branch copies (the status file's In-flight note, the checklists'
     "How it is used" paragraphs, the projects index's introduction) in line
     with the templates. Links between them keep working: their layout under
     `.relay/` is the old one.
- **Remove the local skills last.** Delete them in the same change only if the
  relay skills are installed where this repo's agents will find them (check
  `~/.claude/skills/` and `~/.agents/skills/`, or ask). Otherwise the repo
  loses its workflow until they are. Also remove or rename any local skill
  whose name collides with a relay skill.

Update every doc that names the old skills (`/next` → `/relay-next`,
`/execute` → `/relay-execute`, and so on), including the status file's
explanatory text and the checklists' "How it is used" paragraphs.

## 4. Write the files

1. **AGENTS.md.** Fill `templates/agents-section.md` with the chosen settings,
   dropping the angle-bracket alternatives that do not apply, and insert it as
   the `## Relay workflow` section after the baseline sections, or replace the
   existing one. Make the §2 edits to the baseline sections.
2. **.gitignore.** Add `/.relay/` with a comment saying it holds the relay's
   local process files. Confirm with `git check-ignore .relay/status.md`.
3. **Process files.** For each path setting whose file does not exist yet,
   copy the matching template into `.relay/`: `templates/status.md`,
   `templates/review-checklist.md`, `templates/brief-checklist.md`,
   `templates/projects/index.md`, and `templates/projects/template.md`. Create
   the empty chunks directory. Fill in the dates, and replace `DEC-n` in the
   templates with the decision log's prefix if it differs.
4. **Never overwrite an existing file.** When a file already exists at a
   mapped path in a different format, ask whether to adopt it as it is,
   convert it, or map the setting to a new path.
5. **Docs index.** If the authority docs have an index (a `docs/README.md`),
   do not list the process files there: they are not in the repository, and
   AGENTS.md already says where they are.

## 5. Repository settings

The workflow assumes the repository enforces a few things. Compare them with
what §0 found and recommend changes, but ask before applying any: they are
outward-facing and affect everyone who uses the repo.

- Squash merges enabled (and merge commits, with a separate release branch);
  rebase merges off; head branches deleted automatically after merge.
- The integration branch (and a separate release branch) protected: changes
  through pull requests only, CI required on the latest commit, no
  force-push.
- Force-push blocked on `chunk/**`, so a chunk branch's history is the
  complete record its reviewer reads.

If the settings name a separate release branch or an integration branch that
does not exist yet, create it from the current release-branch tip and push it
before anything else, after confirming with the user.

## 6. Land it

Show the user a summary of the changes. Unless they say otherwise, land the
tracked ones (AGENTS.md, `.gitignore`, any baseline or docs edits, and a
migration's removals) like any planner change: a `plan/relay-setup` branch
from the integration branch, one commit, a pull request (titled as the repo's
convention requires), CI, and a squash-merge. If the repo has no remote, or
the user wants it committed directly, commit on the current branch and say so.
Before committing, check `git status --ignored .relay` shows `.relay/` as
ignored and nothing under it staged. After the merge, pull the integration
branch and confirm `.relay/` is intact.

## 7. Hand off

Report the settings chosen, the files created or adopted, where a migration's
archive is, the baseline sections changed, anything moved out of retired local
skills and where it went, and any repository setting left for the user. Close with the next step:
*"In a fresh session at this repo, run `/relay-project <idea>` to shape the
first project, or `/relay-next` with a small, already-designed fix."*
