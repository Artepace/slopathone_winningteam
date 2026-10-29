# Decision Report

## 1. Approach
The agent plays one 48-month career. The ending covers career level, total wealth, health and dignity, skill, risk control and network, and an early exit is scored from the state at exit. Our approach, in order:
1. **Stay in the game.** Protect Health and Dignity when they are low, and clean up hidden risk as soon as the game warns that it is serious.
2. **Get promoted.** Reviews every six months look at Skill, Network and Output together; a higher level also raises salary for every remaining month.
3. **Waste nothing.** Energy goes where it still changes something.
4. **Stay honest.** Options that hide problems or skip checks are never taken.

## 2. Information used
- The public handbook (read once) and the published rules: salary by level, quarterly actions, review months, grades, failure directions and ending dimensions.
- Each `observe` result: the monthly feed (including comments about risk), the situation, the choices and the statistics.
- The costs and effects listed for each quarter-end action.
- The agent's own one-line notes, recovered through `check_latest_logs` after a context reset.

## 3. What our runs taught us
We ran five local games on the development dataset with three earlier versions.
- **Simple beat complex.** Our first, simple version scored 68.6. A version with long psychology-based procedures scored 59.0: it treated most turns as pressure and grew slowly. A four-Skill version scored 65.2, 26.2 and 50.4 in three runs.
- **Most points were lost on level and wealth** in every completed run, through slow promotions.
- **One elimination ruins the average.** One run was ended at month 19 by a trust crisis after hidden risk built up. In that run a serious risk warning got no clean-up action; in another, the clean-up came a year late. Runs that acted soon after serious warnings ended with no hidden risk. Mild warnings often faded without action.
- **Waste.** The first version bought Health recovery while Health was already full and repeated the same quarter plan for years.
- **Event choices were similar in every version**, so the differences came from quarter-end decisions and from event luck.
- **What held promotions back.** At the higher levels Output and Network stopped rising early while Skill was still far behind, and promotion came only when Skill caught up. Review grades followed growth: half-years with little growth in Skill, Network and Output gave weak grades, and a weak grade blocked promotion even when the statistics looked complete. This motivated the promotion push and the focus flag.
- **Wording matters for this model.** In one run the agent quoted a soft rule ("pick the risk-lowering action after a warning"), reasoned that it should "consider" it, and then did not. Rules are therefore written with MUST and IF-THEN, and the critical ones are repeated in the manifest.

## 4. Risks and mitigations
- **Hidden risk is invisible.** Mitigation: a fixed clean-up rule tied to the feed's risk comments, plus never choosing options that hide problems or skip checks.
- **Clean-up costs growth.** Mitigation: serious warnings are always acted on; mild ones only when they repeat and no clean-up was done the quarter before.
- **Slow promotions.** Mitigation: Energy is never spent on full statistics, a paid-for statistic that did not rise is replaced, and the promotion push moves Energy, the main action and event preferences to Skill when Output and Network have stopped rising. It ends after each promotion and never overrides the survival rules. This is the area with the most remaining uncertainty.
- **Event luck between runs.** Mitigation: versions are compared over at least three runs each, and survival is judged before the average score.
- **Model limits and updates.** Mitigation: short Skills with explicit rules and no dependence on one model version's quirks.

## 5. Generalisation
Nothing depends on event titles, event order, event text or numbers from our runs. Each decision uses the current statistics, the feed and the effects shown on screen. The only numeric margin (Health or Dignity at 3 or below on the published 0 to 10 range) is labelled as our own. If action costs, effects or lists change, the Skills tell the agent to use what the interface shows.

## 6. Validation status
This version is evaluated with the same local process over several runs, and this report claims only what has been observed.
