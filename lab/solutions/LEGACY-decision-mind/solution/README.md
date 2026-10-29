# Winning team - Decision Mind Agent

This submission is a Career Survival Agent for JiuwenSwarm 0.2.4b3 in single-agent mode (`"mode": "agent"`). It plays the full 48-month simulation through the five official MCP tools only: `new_game`, `observe`, `take_action`, `check_latest_logs` and `show_employee_handbook`.

The agent is built around one idea: a cheap model makes better decisions when good judgement is written down as character plus procedure. A stable character (described with the Big Five personality model) sets its default behaviour on routine turns. A forced, written procedure (System 2 thinking) takes over whenever a decision is risky or important. Every decision is judged by one question: which option leaves the career best placed at month 48?

The agent decides only from the public handbook and from what the simulation returns during the current run. It contains no event-specific answers, no memorised sequences and no unpublished thresholds.

## Skills
| Skill | Role | Purpose |
|---|---|---|
| `career-survival-core` | The body | Run protocol: start or resume a game, recognise the phase of each turn, the turn loop, rejected actions, the ending, tool discipline. |
| `decision-mind` | The brain | Character, pressure check, fast or slow thinking, written simulation of each option's futures, ruin filter, dominance, long-term value, bias checks, learning after each action, and the ledger note used as memory. |
| `event-choice-evaluation` | The eyes | Monthly story events: turns the wording of each choice into likely stat effects and risk, then applies the `decision-mind` procedure. |
| `quarterly-planning` | The planner | Quarter-end phase: build or prove quarter, the cap and buffer rules, growth balance, risk hygiene, allocation templates for the 3 Energy points, and the main action. |

Each shared definition (what counts as pressure, the phases of the run, the note format) lives only in `decision-mind`, and the other Skills refer to it. There are no scripts and no reference files: the design needs only instructions and the official tools.

## Files
- `manifest.json`: team, submission name, mode, and the short instruction shown to the agent on every call (persona, Skill roles and protocol rules).
- `design/skills_design.md`: how the four Skills divide responsibilities and combine into one decision.
- `design/decision_report.md`: the decision approach, its foundations, the information it relies on, the main risks, how it generalises, and what earlier runs taught us.
- `skills/`: the four Skills above.
- `presentation.mp4`: the English presentation video.
