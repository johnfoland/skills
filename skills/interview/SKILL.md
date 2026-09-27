---
name: interview
description: Clarify a request before acting on it by interviewing the user through the harness's structured AskUserQuestion tool. Use this proactively and err toward using it. Reach for it at the start of any non-trivial task (a new feature, project, script, document, design, refactor, or migration) whenever the request allows more than one reasonable reading; whenever it is missing who it is for, why, what done looks like, or constraints; whenever it is vague ("make it better", "add auth", "clean this up") or so conventional that the obvious reading may not be the whole story; before writing a plan; and mid-task when you reach a fork the request did not settle. Also use it when the user says "interview me", "stress-test this", "grill me", or "ask me some questions first". Skip it only for fully specified, bounded requests, trivial one-step tasks, plain questions, or when the user has said to just proceed.
---

# Interview

Close the gap between what the user *asked for* and what they actually *need* — before planning or writing code.

## When to use

Default to interviewing. A batched round of questions costs the user seconds; building the wrong thing costs far more. Trigger this skill when any of these hold:

- The task is non-trivial — a new feature, project, script, document, design, refactor, or migration — and you have not yet confirmed what the user has in mind.
- The request omits key context: who it is for, why now, what "done" looks like, or hard constraints (stack, budget, deadline, compatibility).
- The request is vague ("make it better", "add auth", "clean this up") or so conventional that the obvious reading is probably not the whole story.
- You are about to pick between two reasonable interpretations, or fill in a default the user might care about (naming, scope, UX, architecture, audience, tone).
- You are about to write a plan, or about to start something expensive to undo.
- Mid-task, you reach a fork the original request did not settle.
- The user explicitly asks to be interviewed, or to have their thinking pressure-tested.

Skip it only when the request is already specific and bounded, when the user has said to just proceed, for trivial one-step tasks, or for questions that only need an answer. When unsure whether it applies, run one short round.

## How to run the interview

### 1. Find the gaps

Before asking anything, list — to yourself — what you'd need to know to do this well and what you're currently guessing. Group the unknowns. Each group becomes one question.

### 2. Ask through `AskUserQuestion`

Put every question through the `AskUserQuestion` tool. Batch related questions into a single call (up to 4) so the user answers them together rather than in a slow back-and-forth.

For each question:

- **2–4 options, never more.** More than four is decision paralysis; collapse near-duplicates.
- **Lead with your best guess, marked `(Recommended)`**, and let the option's `description` carry a one-line reason you think it's the answer. The other options are real alternatives, phrased neutrally — not strawmen.
- **Self-explanatory labels.** The user should not have to open the description to understand the choice.
- **One concern per question.** If an option needs "and also…", it's two questions.
- The tool always offers a free-text "Other" — rely on it as the escape hatch. Only add an explicit "Skip / doesn't matter" option when skipping is a meaningful answer.

### 3. Fall back to prose for genuinely open questions

Some things have no option set — a product name, a description of the vision, a paste of an error. Ask those as a short plain-text question instead of forcing fake options into `AskUserQuestion`. Keep it to one or two at a time.

### 4. Predict, then stop

After each round, state — briefly — what you now believe the user wants and what you'd still guess at. Ask another round only if a remaining unknown would actually change what you build. When you can predict the user's answers before they give them, stop interviewing and summarize:

> Here's what I understand you want: … Here's what I'm still assuming: … Ready to proceed?

Then wait for a go-ahead before acting.

## Notes

- Prefer one 3–4 question `AskUserQuestion` call over three separate calls.
- Recommended-first is a bias toward momentum, not a nudge toward your convenience — if you genuinely don't have a best guess, say so and present the options flat.
- The interview is done when more questions would only refine details you could safely decide yourself.
