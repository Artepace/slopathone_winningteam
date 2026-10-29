# Decision Report

## 1. Overall approach
The task is a balance-and-timing problem under incomplete information. The ending score covers career level, total wealth, health and dignity, skill, risk control and network, and a run can end early through several failure directions whose exact limits are unpublished. Our approach is therefore:

1. Avoid early failure by reacting to trends and explicit warnings, not to guessed numbers. A small stable value or a single weak review is not treated as a crisis.
2. Keep all principal dimensions in balance, because maximising one while another decays is penalised.
3. Build Skill, Network and sustained Output across the 48 months, because promotion rewards sustained results.
4. Accumulate Wealth steadily through level and review bonuses.
5. Aim every quarter-end at the next promotion: find the hardest gap among Skill, Network and Output, stop spending on areas that no longer move, sprint before a review and recover after it.

Surviving all 48 months also matters for the token-efficiency term, because a run that ends early is capped on that term.

## 2. Information the approach relies on
- The public employee handbook, read once at the start.
- The published rules: monthly salary by level, the quarterly Energy actions and main actions with their qualitative effects, the six-month review grades and bonuses, and the promotion windows.
- Every statistic and warning returned by `observe`, and the change between consecutive observations.
- The event text and the choices shown.
- Review grades and promotion results.
- `check_latest_logs` and the agent's own earlier notes, to recover after a context reset.

## 3. In-run feedback loop
After each action the agent compares the next observation with what it expected. A worse result makes similar choices more cautious. A better result lets it use that kind of choice slightly more. After each six-month review, a C or D shifts the next quarters toward Output and Skill, and an S or A keeps the balance. These adjustments live only in the agent's notes, never as claims about hidden formulas. At each quarter-end the agent compares Skill, Network and Output with its earlier notes: an area that has not risen despite effort is treated as satisfied for now and re-checked every quarter, and an area that an event lowered becomes first priority. After a review without promotion it recovers, changes the approach for the area that stayed behind, and sprints again.

## 4. Principal risks and mitigations
- **Unknown limits.** The failure limits and hidden-risk conditions are unpublished. Mitigation: act on trends and explicit warnings, and use the quarterly "Defuse legacy risk" action when feedback suggests risk is building.
- **Over-caution.** Constant protection could lower Output, Skill and promotion progress. Mitigation: the Skills switch to growth actions whenever no dimension is under pressure.
- **Aggressive trade-offs.** Overwork buys short-term results at the cost of Health and Dignity. Mitigation: these actions are allowed only when the state is healthy, and they are paired with recovery.
- **Unclear effects.** Event choices do not state their consequences. Mitigation: translate wording into uncertain effects, check the strongest alternative, judge future consequences rather than persuasive labels, and keep unknown effects unknown.
- **Context loss in a long run.** Mitigation: compact notes each turn, a rule never to call `new_game` when a session exists, and a recovery path through `observe` and `check_latest_logs`.
- **Token cost.** Mitigation: short notes, no handbook re-reads, rare log checks, and a short manifest instruction.
- **Model limits.** The designated model may not follow long text perfectly. Mitigation: ordered steps and one clear priority list per Skill.

## 5. What our earlier runs taught us
We ran two versions locally on the development dataset, one run each. Version 1 (three Skills) completed all 48 months and scored 68.6. A heavier version with a long psychology-based decision Skill scored 59.0, so this version builds on version 1. It keeps version 1's run protocol, replaces the event judgment with a short evidence-based version, and replaces the quarterly plan with a promotion-focused one. The logs showed:
- Both runs kept buying actions for Network and Output during long periods when those statistics no longer rose, while another area was still behind. This motivated the satisfied-area rule.
- Health and Dignity were often at their maximum while Energy was still spent on them, and the same quarterly plan was repeated for years.
- Events sometimes lowered a statistic shortly before a review, which cost a promotion. This motivated the dropped-area priority.
- The quarter-end menu shows each action's cost and effects, so the agent can decide from the numbers on screen.
- Event sequences differ between runs, so we compare versions over several runs, not one.
- The heavier version flagged pressure on most turns of its first two years (a weak review and small but stable values counted as pressure), which kept it defensive. This version only treats a trend or an explicit warning as pressure.

## 6. Generalisation beyond the development dataset
The official dataset and parameters differ from the development set, so nothing in the Skills depends on event titles, event order, memorised sequences or specific numbers. Each decision is re-derived from the current state and the effects the text or interface shows. The only numeric margins (for example the lower third of the 0 to 10 range in the core's inherited caution rules) are stated as the team's own caution habits, and action effects are read from the screen each time. If action costs, effects or the option list differ, the Skills tell the agent to follow what the interface shows and to apply the same diagnose-then-plan logic.

## 7. Validation status
The design follows the public documentation. Local development runs are used to find where the agent fails and to refine the Skills. This report claims only what has been observed in those runs, and no result is assumed in advance.
