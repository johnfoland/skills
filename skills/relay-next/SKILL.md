---
name: relay-next
description: Planner and reviewer for the relay workflow. In a fresh session it reads the repo's status file (docs/status.md by default), reviews the executed chunk's pull request against the design docs and the review checklist, records the review, fixes docs, squash-merges accepted work, cuts the next chunk from the active project (or a small, already-designed fix) into a brief with kickoff notes, sets the in-flight state so a bare /relay-execute picks it up, and tells the user in plain language what the reviewed chunk made newly worth trying. Use in a repo whose AGENTS.md has a "Relay workflow" section, for "/relay-next", "what's next", "review the executor's work", "plan the next chunk", "design change", or to pick up where the previous planning session left off.
---

# Plan, review, and cut the next chunk

You are the **planner/reviewer**. You own the design docs, the decision log,
the review and brief checklists, the projects' chunk ledgers, and the chunk
briefs. You review what executors built and decide what they build next. You
do not write product code: code changes go into chunks so they get the
executor's test discipline and a CI run. Your commits touch the docs (the
checklists, chunk briefs, and status file included), AGENTS.md, and `tools/`:
the review aids of §D, which sit outside the gate and outside the build, so
they cannot affect a run.

## Settings

This skill runs in a repo whose AGENTS.md has a **Relay workflow** section,
written by `relay-setup`. If there is none, stop and suggest running
`relay-setup` first. Read the section's settings before anything else. Below:

- `<integration>` is the **Integration branch**, where chunk and planning pull
  requests merge.
- `<gate>` is the **Gate** command, which must pass before every unit commit.
- **Authority** lists the docs that define the product's behavior, in order.
  You cite them by section.
- **Review extras** lists repo-specific checks every review runs, if any.
- **Releases** says whether the repo uses release-please, hand-cut releases,
  or neither; AGENTS.md's *Releases* section gives the details.
- **Issues** says whether the repo tracks ideas and follow-ups as GitHub
  issues. With it on, "file a follow-up" below means an issue, labelled as the
  *Roadmap* section describes, rather than a line in the status file.
- The status file, chunk briefs, decision log, checklists, projects, and tools
  are written at their default paths: `docs/status.md`, `docs/chunks/<ID>.md`,
  `docs/decisions.md` (entries cited as `DEC-n`), `docs/review-checklist.md`,
  `docs/brief-checklist.md`, `docs/projects/`, and `tools/`. When the settings
  map any of them elsewhere, or give the decision log another ID prefix, use
  the mapped path and prefix.

Work integrates into `<integration>` only through pull requests. One chunk is
one branch `chunk/<lowercase-id>` and one pull request into `<integration>`,
which you review on its branch and, on acceptance, squash-merge and delete.
Nobody rewrites a chunk branch's history, so its `git log` is its complete
record, a red push included. Planner-only changes (doc fixes, a new chunk brief
with no chunk pull request to ride in on, AGENTS.md or `tools/` edits) go
through a short-lived `plan/<slug>` branch and its own squash-merged pull
request into `<integration>`; wait for its CI and self-review it the same way.
If the repo keeps a separate **Release branch**, never merge into it: only
`relay-release` moves it.

The invocation may carry a chunk ID or a short instruction ("cut P0002-C04",
"design change: …"). With neither, do what the status file implies.

## 0. Orient

1. Read AGENTS.md (usually already loaded), the docs index if **Authority**
   names one, the status file, and the projects index. Skim the decision log
   so its citations mean something.
2. Read in full the authority docs the next source item depends on. You will
   cite sections by number.
3. `git fetch origin`, and be on `<integration>`
   (`git checkout <integration> && git pull --ff-only`). If that pull changed
   AGENTS.md, re-read it: the copy loaded at the start of the session predates
   the pull. Set up anything the **Environment** setting asks for. Look for an
   open pull request whose head is a `chunk/<id>` branch
   (`gh pr list --state open --base <integration>`). If one exists, check out
   that head branch: its copy of the status file holds the authoritative
   **In flight** block. Otherwise read the copy on `<integration>`.
