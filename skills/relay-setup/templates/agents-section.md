## Relay workflow

Work in this repository is built by fresh agent sessions that hand it to one
another through the files below, using the relay skills:

- `/relay-project` shapes an idea into settled design and an ordered delivery
  plan, and closes the project when its work is accepted.
- `/relay-next` reviews the chunk in flight, records the review, merges
  accepted work, and cuts the next chunk brief.
- `/relay-execute` builds the chunk in flight unit by unit on its own branch
  and draft pull request, then hands it back for review.
- `/relay-release` cuts a version: by hand from the changelog, or by
  reviewing and merging release-please's release pull request.

Code reaches the integration branch only through a chunk pull request, so every
change gets the executor's test discipline and a CI run. The status file is the
handoff between sessions: run each skill in a fresh session.

When code and an authority doc disagree, one of them is wrong: fix it and say
which. A decided entry in the decision log is not re-litigated; where the docs
genuinely do not cover something, add an entry, update the doc that should have
said it, and cite the entry at the code site.

### Settings

- **Integration branch:** `<integration>`. Chunk and planning pull requests
  squash-merge here.
- **Release branch:** <"same as the integration branch" | `<release>`, reached
  from `<integration>` by a merge-commit release pull request>.
- **Gate:** `<gate>`, which runs <what it runs>. It passes before every unit
  commit and push. <"CI runs these same targets." | omit>
- **CI:** <`<workflow file>` runs the gate on pull requests <once ready for
  review | including drafts>; pushes to `<integration>` <run it | run none> |
  none>.
- **Releases:** <release-please, as *Releases* describes: a chunk pull
  request's title is a Conventional Commit for the chunk's user-visible
  effect, and nobody edits the changelog by hand. Unit commits on a chunk
  branch keep their relay titles; only the squash commit reaches
  `<integration>`. | hand-cut, as *Releases* describes: behavior-bearing unit
  commits carry their changelog entries, and `/relay-release` cuts versions. |
  none>.
- **Issues:** <GitHub Issues, as *Roadmap* describes: review follow-ups and
  ideas are filed as issues, a project or maintenance chunk may start from
  one, and the pull request that finishes it closes it. | none: follow-ups
  live in the status file>.
- **Authority:** <the docs that define behavior, in order, e.g.
  `docs/spec.md`, then `docs/design.md`; `docs/README.md` gives the reading
  order. | `README.md` and the code's own documentation>.
- **Status:** `docs/status.md`
- **Chunks:** `docs/chunks/<ID>.md`
- **Decision log:** `docs/decisions.md`, entries cited as `(DEC-n)`
- **Review checklist:** `docs/review-checklist.md`
- **Brief checklist:** `docs/brief-checklist.md`
- **Projects:** `docs/projects/` (`index.md`, `template.md`, one
  `P####-slug.md` per project)
- **Tools:** `tools/`, review aids run by hand, outside the gate and the build
- **Review extras:** <none | repo-specific checks every review runs>.
- **Environment:** <none | what a session must set up first>.
