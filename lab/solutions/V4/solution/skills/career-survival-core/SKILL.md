---
name: career-survival-core
description: "Runs the 48-month Career Survival game: start or resume one session, the observe-decide-act loop, routing each turn to the right Skill, rejected actions, the note format and the ending. Use at the start of every run and again after any context reset or continue message."
---

# Career Survival Core

**Role:** you run the game safely from month 1 to month 48.
**Task:** keep one session alive, send each turn to the right Skill, and write one note per action.

## CRITICAL
1. If you already have a session_id, NEVER call `new_game`.
2. After every `take_action`, call `observe` before the next decision. Never guess the state.
3. For the game use ONLY `show_employee_handbook`, `new_game`, `observe`, `take_action`, `check_latest_logs`. Open Skills with the platform's skill tool.
4. NEVER stop or ask the user before the game ends.
5. When a result says the game is over or shows `ending_score`, print the full `ending_score` payload, then `DONE`. Make no further calls.

## Start (no session_id yet)
1. Load `event-choice-evaluation` and `quarterly-planning` with the skill tool.
2. Call `show_employee_handbook` once.
3. Call `new_game` once.
4. Print one line: `SESSION_ID=` followed directly by the session id, with no brackets or spaces.
5. Call `observe`.

## Resume (you have a session_id, or a reset or continue message)
1. Do not call `new_game`.
2. Reload this Skill with the skill tool.
3. Call `observe`.
4. Call `check_latest_logs(session_id, count=10)` and read your last notes.

## Every turn
1. `observe`. Read the news text (the `events` field: salary, comments, review results), the situation, every choice and the stats.
2. Set the risk flag from the news text:
   - `mild`: a comment mentions some risk and says it is NOT serious yet.
   - `serious`: a comment says risks have built up or must be dealt with now.
   - If unsure between the two, use `serious`.
   - `none`: no risk comment, or a comment that you are doing fine.
3. Route the turn:
   - Story event or follow-up: use `event-choice-evaluation`.
   - Quarterly Energy allocation or main-action list: use `quarterly-planning`.
4. Call `take_action(session_id, choice=[number exactly as listed], notes=[note])`.
5. Go back to step 1. That `observe` is the one CRITICAL rule 2 requires; do not call it twice.

## If something goes wrong
- Action rejected: read the error, call `observe`, choose a number that is listed now. Never repeat the same rejected call.
- Lost track of the month or plan: call `check_latest_logs(session_id, count=10)`.

## Priorities
1. **Stay in the game.** Health or Dignity at 3 or below (our own margin, not a game rule): protect it first. A `serious` risk flag: clean it up at the next quarter-end.
2. **Get promoted.** Reviews happen at the start of months 6, 12, 18, 24, 30, 36, 42 and 48. Promotion looks at Skill, Network and Output together, and it rewards results that keep growing: a half-year with little growth gives a weak review. `quarterly-planning` handles this. Quarter-ends come at the end of months 3, 6, 9, ... 48.
3. **Finish strong.** The ending counts level, wealth, health and dignity, skill, risk control and network.

## The note (one line, under 300 characters)
Values in [ ] are placeholders: write the real value, without brackets.
`M[month] L[level] H[h] D[d] S[s] N[n] O[o] W[w] | risk:[none|mild|serious] | focus:[Skill|none] | [choice and short reason] | next:[plan]`
H Health, D Dignity, S Skill, N Network, O Output, W Wealth. After a review, add `review: grade [X], promoted yes/no`.

Keep the `focus` value from the last quarter note until `quarterly-planning` changes it.

Example: `M14 L2 H8 D10 S24 N9 O7 W5 | risk:mild | focus:none | opt1 fixes the root cause openly, Skill and Network up | next: quarter-end at M15`
