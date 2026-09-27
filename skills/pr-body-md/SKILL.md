---
name: pr-body-md
description: Write a polished pull request body for the current branch from its commit history, code diff, and changelog or release notes. Use this whenever the user asks to open, create, or draft a pull request (including a draft PR, or `gh pr create`), asks for a PR description or body, or wants an existing PR's description rewritten.
---

# PR Body

Generate a polished pull request body for the current branch by synthesizing the commit history, code diff, and changelog documentation.

## Steps

### 1. Identify the base branch

The base is the branch the PR will merge into. Take the first of these that applies:

1. The branch the user named, or the base of the PR if one already exists (`gh pr view --json baseRefName -q .baseRefName`).
2. The branch the repo's own conventions name: its agent instructions or contributing docs may send PRs to an integration branch (`develop`, `dev`, `next`) or a release branch rather than the default.
3. The remote's default branch:

   ```bash
   git symbolic-ref --short refs/remotes/origin/HEAD   # e.g. origin/master
   ```

   If that ref is not set, `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` gives the same answer.

Fetch the base first and compare against the remote-tracking ref (`origin/<base>`), so a stale local copy does not pull already-merged work into the PR. The steps below write it as `<base>`.

### 2. Gather commit history

```bash
git log <base>..HEAD --oneline
```

Read every commit message. They reveal the scope and sequence of work: the narrative arc the PR body should follow.

### 3. Read the code diff

```bash
git diff <base>...HEAD
```

The three-dot form diffs against the merge base, so it shows only what this branch changed. Read the full diff. Focus on:
- What behavior changed, not just what lines changed
- Non-obvious mechanics: timing, state management, error handling, edge cases
- Patterns that span multiple files and tell a coherent story

Do not produce a file-by-file summary. Look for the "why" behind the changes.

### 4. Read release documentation

Find where the repo keeps its changelog and release notes. Common places are a top-level `CHANGELOG.md`, `CHANGES.md`, `HISTORY.md`, or `RELEASENOTES*` file, a `docs/` or `release-notes/` directory, and per-change fragment directories such as `changelog.d/`, `.changeset/`, or `newsfragments/`; the repo's instructions or contributing docs may say which. If there are none, skip this step.

Read only the unreleased part of each: the `[Unreleased]` section, or the fragments not yet folded into a release. Only entries added on the current branch should be considered; `git diff <base>...HEAD -- <path>` shows which those are. User-facing release notes are especially valuable for framing changes at the right level of abstraction.

### 5. Synthesize and write the PR body

**Opening paragraph (required):**
- Must begin with the exact words "This PR"
- One concise paragraph of plain prose; no bullets, no headers, no jargon
- Orients the reviewer to the overall purpose and scope at a glance

**Body (after the opening paragraph):**
- Use `###` (h3) for all section headers
- Use headers, bullet lists, or tables where they genuinely help; not to pad length
- Do NOT list every changed file; that is noise
- Do get specific about important mechanics when they matter: e.g., a retry loop introduced, a race condition fixed, a new composable that replaced inline logic
- Group related changes logically rather than repeating the commit order
- Draw from the user-facing release notes for framing; draw from the code diff for technical depth

**Tone and style:**
- Matter-of-fact, professional
- Active voice: "adds", "fixes", "caps", "restores"
- No superlatives or filler ("great improvement", "now users can easily")
- Never use em dashes; use colons or semicolons instead, as appropriate
