# Skills Design (Preliminary)

## 1. Our understanding of the task
The agent is a newly hired engineer in a 48-month workplace simulation. Each month it faces up to three story events and picks one choice per event. At the end of each quarter it receives 3 Energy points (no carry-over) and may pick one quarterly main action. Every six months there is a performance review with a bonus and a promotion window. The agent acts only through five official MCP tools: `new_game`, `observe`, `take_action`, `check_latest_logs` and `show_employee_handbook`.

The run can end early. The public failure directions are health at zero, critically low dignity, accumulated hidden risk, repeated low performance, network at zero for long, wealth negative for long, and skill falling far behind. The exact thresholds are unpublished. A completed run ends with a quantitative score from 0 to 100, based on career level, total wealth, health and dignity, skill, risk control and network. Official scoring averages three runs and adds document design quality and token efficiency. Surviving all 48 months therefore matters twice: it protects the live-play score and it removes the cap on the token-efficiency term.

Our central view is that this is a balance-and-timing problem under incomplete information. Maximising one statistic (for example Output through overwork) is likely to end the run early or lower the ending score. We therefore design for steady, balanced growth with early correction of adverse trends.

## 2. Planned Skills and responsibilities
| Skill | Responsibility |
|---|---|
| `career-survival-core` | Owns the whole run: setup (handbook, new game), the observe/decide/act loop, the priority order (avoid early failure, balance, long-term growth, wealth), how to read risk from trends and warnings, horizon awareness, and token economy. |
| `event-choice-evaluation` | Owns monthly story events: reads the state, estimates each choice's effect on the visible statistics, classifies it as safe, trade-off or gamble, and applies the priority rules. It works from effects, never from event names. |
| `quarterly-planning` | Owns the quarter-end phase: diagnoses the state, covers urgent needs first, spends the 3 Energy points, and chooses or skips the main action, using only the published action effects and adjusting for the stage of the run. |

The Skills are linked as one decision chain. The core Skill sets the priorities and calls the other two at the right phase. Both of those Skills use the same priority order, so their outputs stay consistent.

## 3. Information the agent uses
- The public employee handbook, read once at the start.
- The statistics returned by `observe`: Health, Dignity, Skill, Network, Level, Output, Wealth, Energy and CurrentLevelDuration.
- Event text, the listed choices and any warnings.
- Changes between consecutive observations, used to detect trends.
- `check_latest_logs`, used only when a warning or unexpected change needs explaining.
- The agent's own short notes in `take_action`, used to record the reasoning and expected effect.

The Skills do not contain any internal formulas, event lists, event-specific answers or unpublished thresholds. Where we mention a safety margin, we describe it as a cautious working habit, not as a known rule.

## 4. How the decisions are combined
For every decision, the agent (1) reads the state and finds the weakest or fastest-falling dimension, (2) lists the effects of each option, (3) protects against early failure first, (4) then prefers long-term growth in Skill, Network and sustained Output, and (5) records a short reason. Monthly events and quarterly actions share the same logic, so a recovery chosen in the quarterly phase is not undone by a gamble in a story event.

## 5. Main risks in the approach
- **Incomplete information.** Thresholds and hidden-risk conditions are unknown. Our mitigation is to act on trends and warnings, and to be conservative when an effect is unclear.
- **Over-caution.** Too much protection could lower Output, Skill and promotion progress. We mitigate this by switching to growth actions whenever the state is stable.
- **Vague event effects.** Choices may not state their effects. The agent must infer from wording, and may misjudge. In-run comparison of expected and actual change is the correction.
- **Dataset overfitting.** The official dataset differs from the development one. We avoid event memorisation and keep the Skills generic.
- **Token cost.** Long reasoning every turn raises tokens per month. The core Skill asks for short notes, rare log checks and a single handbook read.
- **Model limits.** The designated model may not follow long instructions perfectly. We keep each Skill focused and structured as ordered steps.

## 6. Plan for improvement
After the API key arrives, we will run local games, read transcripts and score reports, and refine each Skill against what actually fails. We expect to tune the early/middle/late emphasis in quarterly planning and the risk classification in event evaluation. We will decide whether any reference files are warranted. We currently plan no scripts, because the design needs no code execution.