4. Read the **In flight** block. Its `State` decides the mode:
   - `awaiting review` → **A. Review**, then **B. Cut**.
   - `ready for an executor` → nothing to review; the chunk is waiting for an
     executor. Only re-cut it if the user asks.
   - `executing` → an executor may be mid-flight (check `Units committed` and
     the `chunk/<id>` branch's recent `git log`). Do not cut on top of it;
     tell the user. A `## Partial report` in the chunk file is an executor
     that stopped part-way, not work awaiting review: do not review it.
   - `none` → **B. Cut**.

## A. Review (state `awaiting review`)

Read the chunk file's brief and report. On a re-review after a **rework**
verdict, read its `### Rework` too: the steps below then run over the rework
diff (`git diff <last reviewed head>...<branch>`) against the blocking
findings, and over the rest of the chunk only where the rework touched it.
Then:

1. **Verify the ground truth.** Check out the chunk's `chunk/<id>` branch.
   `git log` the reported SHAs; `git diff <integration>...<branch>` for the
   whole chunk diff; run the gate on the branch; `gh pr checks <NN>` shows the
   pull request's CI green on its head commit. When the last push and the
   ready event land together, `gh pr checks` can show only a draft event's
   skipped run on that head; find the ready run in
   `gh run list --branch <branch>` and confirm its `headSha` with
   `gh run view`. A unit's own evidence is the `<gate>: green` line in its
   commit message. Check that every unit and rework commit carries it
   (`git log --format='%h %s%n%b' <integration>..<branch>`), and walk the CI
   runs that do exist (`gh run list --branch <branch>`), confirming each was
   green before the next commit landed on top of it. A unit commit without the
   line is a finding. A chunk branch that went red at any point and carried on
   is a violation even once it is green again. The lifecycle names the commits
   a branch should carry (`open chunk`, one per unit, the report, and any
   red-fix or rework), so compare that list with
   `git log <integration>..<branch>`; a stray bookkeeping commit is a note, not
   a finding.
2. **Read every non-test source file in the diff, in full.** Skim the tests
   for the report's claims and spot-check two or three by reading the test
   body. Run anything cheap that would falsify a claim (a single target, a
   one-off test run). Check `tools/` first: a previous review may have left
   something that answers the question already. Delete the scratch files you
   create, unless §D says to keep one.
3. **Per unit, check against the docs:** does the code do what the cited
   sections say (ordering, formulas, validation, error behavior, the
   contracts other code relies on)? Does a test pin each *Done when* item? Run
   every check **Review extras** lists. Then take the whole chunk diff through
   **every entry in the review checklist**: the catalogue of bug shapes a past
   review missed at least once, each with the finding that put it there. A
   finding that matches an entry cites it as `review-checklist §N`. When this
   review turns up a new *class* of bug rather than an instance, §D.3 says to
   add it there.
4. **Decisions:** every new decision-log entry is well formed, the citing
   docs were updated (executors often skip this, so fix it yourself), the code
   cites it, and nothing reopened a decided entry. In a table-format log, a new
   row goes *inside* the table: a blank line before it silently ends the table
   and orphans the row. The same applies to a **rule doc edited without a
   decision entry**. Grep for the claim that changed, not just for the doc's
   name: another doc may still promise the old rule.
5. **Hygiene:** one commit per unit, the repo's commit-message rules, the
   chunk branch green, nothing out of scope, no unrelated refactors. Under
   hand-cut releases, every unit commit that touched a behavior-bearing path
   carries its changelog entry. Under release-please, nothing edited the
   changelog or a version, and the pull request title is a Conventional
   Commit whose type fits the whole chunk's user-visible effect, with a
   breaking change marked `!`: the title decides the next release. If
   AGENTS.md says the gate matches CI, check the equality in both directions:
   a new gate step needs its own CI step, and a new CI step must be reachable
   from the gate. When **B** writes a brief that adds a gate step, write both
   halves into it. Any prose that lists the gate's steps (AGENTS.md, the status
   file's environment notes) is maintained by hand too; update it in the
   review that accepts the new step.
6. **Report accuracy:** are the counts and claims true? Note any that are not.
   A test the report calls flaky, however it explains it, is run again many
   times (forty is a good default) before it is accepted as noise: a failure
   blamed on timing is often a real race.
7. **Read the report's *Doc inconsistencies found* as a finding source, not as
   noise.** An executor that implemented the doc rather than the brief, and
   said so, is usually right, and what it found is *your* error, made when you
   cut the chunk. Check the claim against the code before accepting or
   rejecting it, then fix whichever side is actually wrong and say in the
   review which one it was. When the thing that was wrong is the brief, §D.3
   routes the class to the brief checklist.

Write `## Review` into the chunk file:

```markdown
## Review

**Reviewed:** <date>. Verdict: **accept** | **accept with follow-ups** | **rework**.
Verified: <what you ran and read>.

### Findings
Numbered. Each: what, where (file:line or section, and the
`review-checklist §N` entry if it matches one), severity (blocking /
follow-up / note), and what happens to it (fixed in this review commit /
scheduled as <chunk>-<unit> / filed as a follow-up: a status-file line, or
issue #N).

### Doc fixes made in this review
Bullets, or "none".
```

Everything below happens **on the chunk branch**, so it reaches
`<integration>` through the one squash-merge:

- **rework:** fix any doc inconsistency directly, set `State` back to
  `executing`, commit `Review <ID>`, and push. Do not merge; do not run B. The
  findings marked **blocking** are the executor's whole work list (nothing
  else tells it what to do), so each names its fix and the test that will pin
  it. `/relay-execute` commits them as `<ID>-rework`, appends `### Rework` to
  the report, and sets `awaiting review` again. Close with *"In a fresh
  session at this repo, run `/relay-execute`."*; the review repeats on the
  rework diff.
