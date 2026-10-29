# Skills Design

## 1. Design principle
The designated model is fast and inexpensive, so it follows explicit procedures much better than general advice. We therefore split good judgement into two layers:
- **Character (System 1).** A stable personality, described with the Big Five model, sets the default behaviour on routine turns.
- **Procedure (System 2).** A written, step-by-step comparison is forced whenever a decision is risky or important.

Each Skill has one responsibility, and every shared definition lives in exactly one place, so the agent never sees two different versions of the same rule.

## 2. The manifest instruction
The runner shows the manifest instruction to the agent on every model call, and it survives context compression. It therefore carries only what must never be lost: a short persona, the role of each Skill, the five official tools, the rule never to call `new_game` when a `session_id` exists, printing `SESSION_ID=<id>`, printing the ending payload followed by `DONE`, never stopping early, and the fair-play rules. Everything else lives in the Skills.

## 3. The four Skills

### `career-survival-core` (the body)
- **Responsibility:** keeping the run alive mechanically. Starting a game, resuming after a context reset (never a second `new_game`; recover from `observe` and `check_latest_logs`), recognising the phase of each turn (story event, follow-up, Energy allocation, main action, review result, warning), the turn loop, rejected actions, the ending, and tool discipline.
- **Information used:** the output of `observe`, error messages, and the agent's earlier notes returned by `check_latest_logs`.
- **Output:** which phase this is and which Skill to apply. It makes no strategic decision itself.

### `decision-mind` (the brain)
- **Responsibility:** how every decision is made.
  1. Character as behaviour.
  2. A pressure check that defines when a stat is "under pressure" or has a "safe margin" (our own caution lines, labelled as such).
  3. Fast or slow: seven triggers force slow thinking.
  4. The slow procedure, steps A to H: translate options into stat effects, simulate the likely, bad-case and month-48 futures, rate the risk, ruin filter, dominance, long-term value, tie-breaks, verify before acting, record.
  5. Bias checks.
  6. The long-term frame: eight six-month cycles, each a build quarter then a prove quarter, across Foundation, Convert and Harvest phases.
  7. Relationships as a repeated game.
  8. Learning after each action.
  9. Worked examples (invented and labelled as such).
  10. The ledger note format.
- **Information used:** the current statistics and their trend, warnings, review results, and the agent's lessons from earlier in the run.
- **Output:** the chosen option, a prediction of its effect, and one ledger line that serves as memory.

### `event-choice-evaluation` (the eyes)
- **Responsibility:** monthly story events, which are most of the turns. Event choices are written in words without numbers, so this Skill provides a table of general workplace language cues. For example, "extra hours" suggests Output up and Health down, and "signing without reading" suggests hidden risk. These cues fill step A of `decision-mind`. In-run lessons override the cues.
- **Information used:** the monthly feed, the full situation text, every choice, and whether the situation follows up an earlier one.
- **Output:** one choice number, chosen through the `decision-mind` procedure.

### `quarterly-planning` (the planner)
- **Responsibility:** the quarter-end phase, the strongest long-term lever. It decides whether this is a build quarter, a prove quarter (a review is due within three months) or the final year. It then applies:
  - the cap rule: never spend Energy on a stat already at its maximum;
  - the buffer rule: a safe margin is spent in build quarters and restored before reviews;
  - growth balance: give priority to whichever of Skill, Network and Output grew least;
  - risk hygiene: schedule "Defuse legacy risk" after risky actions.
  Skill learning is the default build-quarter action, High-intensity work is restricted because it raises hidden risk, and the same plan is not repeated for more than two quarters. It picks one of the allocation templates and a main action, plans the whole quarter first, then executes one action per turn. Consecutive Energy actions may be chained without a new `observe` to save calls.
- **Information used:** the published action effects, the action descriptions shown in the interface (which take priority), the pressure check, the next review month recorded in the notes, and in-run lessons.
- **Output:** a quarter plan in the ledger note, then one action per turn.

## 4. How the outputs combine into one decision
1. `career-survival-core` observes the state and identifies the phase.
2. The phase Skill (`event-choice-evaluation` or `quarterly-planning`) prepares the options: it translates the wording or selects a template.
3. `decision-mind` runs the pressure check, chooses fast or slow thinking, filters out ruinous options and picks the best long-term value.
4. The agent verifies the choice number and calls `take_action` with one ledger line.
5. On the next turn it compares its prediction with the real change and records a lesson if they differ.

The ledger line (month, level, cycle, all six statistics with their trend, the pressure list, the choice, the prediction, the plan and the next review month) carries the strategy across turns and across context resets.

## 5. What the agent does not use
- No internal package, database, hidden state or evaluation data.
- No event names, memorised sequences or lookup tables of events.
- No number presented as a simulation rule. The caution lines ("lower third", "upper half", "two observations in a row") are the team's own margins, and the Skills say so. The only numbers stated as facts are published ones: the 0 to 10 ranges, the 48 months, quarters, six-month reviews and grade meanings.
- No scripts or reference files.
