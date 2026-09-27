---
name: repo-setup
description: Create a new repository, or bring an existing local folder that has no remote onto GitHub, set up the way a well-kept repo should be from its first commit. Interviews the user for the name, purpose, stack, license, and visibility; scaffolds the project with the stack's own tooling and a single check command; adds a .gitignore, a LICENSE, a README with a light/dark SVG logo, a CI workflow, and Dependabot; runs instructions-setup for the agent instructions; creates the GitHub repo with squash-only merges and auto-deleted branches; and protects the default branch once CI passes. Also covers taking a private repo public later. Use whenever the user wants to start, create, init, scaffold, or bootstrap a new project or repo, put an existing folder under git and on GitHub, or make a repo public.
---

# Set up a new repository

A repo is easiest to keep well when it starts well: one command runs every
check, CI runs the same command, the default branch only takes green pull
requests, and the agent instructions exist before the first agent session.
This skill does the creation; `instructions-setup` writes the instructions,
and `relay-setup` can add the relay workflow on top.

Personal defaults (where repos live, the GitHub owner, the default visibility
and license, the default branch name, a logo style) come from the user's own
instructions. Use them when stated, and ask for anything they leave open.
Never hardcode a person's name, account, or path into what you write.

## 0. Orient

- **Target.** A new directory, or an existing folder. An existing folder that
  is already a git repo with a remote is out of scope: for its instructions,
  use `instructions-setup`.
- **Tools.** `gh auth status` (and the account it is logged in as),
  `git config init.defaultBranch`, and the stack's tools (`uv`, `node`/`npm`,
  `go`, `cargo`, …).
- **Existing folder.** List what is there, including what a first commit would
  pick up (`git status --ignored` after `git init`). Look for anything that must
  never reach a remote: `.env` files, keys and certificates (`*.pem`, `id_*`),
  credentials, tokens in config files, large binaries, local databases. If
  `gitleaks` is installed, run `gitleaks detect --no-git` over the folder.
  Anything found goes into `.gitignore` or out of the folder, with the user's
  say, before anything is committed.

## 1. Interview

Ask with the harness's structured question tool (the `interview` skill, if
available, says how), in one or two rounds, leading each question with the
default from the user's instructions or the conventional answer:

- **Name** (the directory, the GitHub repo, and usually the package), a
  one-line **description**, and who it is for.
- **Stack**, in enough detail to scaffold without guessing: language and
  version, kind of project (library, CLI, web service, app), framework,
  package manager, and the formatter, linter, type checker, and test runner.
  Recommend the ecosystem's current standard where the user has no preference.
- **Visibility:** private or public.
- **License**, below. Default MIT.
- **Copyright holder** for the license: suggest the name on the user's GitHub
  profile (`gh api user -q .name`), else `git config user.name`, and confirm.
- **Logo:** what the icon should show; a picture of what the project is or
  does, drawn flat.
- **Publishing:** where releases go (PyPI, npm, crates.io, a container
  registry, nowhere yet). This is for `instructions-setup`'s release step.

### Choosing a license

Ask by objective, then name the license. The question tool takes four options,
so ask the family first and, for a copyleft family, which of the two:

| Your objective | License worth considering |
|---|---|
| "Use my code anywhere; I mainly want adoption." | **MIT** |
| "Same, but I want explicit patent protections." | **Apache 2.0** |
| "Companies can build proprietary products, but changes to my files should remain open." | **MPL 2.0** |
| "People can use my library in proprietary apps, but improvements to the library should remain open." | **LGPL** |
| "Distributed derivatives of my software should remain open." | **GPL** |
| "Even SaaS providers shouldn't be able to modify this and keep those modifications private." | **AGPL** |