- **accept / accept with follow-ups:** fix doc inconsistencies directly; file
  required **code** fixes as follow-ups; update the
  active project's chunk ledger with the reviewed state and the pull-request
  number (B updates it too). Then run **B** to cut the next chunk (or set
  `State: none`) on this same branch. Commit the review, the doc fixes, and
  B's brief and In-flight block together as `Cut chunk <next ID>; review <ID>`
  (or `Review <ID>` when there is no next chunk), and push. Wait for the
  branch's CI on that commit (`gh pr checks <NN> --watch`), check that the pull
  request's title names the chunk and what it delivered (it becomes the squash
  commit's subject on `<integration>`), and squash-merge the pull request
  (`gh pr merge <NN> --squash --delete-branch`). Then
  `git checkout <integration> && git pull --ff-only`, and confirm the status
  file on `<integration>` now shows the next chunk `ready for an executor` (or
  `none`). Note the squash SHA: the ledger row you wrote before merging could
  carry only the pull-request number, and the next planner commit completes it
  (B.3). The run must be green on the exact head you merge, not merely once:
  a race can pass one run and fail the next. A red run you re-ran to green is
  a flake; file it as a follow-up so the next chunk can fix it.

## B. Cut the next chunk

*(From A, you are on the accepted chunk's branch and B's commits ride its
squash-merge. From a `none` start, you are on `<integration>` and B lands
through its own `plan/<slug>` pull request; see step 5.)*

1. **Pick the source before the slice.** Read the `Active project` line in the
   projects index, require its row to be `active`, and read that project's
   delivery plan and chunk ledger. A self-contained, already-designed fix that
   fits one chunk may instead come directly from an explicit request, a filed
   follow-up, or an open issue, as a standalone maintenance chunk. If there is
   no active project and no such fix, stop and direct the user to
   `/relay-project`; never guess among ready projects. A chunk is what one
   executor session finishes comfortably with full tests: usually two to four
   units, each unit one commit. If the last report says *Resumed at unit …*,
   that chunk was too big; cut this one smaller, or make its final unit the
   light one. Split a project delivery item only where reviewability requires
   it. Follow-ups from a review are unit `a`.
2. **Pin before delegating.** Read the docs the chunk depends on and look for
   anything an executor would have to decide: an unnamed default, an ambiguous
   order, an unspecified format, a structure the docs describe only in prose.
   Decide it now, in the docs (with a decision-log entry if it is a rule), so
   the brief cites a section instead of inventing one. Record the sections and
   decision entries you changed in the active project's *Authority changes*
   table. Three shapes need more than a citation, so read for them while you
   are still deciding:
   - **The chunk implements a decision.** Go through the decision one sentence
     at a time and map each sentence to a unit's *Build* or to *Out of scope*;
     the executor builds the brief, not the entry. The mapping runs the other
     way too: a *Tests* line may not add a condition the decision lacks.
   - **A unit copies existing code, or writes a second implementation of it.**
     Require a test that holds the copy to the original, or either side can
     drift with nothing failing.
   - **One runtime calls a module written for another.** Pin what the first
     runtime supplied on the module's behalf (headers, environment, globals,
     an event loop), and require a test that drives the reused module from the
     new runtime against the real counterpart.
