# Winning team: V5 adaptive r2

Revision r2 of the five-Skill design for the 48-month Career Survival task, intended for JiuwenSwarm **0.2.4b3**, single-agent mode. It is a separate candidate, not a replacement of an existing tested version.

| Skill | Responsibility |
| --- | --- |
| session-ledger | One session, observation/action protocol, compact recoverable memory, errors and ending. |
| threat-control | Persistent evidence-based concerns and proportionate protective obligations. |
| event-judgment | Integrity, uncertain downside, feasible alternatives and monthly choices. |
| resource-planning | A joint quarterly Energy/main-action plan under current constraints. |
| feedback-learning | Checkpoints, provisional focus, plateau diagnosis and course correction. |

All Skills are newly authored and self-contained. There are no runtime scripts, external references inside Skill folders, agents requiring team mode, or web calls during play. The five Skills describe procedures performed by one agent.

The design addresses failures documented in earlier local runs: warnings erased by praise or silence, protection mistaken for resolution, flat statistics mistaken for sufficiency, focus locked until promotion, weak performance neglected during protection, repeated unsupported predictions, conflicting priorities, and excessive re-analysis. See [skills_design.md](design/skills_design.md), [decision_report.md](design/decision_report.md), and [sources.md](design/sources.md).

The r1 baseline completed one of three local careers. Revision r2 tests how the agent handles a weak review when spending more on delivery brings little visible return. It retains the five roles, uses a short same-level comparison and reevaluates after a change in conditions. Evaluate this revision using its own frozen runs.

This package deliberately has no `presentation.mp4`. It is prepared for local inspection and possible later authorized local play, not a complete final competition submission. A final submission requires the team's English presentation video. Merely opening or validating this directory does not authorize a game, installation, upload, or publication.
