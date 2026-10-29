# Skills Design

## Overview
The agent is controlled by four Skills and a short manifest instruction. The manifest instruction is shown on every model call, so it carries the rules that must never be lost: the five official tools, the role of each Skill and the routing between them, never calling `new_game` when a `session_id` exists, printing `SESSION_ID=<id>`, printing the ending payload followed by `DONE`, and never stopping early. The Skills hold the detailed procedures. Each Skill has one owner role, so the agent never has two Skills deciding the same thing.

## Skills and responsibilities

### `career-survival-core` (protocol and execution)
- **Owns:** starting or resuming one session, reloading after a context reset, routing each observed phase to its Skill, executing every game action exactly once, handling rejected actions, and reporting the ending. It also keeps the overall priorities (avoid early failure, balance the ending dimensions, sustained growth, wealth through progress) and the note rules (one note under 300 characters), including the carried status of an unresolved accumulated-risk concern.
- **Information it uses:** `observe`, error messages, `check_latest_logs` on recovery, and the public handbook.
- **Output:** the executed action and a compact note. The specialist Skills choose; the core executes.

### `decision-mind` (judgment for events)
- **Owns:** what counts as pressure (for Network, Skill, Output and Wealth: decline across several observations or an explicit warning, not a small stable value or a C grade alone; for Health and Dignity: an explicit warning, a severe condition or sustained deterioration), when to use a brief decision versus a short written comparison (only for an unresolved warning, a gamble-type option or genuine Health or Dignity pressure), judging future consequences rather than persuasive wording, and cautious learning from feedback.
- **Information it uses:** the current state, the handbook, the offered choices and this run's feedback.
- **Output:** the judgment that `event-choice-evaluation` applies to a choice.

### `event-choice-evaluation` (monthly events)
- **Owns:** every monthly story event and follow-up. It reads every choice, translates wording into uncertain effects with a short cue table, checks the strongest alternative with `decision-mind`, and treats money or visibility opportunities as worthwhile only when the credible benefit exceeds an affordable, recoverable cost.
- **Information it uses:** the full situation text, every choice, the current state and earlier predictions.
- **Output:** the exact choice number, a short trade-off and a predicted effect, returned to the core.

### `quarterly-planning` (quarter end and promotion)
- **Owns:** the 3 Energy points and the main action, aimed at the next promotion after feasible responses to unresolved safety threats. Both phases explicitly consider carried accumulated-risk warnings before optional growth, while balancing more immediate failure threats.
- **Information it uses:** each action's cost and effects as listed on screen, the current statistics, values recorded in earlier quarter-end notes, the review months and review results.
- **How it decides:** it labels the quarter SPRINT (a review is within three months), RESET (a review just happened) or FINAL (no review left). Areas that stopped rising despite effort are treated as satisfied for now; areas an event knocked down come first. Most Energy goes to the dropped area or the hardest remaining gap, Health and Dignity are kept in the upper half during the run (the team's own margin) and raised to 10 only in the final quarter, Health- or Dignity-costing actions are taken only in a SPRINT quarter when both are in the upper half, and in the final quarter only what the ending counts is bought. Each quarter note records Skill, Network, Output, Health and Dignity so the next quarter can compare.
- **Output:** a quarter plan, one action per turn through the core, and a one-line quarter note.

## How the outputs combine
1. The core observes the state and routes the phase.
2. For a monthly event, `event-choice-evaluation` prepares the options and `decision-mind` judges them. For a quarter end, `quarterly-planning` builds the plan.
3. The core executes the chosen number with one compact note.
4. On the next observation the agent checks what actually changed, and the notes carry the plan and the review results across turns and context resets.

## What the agent does not use
- Any internal package, database, hidden state or evaluation data.
- Event names, memorised sequences or lookup tables.
- Any number presented as a simulation rule. Caution margins are labelled as the team's own. Action effects are read from the screen each time, never remembered.
- Scripts or reference files.
