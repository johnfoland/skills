---
name: instructions-setup
description: Set up, or reorganize, a repository's agent instructions. Makes AGENTS.md the one instructions file (what the project is, its commands, workflow, conventions, and rules), with a CLAUDE.md that imports it, project skills in .agents/skills behind a .claude/skills symlink, a git-ignored CLAUDE.local.md for machine-specific notes, and a decision log. Optionally adds a GitHub Issues roadmap (labels and filing rules) and a release system (release-please with Conventional Commits, or hand-cut releases through the relay workflow). Use when a repo has no AGENTS.md or its instructions are scattered, and whenever the user asks to "set up instructions", "write an AGENTS.md", "set up CLAUDE.md", "add release-please", "track the roadmap in issues", or tidy a repo's agent setup; also when relay-setup finds no instruction baseline.
---

# Set up a repo's agent instructions

AGENTS.md is a repo's one real instructions file, written for any agent.
CLAUDE.md holds `@AGENTS.md` plus any lines only Claude Code needs, so shared
guidance never lives there. Instructions load into every session, so every line
has to earn its place: write what an agent could not infer from the code and
would get wrong without being told, and leave out what the README, the code,
or a linter already says.

## 0. Orient

Read every instruction file the repo has: AGENTS.md (including nested ones),
CLAUDE.md, CLAUDE.local.md, `.cursorrules` or `.cursor/rules/`,
`.github/copilot-instructions.md`, GEMINI.md. Read the README, CONTRIBUTING.md,
and any docs index. Then detect:

- **Toolchains and commands:** the setup, build, test, lint, format, and type
  check commands, and whether one command runs all the checks (a Makefile
  `check` target, a `package.json` script, a `justfile` recipe).
- **CI:** the workflows under `.github/workflows/`, what they run, and which
  checks branch protection requires.
- **Branches and history:** the default branch
  (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), and the
  commit style in `git log --oneline -30` (Conventional Commits already?).
- **Releases:** tags, a changelog and its format, `release-please-config.json`,
  and release workflows.
- **Issues:** `gh repo view --json hasIssuesEnabled,visibility` and
  `gh label list`.
- **Skills and local notes:** project skills in `.agents/skills/` or
  `.claude/skills/`, and whether `CLAUDE.local.md` is ignored
  (`git check-ignore -q CLAUDE.local.md`).
- **Decisions:** a decision log, ADRs, or settled questions recorded anywhere.

If instructions already exist, this is a reorganization. Keep every rule, move
each where it belongs, and show the user what moved. Never drop a rule
silently; if one looks obsolete, ask.

## 1. Interview

Ask what detection cannot settle, with the harness's structured question tool
(the `interview` skill, if available, says how), leading each question with the
detected or conventional answer as the recommendation. One or two rounds
usually cover it:

- What the project is and who it is for, if the README does not say.
- The check command to run before every push, and whether CI runs the same.
- **Release system:**
  - **release-please:** versions and the changelog come from Conventional
    Commits, and merging a release pull request tags and publishes. It needs
    no skill to cut a release.
  - **Hand-cut:** agents keep a Keep a Changelog `[Unreleased]` section as they
    commit, and `/relay-release` derives the version and cuts the release.
    This needs the relay workflow, so offer `relay-setup` afterwards.
  - **None yet.**
- **Commit convention:** Conventional Commits (required with release-please)
  or plain messages.
- **GitHub Issues as the roadmap:** yes or no, and if yes, the area labels
  that divide the project (for example `cli`, `ui`, `docs`, `release`).
- Rules every agent must follow here: things never to do, docs to keep in step
  with behavior, where behavior belongs.

## 2. Write the instruction files

1. **AGENTS.md.** Fill `templates/AGENTS.md`, dropping every section and
   alternative that does not apply. Add the **Releases** section from
   `templates/sections/` for the chosen system, and the roadmap section if
   chosen (§3). Add *Conventions*, *Testing notes*, and *Rules* sections only
   when there is something real to say, and give each rule its reason: a rule
   with a reason gets followed in cases it did not foresee. Link to docs rather
   than copying them, and point humans to CONTRIBUTING.md rather than
   duplicating it. Aim for a file an agent reads in a minute. In a monorepo,
   put package-specific rules in a nested AGENTS.md in that package.
