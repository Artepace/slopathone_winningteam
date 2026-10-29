# Decision Report

## 1. The problem as we understand it
The agent plays one 48-month career. Its ending score covers career level, total wealth, health and dignity, skill, risk control and network. A run can end early through several failure directions whose exact limits are unpublished, and an early exit is scored from the state at exit. The official live-play score is the mean of three runs.

Three consequences shape the whole design:
1. **Ruin is permanent.** One early exit can sink the average, so reliability matters more than brilliance.
2. **Level compounds.** Salary rises steeply with level, and promotion windows come only every six months. An earlier promotion pays for every remaining month.
3. **Information is incomplete.** Formulas and thresholds are hidden, and event choices are written in words. The agent must infer effects and learn during the run.

## 2. Decision approach
Every decision is judged by one question: **which option leaves the career best placed at month 48?** The agent answers it in a fixed order:
1. **Pressure check:** which statistics are under pressure, and which have a safe margin.
2. **Fast or slow:** routine turns use a short three-question check. Warnings, pressure, review months, quarter ends, gambles, close calls and the final six months force the slow procedure.
3. **Slow procedure:** translate each option into stat effects; simulate its likely, bad-case and month-48 futures; rate the risk; remove ruinous options; remove dominated options; rank the rest by long-term value; break ties; verify the choice; record a prediction.
4. **Learning:** compare the prediction with the real change and record a lesson.

## 3. Foundations
Each idea below is compiled into a concrete rule in the Skills. The theory is explained here, not in the Skills, so the agent receives only executable steps.

- **Ergodicity and ruin avoidance (Peters; the Kelly criterion).** The game is a single path with an absorbing failure state. On one path, a small chance of ruin destroys long-run value, so the agent first removes options that could end the run, then maximises long-term growth among the rest. Rule: the ruin filter (step C).
- **System 1 and System 2.** Fast, intuitive choices are cheap but biased; slow, deliberate choices are better but costly. For a language model, slow thinking means written, structured comparison. Rule: seven triggers decide when the agent must write out the option rows.
- **Big Five personality (Costa and McCrae).** A stable character improves consistency on routine turns. The profile is very low neuroticism (calm but responsive to warnings), very high conscientiousness (follows procedure, never quits), agreeableness high but bounded (honest and cooperative, but low compliance and moderate modesty, because complying with every cost drains Dignity and false modesty hides Output), moderate extraversion, and openness high for ideas and low for fantasy. Rule: the character section of `decision-mind` and the persona in the manifest.
- **Premortem (Klein) and Stoic premeditation.** Imagining failure before acting exposes hidden costs. Rule: the bad-case line in step B and the question "can I recover by next quarter?"
- **Stoic dichotomy of control.** Act on choices and Energy, never on guesses about hidden formulas. This also keeps the agent within the competition rules. Rule: the control and equanimity rules.
- **Aristotle's golden mean and telos.** Balance without deficiency or excess, aimed at the end goal at month 48. Rule: no statistic in deficiency, none pushed up by draining another, and the month-48 test.
- **Margin of safety (Graham) and the planning fallacy.** Keep a buffer before it is needed, and assume recovery takes longer than planned. Rule: the safe-margin definition and recovery before reviews.
- **Repeated games and reciprocity (Axelrod, Cialdini).** Network is a 48-month relationship game in which goodwill compounds and burned bridges do not return. Rule: cooperate by default, return favours, stay firm but polite when exploited.
- **Signalling and hidden motives (Simler and Hanson).** Output is defined as visible results, and requests for secrecy or blame shift risk onto the agent. Rule: visibility actions in each prove quarter; secrecy and unfair blame rated as high risk.
- **Bayesian updating and value of information.** Predictions are tested against outcomes, and trying an option type early is worth more than late. Rule: lessons recorded after surprises, explore in the first year, exploit afterwards.
- **Consistency.** Because the score averages three runs, a random choice in a close call adds noise. Rule: when unsure, follow the default rules.

We deliberately excluded ideas that are weakly supported or harmful here: ego depletion (failed large replications), Myers-Briggs types (not scientifically valid), explicit utility formulas (confusing for a small model) and manipulation tactics (they add hidden risk).

