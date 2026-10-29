# Winning team - Career Survival Agent (v3)

This submission is a Career Survival Agent for JiuwenSwarm 0.2.4b3 in single-agent mode (`"mode": "agent"`). It plays the full 48-month simulation through the five official MCP tools only: `new_game`, `observe`, `take_action`, `check_latest_logs` and `show_employee_handbook`.

The design builds on our first version, which completed all 48 months without errors in local testing. It keeps that version's run protocol and adds two focused improvements: sharper judgment for monthly events, and a quarter-end plan aimed at the next promotion. The agent decides only from the public handbook and from what the simulation returns during the current run. It contains no event-specific answers, no memorised sequences and no unpublished thresholds.

## Skills
| Skill | Purpose |
|---|---|
| `career-survival-core` | Run protocol: start or resume one session, route each phase to the right Skill, execute every game action, recover from errors or context loss, and report the ending. Also holds the overall priorities and the compact note rules. |
| `decision-mind` | Judgment for monthly events: when a statistic is really under pressure, when a short written comparison is needed, how to compare future consequences instead of persuasive wording, and how to learn cautiously from feedback. |
| `event-choice-evaluation` | Monthly story events and follow-ups: read every choice, translate wording into uncertain effects, check the strongest alternative with `decision-mind`, and return the exact choice number with a short note. |
| `quarterly-planning` | Quarter-end phase, aimed at the next promotion: find the hardest gap among Skill, Network and Output, stop spending on areas that are already satisfied, sprint before a review and recover after it, using the action effects shown on screen. |

There are no scripts and no reference files: the design needs only instructions and the official tools.

## Files
- `manifest.json`: team, submission name, mode, and the instruction shown to the agent on every call (Skill roles and routing, protocol rules).
- `design/skills_design.md`: how the four Skills divide responsibilities and combine into one decision.
- `design/decision_report.md`: the decision approach, the information it relies on, what earlier runs taught us, the main risks and how it generalises.
- `skills/`: the four Skills above.
- `presentation.mp4`: the English presentation video.