The first question's options: **MIT (Recommended)**, **Apache 2.0**,
**Keep changes to this code open** (MPL 2.0 or LGPL), and **Keep derivatives
open** (GPL or AGPL). Fetch the text from GitHub (`gh api licenses/<key> -q
.body` with `mit`, `apache-2.0`, `mpl-2.0`, `lgpl-3.0`, `gpl-3.0`, or
`agpl-3.0`), and fill in the year and copyright holder where the text has
placeholders for them (MIT's `[year]` and `[fullname]`).

Before creating anything, show the user a summary (name, location, owner,
visibility, license, stack, what will be scaffolded) and get a go-ahead:
creating a GitHub repo is outward-facing.

## 2. Create the GitHub repo

Create it empty, so later steps can use it before anything is pushed:

```bash
gh repo create <owner>/<name> --private --description "<description>"   # or --public
```

Then set how it merges:

```bash
gh api -X PATCH repos/<owner>/<name> \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
  -F delete_branch_on_merge=true
```

Squash-only keeps the default branch one commit per pull request, titled by
the pull request, which is what Conventional Commit title checks and
release-please rely on. A later `relay-setup` with a separate release branch
turns merge commits back on.

## 3. Build the first commit locally

1. **Directory and git.** Create the directory where the user's instructions
   put repos (or use the existing folder), and, unless it is a git repo
   already, `git init -b <branch>` with the default branch from the user's
   instructions, else `init.defaultBranch`, else ask. Add the remote:
   `git remote add origin https://github.com/<owner>/<name>.git`.
2. **Scaffold** with the ecosystem's own tool rather than by hand: `uv init`
   (`--package`, `--lib`, or `--app`), `npm init` with the framework's
   generator, `cargo new`, `go mod init`. In an existing folder, add only what
   is missing.
3. **Tooling ships with the language.** Add the formatter, linter, type checker
   where the language has one, and test runner, each pinned (a lockfile or
   exact versions). Wire them into **one check command** that runs them all
   and fails on any problem: a Makefile `check` target, a `check` script in
   `package.json`, or a `just check` recipe. Add one real test, so the check
   command proves something from the first commit. Run it and make it pass.
4. **`.gitignore`** from GitHub's template for the stack
   (`gh api gitignore/templates/<Python|Node|Go|Rust|…> -q .source`), plus
   anything §0 found that must stay out.
5. **LICENSE** as chosen in §1.
6. **Logo.** Draw the icon as SVG elements in a 96×96 tile, following the
   user's logo style when their instructions describe one: flat shapes, a few
   colors, kept inside about x and y 9 to 87 so it clears the rounded corners,
   and legible at 32px. Then generate both variants with the bundled script,
   which sets the name in the chosen font and converts it to paths:

   ```bash
   uv run --with fonttools python <skill-dir>/scripts/make_logo.py \
     --text <name> --font <font file> --icon icon.svg --out docs/
   ```

   `<skill-dir>` is the absolute path of the directory holding this
   `SKILL.md`. The script's options set the tile, border, and text colors.
   Render both files (`rsvg-convert -z 3 docs/logo-light.svg -o light.png`, or
   a browser) and look at them before keeping them. Iterate on the icon until
   it reads at a glance, then delete the scratch icon file and renders.
7. **README** from `templates/README.md`, headed by the logo, with the
   description, install, usage, development (the check command), and license
   sections filled from what exists now; leave out a section there is nothing
   true to say in yet. If the README will also be shown on a package registry
   (PyPI, npm), use absolute `https://raw.githubusercontent.com/<owner>/<name>/<branch>/docs/logo-*.svg`
   URLs instead of relative ones; they load only once the repo is public.
8. **CI** from `templates/ci.yml` into `.github/workflows/ci.yml`: set up the
   toolchain from the version the repo pins, install locked dependencies, and
   run the check command. Keep the job named `check`; it becomes the required
   status check.
9. **Dependabot** from `templates/dependabot.yml` into
   `.github/dependabot.yml`, with the stack's ecosystem. Keep the
   commit-message prefixes if the repo will use Conventional Commits.
10. **Agent instructions.** Run `instructions-setup` now, following that skill,
    and pass on what the interview already settled (the purpose, the stack, the
    check command, publishing) so it asks only what remains. Its changes go into
    the initial history directly, since there is nothing yet to open a pull
    request against. If it sets up a GitHub Issues roadmap, its labels go on
    the repo §2 created.

Run the check command once more on the finished tree, then commit (with the
commit convention `instructions-setup` settled, e.g.
`chore: initial commit`) and push: `git push -u origin <branch>`.

## 4. Protect the default branch

Wait for the push's CI run (`gh run watch --exit-status`); protection needs
the `check` status to have reported once. Then:

```bash
gh api -X PUT repos/<owner>/<name>/branches/<branch>/protection --input - <<'EOF'
{
  "required_status_checks": {"strict": true, "contexts": ["check"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

Changes now arrive only through pull requests with a green `check`, including
the owner's, and nobody can bypass a failing check. A single maintainer can
still merge their own pull requests, since no approval is required. If the
repo has a pull-request title check (release-please), add its status to
`contexts` after it has run on a first pull request. A private repo on a plan
without branch protection makes this call fail: say so, and apply it when the
repo goes public.

## 5. Hand off

Report the repo URL, where it lives locally, the stack and check command, the
license, the settings applied and whether protection is on, and what
`instructions-setup` set up, including any one-time settings it left for the
user. If the user wants to build in chunks, suggest `/relay-setup` next.

## Going public later

When the user decides to publish a private repo, check before flipping it,
since everything in the history becomes public at once:

- The history holds nothing private: no secrets (`gitleaks detect` over the
  history, if installed), and no personal paths, hostnames, email addresses,
  or internal names in files or commit messages
  (`git log -p | grep -nE '/Users/|/home/|@'` as a start). Rewriting history
  to remove something is a separate decision for the user.
- There is a LICENSE, and the README's install and usage steps work for a
  stranger.
- Issues and pull requests, which become public too, are fit for any reader.

Show the user what you found, and flip it only on their go-ahead:
`gh repo edit <owner>/<name> --visibility public --accept-visibility-change-consequences`.
Then apply §4's protection if the plan skipped it, and check that the
README's images load.