## 4. Public information and in-run feedback relied on
- The public handbook and rules: statistic ranges, monthly salary by level, the published effects of the Energy actions and main actions, review grades and bonuses, promotion windows, failure directions and ending dimensions.
- Each `observe` result: the monthly feed, warnings, the situation text, the choices and the statistics line.
- The trend between consecutive observations.
- Review grades and promotion results, recorded with their month to locate the next review.
- The action descriptions shown in the interface, which take priority over our summary of the handbook.
- The agent's own ledger notes and lessons, recovered through `check_latest_logs` after a context reset.

## 5. What an earlier version taught us
Version 1 used three Skills with general guidance and no explicit character or simulation step. We ran it once locally against the development dataset. It completed all 48 months with no rejected actions, reached career level 5 and scored 68.6 out of 100. Its ending report and its logs showed:

- **Where the points were.** Health and dignity and risk control were at their maximum, and skill and network were high. Career level and total wealth had by far the most headroom. Level was reached late: promotions came at months 6, 12, 24 and 42, and the windows at months 18, 30, 36 and 48 passed without a promotion, including one with a grade A review.
- **Over-caution.** Health and dignity sat at their maximum from the first months, so the buffer was never used for growth.
- **A repeated plan.** The same quarterly plan (report materials, network maintenance, health recovery, and one growth main action) was used in almost every quarter. The health recovery was bought while health was already at its maximum, so one of three Energy points was wasted each quarter. Skill learning was never used.
- **Interface facts.** Event choices are text without numbers. The result of `take_action` only confirms success, so a new `observe` is needed each turn. Energy actions are taken one per turn. Feed comments from colleagues report rising or stable risk. The platform opens Skills through a skill tool.
- **Cost.** The run used about 54 million tokens, about 1.1 million per surviving month. Almost all of it was the growing conversation re-sent on every call; output tokens were under 0.3 percent. The run cost under one US dollar of credit, so repeated local testing is affordable.

Changes in this version:
- the cap rule and the over-protection rule: no recovery for a stat at its maximum, and spare Energy goes into growth;
- Skill learning as the default build-quarter action, a limit on repeating the same plan, and a restricted, risk-aware use of High-intensity work;
- the growth-balance rule and a follow-up rule for a good grade without a promotion;
- the `event-choice-evaluation` cue table, to translate text choices into effects;
- plan-first execution in `quarterly-planning`, with optional chaining of Energy actions to save calls;
- risk comments in the monthly feed treated as warnings;
- one compact ledger line per turn and slow thinking only when triggered, to limit context growth.

The protocol of version 1 (session handling, ending output) worked without errors and was kept unchanged in behaviour. These changes are general rules; none refers to a specific event.

## 6. Principal risks and mitigations
- **Hidden limits.** Exact failure limits are unpublished. Mitigation: act on trends and warnings, and keep a safe margin before reviews and in the final year.
- **Over-caution.** Survival-first can stall promotion. Mitigation: the buffer rule, growth balance and the "do not hide from growth" rule.
- **Over-aggression.** The buffer rule could spend too much. Mitigation: the ruin filter, restoring the margin before every prove quarter, and limits on High-intensity work.
- **Wrong effect inference.** The wording cues can mislead. Mitigation: unknown effects are marked `?` and treated conservatively, and in-run lessons override the cues.
- **Hidden risk.** Risk control is scored but invisible. Mitigation: secrecy, shortcuts and unfair blame are rated high risk, and risk hygiene schedules "Defuse legacy risk".
- **Context loss in a long run.** Mitigation: the persistent manifest instruction, the ledger line as memory, and a recovery path through `observe` and `check_latest_logs`.
- **Token cost.** Written slow thinking adds context. Mitigation: slow mode only on triggers, one ledger line per turn, one handbook read and rare log checks.
- **Model limits.** A small model may skim long text. Mitigation: each Skill puts its numbered procedure first and its explanation later.

## 7. Generalisation beyond the development dataset
The official events and parameters differ from the development set, so nothing in the Skills depends on event titles, order, text or specific numbers. Every decision is re-derived from the current state, the trend and the effects the wording implies. The wording cues describe ordinary workplace meanings that hold for any event. If action costs, effects or lists differ, the Skills tell the agent to follow what the interface shows and apply the same procedure. The agent's lessons are scoped to the current run, so it adapts to a new environment instead of carrying assumptions from ours.

## 8. Validation status
Version 1 was run locally once and informed the changes above. This version is evaluated with the same local process, and this report claims only what has been observed in those runs.
