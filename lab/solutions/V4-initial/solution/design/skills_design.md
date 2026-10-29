# Skills Design

## Principle
The designated model follows short, explicit rules well and long reasoning procedures poorly. Each Skill therefore has one job and the same shape: role, task, a short CRITICAL block, numbered steps, a cue table where needed, the note format and one invented example. The most important rules are repeated in the manifest instruction, which the agent sees on every call.

## Skills and responsibilities

### `career-survival-core`
- **Owns:** starting or resuming one session (never a second `new_game`), the observe-decide-act loop, routing each turn, rejected actions, the ending (`ending_score` then `DONE`), the overall priorities and the one-line note.
- **Information it uses:** every `observe` result, error messages, and earlier notes through `check_latest_logs` after a reset.
- **Output:** the executed action and a note: month, level, the six statistics, a risk flag (`none`, `mild` or `serious`, read from the monthly feed), the reason and the plan. The note is the agent's memory between turns and after a reset.

### `event-choice-evaluation`
- **Owns:** every monthly story event and follow-up.
- **Information it uses:** the full situation text, every choice, the current statistics and the review months.
- **How it decides:** it writes a short effect line per option from a wording-cue table, removes options that hide a problem, mislead, blame someone unfairly or skip a required check, then chooses in a fixed order: protect a low Health or Dignity; avoid losing Output, Network or Dignity in the two months before a review; otherwise take the most growth for a small, recoverable cost; break ties in favour of honest, fact-gathering options. Options are judged by their content, not their position.

### `quarterly-planning`
- **Owns:** the 3 Energy points and the main action at each quarter-end.
- **Information it uses:** the costs and effects listed on screen, the statistics, and the risk flags in the notes since the last quarter-end.
- **How it decides:** a serious risk flag forces the risk-lowering Energy action and main action; repeated mild flags trigger one risk-lowering action. It never buys a Health or Dignity action for a statistic already at 10. The default plan builds Output and Network with Energy and takes the broad-growth main action; it adjusts when a statistic is low, when a paid-for statistic did not rise, or when Skill falls behind. In the final quarter it spends only on what the ending counts.

## How the outputs combine
1. The core observes, sets the risk flag and routes the turn.
2. The event or quarter Skill chooses the number.
3. The core executes it once, writes the note and observes again.
4. The notes carry the statistics and risk flags from turn to turn.

## What the agent does not use
- Any internal package, database, hidden state or evaluation data.
- Event names, memorised sequences or lookup tables of events.
- Any number presented as a simulation rule. The "3 or below on the 0 to 10 range" margin for Health and Dignity is labelled as the team's own. Action effects are read from the screen each time.
- Scripts, reference files or multiple agents.
