---
name: chezmoi-edit
description: Edit files that chezmoi manages (dotfiles like ~/.zshrc, ~/.oh-my-zsh/custom/aliases.zsh, ~/.claude/settings.json, ~/.gitconfig) by driving `chezmoi edit --apply` with a scripted editor, instead of writing to the source repo or the target file directly. Use this whenever a file to be changed is or might be chezmoi-managed — adding a shell alias or function, tweaking a dotfile, changing config under ~/.claude — and for adding brand-new files to chezmoi. Works the same whether or not chezmoi is set to autoCommit or autoPush.
---

# Editing chezmoi-managed files

Prefer changing files *through* chezmoi rather than around it. Editing the
source repo by hand works but leaves an uncommitted change that bypasses the
user's normal flow; editing the target file alone gets reverted on the next
`chezmoi apply`.

## autoCommit and autoPush

chezmoi can be configured to commit (`git.autoCommit`) and push
(`git.autoPush`) every change to its source state as it happens. Don't check
for these settings or work around them: a user who turned them on wants that
behavior. Run the same flow either way and treat whatever commit and push
chezmoi makes as intended.

What the possibility does change is how careful to be up front, because with
autoCommit on there is no staging step between an edit and its commit:

- autoCommit commits the **entire source working tree**, not only what the
  command touched. A hand edit left uncommitted in the source directory is
  swept into the next chezmoi command's commit — even a `--dry-run` one.
  Confirm `git -C "$(chezmoi source-path)" status --short` is clean before
  running anything that writes, or unrelated work rides along.
- The dry run in Step 3 is the last look at the change before it lands, so
  get the spec right the first time.

## Step 1 — is the file managed?

```bash
chezmoi source-path ~/.oh-my-zsh/custom/aliases.zsh   # prints source path, or errors
chezmoi status                                        # empty = target and source in sync
```

- **Prints a path** → managed, use the flow below.
- **Errors** → not managed. Edit it normally. To bring it *under* management
  use `chezmoi add <path>`.
- **Source path ends in `.tmpl`** → it is a Go template. You are editing
  template source, and the applied result will differ from what you write.
  Read the whole file first and check `chezmoi execute-template < source` or
  `chezmoi cat <target>` to see what actually lands.

If `chezmoi status` is non-empty for your file, the target has drifted from the
source. Resolve that first — ask the user — or the apply step will clobber
whatever is in the target.

## Step 2 — write an edit spec

`scripts/chezmoi-editor.py`, in this skill's directory, is a non-interactive
`$EDITOR`. chezmoi hands it the source file; it applies a JSON list of
operations and exits. The commands below write the script's path as
`<skill-dir>/scripts/chezmoi-editor.py`: substitute the absolute path of the
directory holding this `SKILL.md`, since chezmoi runs the editor from
somewhere else.

Write the spec to a file in the scratchpad (avoids shell quoting problems with
multi-line content):

```json
{
  "skip_if_contains": "alias buccl=",
  "ops": [
    {"op": "insert_after",
     "anchor": "alias ssbrew='brew list | fzf'\n",
     "text": "\n# Upgrade Claude Code cask\nalias buccl='brew upgrade claude-code@latest'\n"}
  ]
}
```

Ops: `replace` (`old`/`new`), `delete` (`old`), `insert_after` /
`insert_before` (`anchor`/`text`), `append` / `prepend` (`text`),
`regex_replace` (`pattern`/`repl`, optional `flags` from `msix`).

Two things that make it safe to run unattended:

- **`count` is an assertion, not a limit.** It defaults to 1, so an op whose
  anchor is missing *or* ambiguous aborts rather than editing the wrong line.
  Set `"count": 3` or `"count": "all"` deliberately when you mean it.
- **`skip_if_contains`** makes a re-run a no-op instead of a duplicate.

Always read the source file first and copy the anchor text out of it verbatim,
including leading whitespace and the trailing newline.

## Step 3 — preview

```bash
CHEZMOI_EDIT_DRY_RUN=1 CHEZMOI_EDIT_OPS_FILE=/path/ops.json \
  <skill-dir>/scripts/chezmoi-editor.py "$(chezmoi source-path ~/.zshrc)"
```

Prints a unified diff and writes nothing. Do this every time. With autoCommit
on, the commit lands the moment `chezmoi edit` returns, so this dry run is the
only chance to catch a bad spec — `chezmoi diff` afterwards is too late.

## Step 4 — apply

```bash
CHEZMOI_EDIT_OPS_FILE=/path/ops.json \
EDITOR=<skill-dir>/scripts/chezmoi-editor.py \
VISUAL=<skill-dir>/scripts/chezmoi-editor.py \
  chezmoi edit --apply --hardlink=false ~/.oh-my-zsh/custom/aliases.zsh
```

Set both `EDITOR` and `VISUAL` — chezmoi checks `VISUAL` first. One target per
invocation; the script refuses multiple files, since one spec cannot sensibly
apply to several.

`chezmoi: warning: ... returned in less than 1s` is expected for a scripted
editor and is not a problem.

### About `--hardlink=false`

By default `chezmoi edit` hands the editor a **hardlink** in a temp directory so
the filename looks natural. Any editor that saves by writing a new file and
renaming it over the old one breaks that link, and the change is silently
discarded. This script writes in place — truncating the existing inode, never
renaming — so it is immune either way and has been verified working in default
hardlink mode. `--hardlink=false` is still worth passing: it makes chezmoi pass
the real source path, so diffs and error messages name the actual file instead
of `/var/folders/.../chezmoi-edit123456/.zshrc`.

If you ever modify this script, keep the in-place write.

## Step 5 — verify

```bash
grep -n "<the change>" "$(chezmoi source-path <target>)"   # source has it
grep -n "<the change>" <target>                            # target has it
chezmoi status                                             # empty = in sync
git -C "$(chezmoi source-path)" status --short --branch    # committed? pushed?
```

Then tell the user what landed: the commit chezmoi made and whether it was
pushed, or that the change is waiting in the source directory for them to
commit. For shell files, remind them to `source` the file or open a new shell.

## Failure behavior

A bad spec makes the script exit non-zero without writing anything. chezmoi then
reports `exit status 1` and aborts — no apply, no commit, no push, source repo
untouched. Verified. So a failed run is safe to diagnose and retry; fix the
anchor and run again.

## New files

`chezmoi edit` only works on already-managed files. For a new one, write it at
its normal location and then `chezmoi add <path>`. With autoCommit on, that
commits right away, so make sure the content is final. Adding into an
already-managed directory (e.g. a new script in `~/.local/bin/`) still needs an
explicit `add`.
