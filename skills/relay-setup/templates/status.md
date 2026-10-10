# Status

Last updated <YYYY-MM-DD> by `relay-setup`.
Last review: none yet.

## Where this stands

- The relay workflow was set up on <YYYY-MM-DD>. No project is active and no
  chunk is in flight.
- **Do next:** `/relay-project <idea>` to shape the first project, or
  `/relay-next` with a request for a small, already-designed fix.

## In flight

- **Chunk:** —
- **State:** none
- **Branch:** —
- **Pull request:** —
- **Units committed:** —

(Fixed shape. `State` ∈ `ready for an executor` · `executing` ·
`awaiting review` · `none`; `Branch`, `Pull request`, and `Units committed` are
`—` until set; the pull request carries `(draft)` or `(ready)`.
`/relay-execute` creates `chunk/<id>` from the integration branch, opens a
draft pull request, sets `executing`, updates `Units committed` per unit, and
sets `awaiting review` when its report lands; `/relay-next` reviews that pull
request on its branch, cuts the next chunk, and squash-merges. This file is
local and git-ignored: there is one copy, whatever branch is checked out, and
every relay skill edits it in place without committing it.)

## Follow-ups not yet scheduled

None.

## Decisions by chunk

None yet. One line per chunk: the decision-log IDs it added.
