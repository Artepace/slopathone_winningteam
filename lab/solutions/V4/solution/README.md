# Winning team - Career Survival Agent (v4)

A Career Survival Agent for JiuwenSwarm 0.2.4b3 in single-agent mode (`"mode": "agent"`). It plays the full 48-month simulation through the five official MCP tools only: `new_game`, `observe`, `take_action`, `check_latest_logs` and `show_employee_handbook`.

This version keeps the simple design of our best-scoring local version and adds a small number of fixes found in our run logs: a fixed rule for cleaning up risk after serious warnings, no Energy spent on a statistic that is already full, and no options that hide problems or skip checks. The Skills are short and use explicit rules, because the designated model follows clear instructions better than long reasoning procedures.

The agent decides only from the public handbook and from what the simulation returns during the current run. It contains no event-specific answers, no memorised sequences and no unpublished thresholds.

## Skills
| Skill | Purpose |
|---|---|
| `career-survival-core` | Start or resume one session, the observe-decide-act loop, routing each turn, the risk flag, rejected actions, the one-line note and the ending. |
| `event-choice-evaluation` | Monthly story events: turn each choice's wording into likely effects, remove options that hide problems or skip checks, and pick the honest option with the best long-term value. |
| `quarterly-planning` | Quarter-end phase: clean up risk after serious warnings, spend all 3 Energy points without waste, and pick the main action for the next promotion. |

There are no scripts and no reference files.

## Files
- `manifest.json`: team, submission name, mode, and the instruction shown to the agent on every call (Skill roles and the critical rules).
- `design/skills_design.md`: how the three Skills divide responsibilities and combine into one decision.
- `design/decision_report.md`: the decision approach, the evidence from our runs, the main risks and how it generalises.
- `skills/`: the three Skills above.
- `presentation.mp4`: the English presentation video.