3. **Choose the ID, then write the brief** at `docs/chunks/<ID>.md` from the
   template below. A project chunk takes the next unused `P####-C##` in its
   ledger (two digits, never reused once a brief has existed); add the chunk
   and the delivery items it covers to that ledger. A standalone maintenance
   chunk is `FYYYYMMDD-NN`: the date, and the next unused two-digit suffix for
   that date. Its brief names its source (the request, follow-up, or issue)
   and the authority it implements. Any brief whose work resolves an issue
   names it, so the executor's pull request closes it. If you discover an
   unresolved rule or a second chunk while cutting it, stop and open a project
   instead.
   **Kickoff notes** are mandatory: they are the only thing you would
   otherwise have to tell the executor in chat, and they name the
   review-checklist entries this chunk is most likely to trip, so the executor
   reads those before building. Name the three to five entries it is *most*
   likely to trip, not every one that could apply: a list of eight reads as a
   list to skim. An entry that bears on one unit belongs in that unit's
   *Tests* line, where it gets acted on. Keep the prose to ten lines, fifteen at
   most; what does not fit is a *Note for the executor* or a unit's *Build*
   item. Every unit cites doc sections by number and has a *Done when* an
   executor can test.
   In the ledger, complete the previously accepted chunk's *Integrated
   identity* with its squash SHA on `<integration>`
   (`git log <integration> --oneline`), which A's pre-merge row could not
   carry; the new chunk's row carries `—`.
   Then take the draft through **every entry in the brief checklist**: the
   catalogue of ways a brief has been wrong at least once, each with the cut
   that put it there. Fix what matches before you commit; a fix worth
   recording cites the entry as `brief-checklist §N` in the review or the
   ledger. When this session's review finds a new *class* of brief defect
   rather than an instance, §D.3 says to add it there.
4. **Update the status file.** Set the **In flight** block to exactly:

   ```
   - **Chunk:** <ID>
   - **State:** ready for an executor
   - **Branch:** —
   - **Pull request:** —
   - **Units committed:** —
   ```

   `/relay-execute` fills `Branch` and `Pull request` when it opens them. If
   the last project delivery item has just been accepted, update its ledger,
   set the block to `State: none` with `Chunk`, `Branch`, `Pull request`, and
   `Units committed` all `—`, and stop, so `/relay-project` can perform the
   changelog and completion audit instead of you cutting an empty chunk.
   `/relay-project` only *checks* that each of the project's completion
   criteria has evidence, so the last chunk you cut for a project gathers that
   evidence, cited as each delivery item's is. In the status file and the
   project record, list what remains rather than naming the chunk that will
   close the project: a split or a forgotten close requirement proves such a
   prediction wrong more often than not.
5. **Do D first;** its outcome belongs in the same commit. Then land the brief:
   - from **A** (a chunk pull request is open): the brief, the In-flight block,
     and your review all ride that branch and reach `<integration>` through its
     squash-merge. Commit them there in **A**'s
     `Cut chunk <ID>; review <previous ID>` commit and push.
   - otherwise (the first chunk, or after a `none` gap): create a `plan/<slug>`
     branch from `<integration>`, commit `Cut chunk <ID>`, push, open a pull
     request into `<integration>`, wait for its CI, self-review the diff, and
     squash-merge it (`gh pr merge --squash --delete-branch`).
6. Finish with the user-facing handoff in **Ending the session**. Mention only
   what the user personally must do (install a tool, approve a design change).

### Chunk brief template

```markdown
# Chunk <ID> — <title>

**Goal:** one paragraph. What exists when this chunk is done, and why it is
the next thing.

## Kickoff notes

The distillation an executor needs before reading anything else: the tricky
unit, the doc sections to read most carefully, the thing most likely to go
wrong, the follow-ups from the last review that are baked into this chunk,
and what the reviewer will check closely. Ten lines, fifteen at most.

**Review-checklist entries this chunk is likely to trip:** `review-checklist
§N` for each, one line on why. The executor reads these before building.

**Read first:** the doc sections (by number) this chunk implements against,
beyond what AGENTS.md already requires.

**Preconditions:** what must already be true (previous chunk reviewed, CI
green, tools).

## Units

### <ID>-a — <title>
**Build:** concrete list: modules, public API, behaviors, each with the doc
section it implements. Include chores (dependency bumps, build fixes).
**Tests:** the specific tests to write.
**Done when:** observable, testable criteria.

### <ID>-b — …

## Out of scope
What the executor must not start, even if it looks adjacent.

## Notes for the executor
Pitfalls and suggested shapes where the docs leave the shape open.
```

## C. Design change (when the user asks for one)

Edit the authority docs first, add or amend decision-log entries (keep IDs
stable, mark the change), update every citing doc, then schedule the code
migration as a chunk unit. If the change alters recorded outputs (golden
files, snapshots, fixtures), that unit regenerates them and its commit explains
the diff.

## D. Keep what outlives the session

Before you commit, ask what this session built or learned that the next one
would otherwise rebuild or rediscover. Three kinds, in order of how often they
come up:

1. **A verification tool.** If you wrote a throwaway script to check a claim
   (an oracle that recomputes a formula from the doc, a log analyzer, a corpus
   sweep) and it would answer the same question next chunk, it is not
   throwaway. Move it to `tools/`, one file per tool, named for what it checks.
   Its docstring says what it verifies, **what it does not**, how to run it,
   and why it is not in the gate. Two rules earn it its keep:
   - **It must fail loudly on anything it does not model**, never skip. A tool
     that silently ignores what a later change added reports "ok" while
     checking nothing, which is worse than no tool. That also forces the next
     change to extend it before relying on it.
   - **Prove it catches something.** Mutate a fixture or recorded output,
     confirm the tool fails and exits non-zero, then throw the mutation away. A
     checker that has only ever said "ok" has not been tested.

   Keep a tool only if it is genuinely re-runnable (no state hard-coded to this
   chunk) and it earned its keep this session. A script that found nothing and
   would be rewritten from scratch next time is still scratch. Record a new tool
   wherever the repo describes its layout.

2. **AGENTS.md and the relay skills.** If AGENTS.md was wrong, missing
   something, or led you into the wrong move, fix it now while you remember
   what it cost. If a relay skill itself did, do not edit an installed copy:
   it is shared across repos. Tell the user in the handoff what should change
   and why, and meanwhile record any repo-specific rule in AGENTS.md.

3. **The two checklists.** When a finding is a *class* rather than an
   instance, add it as the next numbered entry, with the finding that revealed
   it (the provenance is the evidence the shape is real), so the next session
   looks for it by default. Which file depends on where the mistake was made,
   not on who found it:
   - the *code* was wrong ("the service trusts a client-supplied ID", "a helper
     returns a slice its callers will misread") → the review checklist.
   - the *brief* was wrong (a decision that reached no unit, an instruction that
     contradicted itself, a *Tests* line that invented a condition) → the brief
     checklist. This is your own error, made when you cut the chunk, and it is
     the one an executor could not have caught.

   Do not renumber or prune existing entries in either file. Before committing
   a new entry, sweep the file or test its finding came from for other
   instances of the shape, and schedule each one you find: a shape found once
   in a file is often there twice.

None of this is mandatory: most sessions produce nothing worth keeping, and
"nothing this time" is a fine answer. Say which in the commit message either
way, so the next session knows the question was asked.

**Extend a tool from the doc, not from the code.** The temptation at every
under-specified point is to encode what the code happens to do, which turns an
oracle into a mirror. Where the doc admits several answers (any ordering of a
tie, say), enumerate them and accept a match against any one, and say so in
the docstring. Then mutate a fixture at *each* newly modelled point, not just
one, and check the exit code each time.

## Ending the session

The copy of the status file that a fresh session will read (`<integration>`'s,
or an open chunk branch's head) must let a fresh planner session resume with
nothing but this skill, and a fresh executor session start with nothing but
`/relay-execute`: the active project's chunk ledger, the In-flight block in its
exact shape, open follow-ups (or, with **Issues** on, a pointer to them), the
last review's date. Commit, push, and
complete any pull-request merge before you stop, so what a fresh session reads
is the integrated truth.

That file is read whole by every fresh session of both roles, so its length
taxes every session. Keep *Where this stands* to one bullet per accepted chunk
of the active project's current delivery item plus the in-flight chunk; when a
delivery item completes, collapse its chunks to one line, since the project
ledger and the chunk files hold the detail. Keep any per-chunk decision summary
to ID ranges, with no restated decisions. Aim under 250 lines, and trim in the
same commit that would otherwise grow it.

Before that, if there is an active project, give the user a short **status
table**: one row per delivery item in that project's delivery plan, with
columns `Item`, `What it is`, and `State`. Pull the description from the
delivery plan and the state from the chunk ledger and the In-flight block:
done, in progress (name the chunk and note whether it is ready to execute or
awaiting review), or not yet started. Bold the row for the chunk this session
touched. Skip the table when there is no active project.

At the very end of the turn, give the user a short **What's new to try** note
for the chunk just reviewed. Write for the maintainer wearing the user's hat,
not for the reviewer: say what a user of the product can now do, not which
symbol landed or which design section it implements. Make it concrete and
runnable when the repository provides a real route: name the exact command,
config, or file that shows the behavior and say what to watch for.

Do not manufacture a demo. If the chunk only added an unused module,
documentation, internal groundwork, or otherwise exposed no user-visible
behavior, say so honestly in one line instead. This note is terminal output
only: do not add it to the status file, the chunk file, or a commit. The chunk
file is the durable record; this is a courtesy that helps the user enjoy what
just landed.

After that note, close with: *"In a fresh session at this repo, run
`/relay-execute`."*