2. **CLAUDE.md** contains `@AGENTS.md`, plus any lines only Claude Code needs
   (its hooks, its tool quirks). Move shared guidance found in an existing
   CLAUDE.md into AGENTS.md.
3. **Other agents' files.** Fold `.cursorrules`, Copilot, and Gemini
   instructions into AGENTS.md, and replace each with a pointer to it or
   remove it, as the user prefers.
4. **Project skills.** If the repo has or wants project skills, keep them in
   `.agents/skills/`, and make `.claude/skills` a relative symlink to
   `../.agents/skills` so Claude Code finds the same ones. Move the contents of
   an existing `.claude/skills/` directory first.
5. **CLAUDE.local.md.** Offer one from `templates/CLAUDE.local.md` for notes
   specific to one machine or maintainer (local install paths, dotfiles
   involved, release chores done by hand). Make sure it is git-ignored: if
   `git check-ignore` says it is not, add it to `.gitignore`.
6. **Decision log.** Create `docs/decisions.md` from `templates/decisions.md`
   unless the repo has one. An existing log whose entries have no IDs gets them
   once (`DEC-1`, `DEC-2`, … in file order), so docs and code can cite them;
   say so in the summary. Move settled questions found in other instruction
   files into it.

## 3. Optional: GitHub Issues roadmap

Add the section from `templates/sections/roadmap-issues.md`, with the repo's
owner and name and its area labels. Keep the public-issues bullet only for a
public repo. Create the `idea` label ("Not yet planned: a thought to triage")
and the area labels with `gh label create`, and keep GitHub's default type
labels (`bug`, `enhancement`, `question`). Choosing this option in the
interview is the go-ahead to create them.

## 4. Optional: release system

**release-please:**

- Use `templates/sections/releases-release-please.md`, and set the Workflow
  section's commit convention to Conventional Commits.
- Copy `templates/release-please/release-please-config.json` to the root and
  set `release-type` for the ecosystem (`python`, `node`, `rust`, `go`,
  `simple`, …), `package-name` where the release type needs it, and
  `extra-files` for every other file that carries the version (a `__version__`,
  a plugin manifest, a lockfile entry). Copy `release-please-manifest.json` to
  `.release-please-manifest.json` with the current version, or leave `0.0.0`
  when there is none: with `bump-minor-pre-major`, the first `feat` then
  releases `0.1.0`.
- Copy `release.yml` and `pr-title.yml` into `.github/workflows/`, replacing
  the branch placeholders; if the repo's CI workflow already has jobs, the
  title check may be a job there instead. Ask what the project publishes (PyPI,
  npm, crates.io, a container registry, a Homebrew tap) and replace the
  commented `publish` job with a real one, using trusted publishing where the
  registry supports it.
- An existing `CHANGELOG.md` in another format stays; release-please adds its
  sections above the old content.
- Some setup cannot be done from files. List it for the user, and in
  CONTRIBUTING.md's release section for other maintainers: allow GitHub
  Actions to create pull requests (Settings → Actions → General); add a
  `RELEASE_PLEASE_TOKEN` secret, a fine-grained token for this repo with
  Contents and Pull requests read/write, or release pull requests wait for a
  maintainer to approve their CI; make the title check a required status
  check; and configure the registry's trusted publisher and any deployment
  environment.

**Hand-cut:**

- Use `templates/sections/releases-hand-cut.md`, with the behavior-bearing
  paths (the directories and files whose changes users can observe: source,
  build files, CI workflows, recorded fixtures) and the publication chosen in
  the interview.
- Create `CHANGELOG.md` from `templates/CHANGELOG.md` if the repo has none.
- The cut itself is `/relay-release`, which needs the relay workflow. Suggest
  running `relay-setup` next.

**None:** leave the Releases section out.

## 5. Land it

Show the user a summary of the changes. Unless they say otherwise, land them
through a branch and pull request, titled as the commit convention requires
(`chore: set up agent instructions`), and squash-merge once CI passes. If the
repo has no remote yet, or the user wants it committed directly, commit on the
current branch and say so.

## 6. Hand off

Report the files written, the choices made, anything moved between files, the
labels created, and the one-time settings left for the user. If the user chose
hand-cut releases or wants to build in chunks, close with: *"Run
`/relay-setup` next to add the relay workflow."*
