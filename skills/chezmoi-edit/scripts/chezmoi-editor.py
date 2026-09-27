#!/usr/bin/env python3
"""Non-interactive $EDITOR for `chezmoi edit`.

chezmoi invokes $EDITOR with a path to the source-state file. This script
plays the part of the editor: it reads a JSON list of edit operations from
the environment, applies them to that file, and exits.

Env vars:
  CHEZMOI_EDIT_OPS_FILE   Path to a JSON file describing the edit. Preferred:
                          avoids shell quoting problems with multi-line text.
  CHEZMOI_EDIT_OPS        Inline JSON, used only if OPS_FILE is unset.
  CHEZMOI_EDIT_DRY_RUN    If set to 1/true/yes, print a unified diff to stderr
                          and leave the file untouched.

JSON shape (a bare list of ops is also accepted):

  {
    "skip_if_contains": "alias buccl=",     // optional; exit 0 unchanged
    "ops": [
      {"op": "replace",       "old": "...", "new": "...", "count": 1},
      {"op": "delete",        "old": "...", "count": 1},
      {"op": "insert_after",  "anchor": "...", "text": "..."},
      {"op": "insert_before", "anchor": "...", "text": "..."},
      {"op": "append",        "text": "..."},
      {"op": "prepend",       "text": "..."},
      {"op": "regex_replace", "pattern": "...", "repl": "...",
                              "count": 1, "flags": "m"}
    ]
  }

Match discipline: "count" defaults to 1 and is an assertion, not a limit. An
op that matches a different number of times is an error, so a typo'd anchor
or an accidentally ambiguous string aborts the edit instead of silently
mangling the file. Use "count": "all" to accept any number (>= 1).

Exit codes: 0 = written (or intentionally skipped), 1 = refused. A non-zero
exit makes chezmoi abort without applying, and since nothing was written to
the source file there is nothing for git autoCommit to pick up.

Writes are done in place (truncate the existing inode, never rename) so the
edit survives chezmoi's default hardlink mode, where the path handed to the
editor is only a hardlink to the real source file.
"""

import difflib
import json
import os
import re
import sys


def die(msg):
    sys.stderr.write("chezmoi-editor: %s\n" % msg)
    raise SystemExit(1)


def env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def load_spec():
    ops_file = os.environ.get("CHEZMOI_EDIT_OPS_FILE")
    inline = os.environ.get("CHEZMOI_EDIT_OPS")
    if ops_file:
        try:
            with open(ops_file) as f:
                raw = f.read()
        except OSError as e:
            die("cannot read CHEZMOI_EDIT_OPS_FILE %s: %s" % (ops_file, e))
    elif inline:
        raw = inline
    else:
        die("set CHEZMOI_EDIT_OPS_FILE (or CHEZMOI_EDIT_OPS) to a JSON edit spec")
    try:
        spec = json.loads(raw)
    except ValueError as e:
        die("edit spec is not valid JSON: %s" % e)
    if isinstance(spec, list):
        spec = {"ops": spec}
    if not isinstance(spec, dict):
        die("edit spec must be a JSON object or list of ops")
    ops = spec.get("ops")
    if not isinstance(ops, list) or not ops:
        die("edit spec has no 'ops' list")
    return spec, ops


def check_count(op_name, found, want):
    """'count' asserts how many matches there should be."""
    if want == "all":
        if found == 0:
            die("%s: no match found" % op_name)
        return found
    if not isinstance(want, int) or want < 1:
        die("%s: 'count' must be a positive integer or \"all\"" % op_name)
    if found == 0:
        die("%s: no match found (expected %d)" % (op_name, want))
    if found != want:
        die(
            "%s: matched %d time(s) but expected %d - make the match string "
            "more specific, or set \"count\"" % (op_name, found, want)
        )
    return found


def apply_op(text, op, index):
    if not isinstance(op, dict):
        die("op %d is not an object" % index)
    kind = op.get("op")
    label = "op %d (%s)" % (index, kind)
    count = op.get("count", 1)

    if kind == "replace":
        old, new = op.get("old"), op.get("new")
        if old is None or new is None:
            die("%s: needs 'old' and 'new'" % label)
        n = check_count(label, text.count(old), count)
        return text.replace(old, new, n if count != "all" else -1)

    if kind == "delete":
        old = op.get("old")
        if old is None:
            die("%s: needs 'old'" % label)
        n = check_count(label, text.count(old), count)
        return text.replace(old, "", n if count != "all" else -1)

    if kind in ("insert_after", "insert_before"):
        anchor, ins = op.get("anchor"), op.get("text")
        if anchor is None or ins is None:
            die("%s: needs 'anchor' and 'text'" % label)
        n = check_count(label, text.count(anchor), count)
        repl = anchor + ins if kind == "insert_after" else ins + anchor
        return text.replace(anchor, repl, n if count != "all" else -1)

    if kind == "append":
        ins = op.get("text")
        if ins is None:
            die("%s: needs 'text'" % label)
        if text and not text.endswith("\n"):
            text += "\n"
        return text + ins

    if kind == "prepend":
        ins = op.get("text")
        if ins is None:
            die("%s: needs 'text'" % label)
        return ins + text

    if kind == "regex_replace":
        pattern, repl = op.get("pattern"), op.get("repl")
        if pattern is None or repl is None:
            die("%s: needs 'pattern' and 'repl'" % label)
        flags = 0
        for ch in op.get("flags", ""):
            flag = {"m": re.M, "s": re.S, "i": re.I, "x": re.X}.get(ch)
            if flag is None:
                die("%s: unknown regex flag %r (use m, s, i, x)" % (label, ch))
            flags |= flag
        try:
            rx = re.compile(pattern, flags)
        except re.error as e:
            die("%s: bad regex: %s" % (label, e))
        n = check_count(label, len(rx.findall(text)), count)
        return rx.sub(repl, text, count=0 if count == "all" else n)

    die("%s: unknown op %r" % (label, kind))


def main():
    paths = sys.argv[1:]
    if not paths:
        die("no file argument; this script is meant to be run as $EDITOR")
    if len(paths) > 1:
        die(
            "got %d files (%s) but an edit spec targets one file - run "
            "`chezmoi edit` on a single target at a time" % (len(paths), ", ".join(paths))
        )
    path = paths[0]

    spec, ops = load_spec()

    try:
        with open(path) as f:
            original = f.read()
    except OSError as e:
        die("cannot read %s: %s" % (path, e))

    skip = spec.get("skip_if_contains")
    if skip and skip in original:
        sys.stderr.write(
            "chezmoi-editor: %s already contains %r, leaving unchanged\n" % (path, skip)
        )
        return 0

    text = original
    for i, op in enumerate(ops, 1):
        text = apply_op(text, op, i)

    if text == original:
        die("ops produced no change to %s - the spec is probably wrong" % path)

    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile="a/" + os.path.basename(path),
            tofile="b/" + os.path.basename(path),
        )
    )

    if env_flag("CHEZMOI_EDIT_DRY_RUN"):
        sys.stderr.write("chezmoi-editor: DRY RUN, not writing %s\n%s" % (path, diff))
        return 0

    # Truncate in place rather than rename: preserves the inode, so the edit
    # propagates back through chezmoi's hardlink.
    try:
        with open(path, "w") as f:
            f.write(text)
    except OSError as e:
        die("cannot write %s: %s" % (path, e))

    sys.stderr.write("chezmoi-editor: applied %d op(s) to %s\n%s" % (len(ops), path, diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
