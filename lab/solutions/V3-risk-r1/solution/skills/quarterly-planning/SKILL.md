---
name: quarterly-planning
description: "Decides the quarter-end phase: how to spend the 3 Energy points and which main action to take. Use it every time observe shows the quarterly energy allocation or the main-action list. It aims every quarter at the next promotion: it finds the hardest gap among Skill, Network and Output, stops spending on areas that are already satisfied, sprints before a review and recovers after it."
---

# Quarterly Planning

## Attitude
- **Growth goal: the next promotion, after feasible responses to unresolved safety threats.** Level is part of the ending score and raises salary for every remaining month.
- **If one area is already satisfied, focus on the others.** Effort on something that no longer moves is wasted.
- **Push first, rest after.** Sprint before a review, recover after it. Take a risk only when work can cover it.
- **Think before doing.** Plan the whole quarter before the first action. A setback is information: recover, change the approach, push again.

## How the quarter works
- 3 Energy points; unused points are lost. One Energy action per turn; the same action may be taken again while it is listed. The reserve option ends the Energy phase.
- Then one main action. Check its listed cost; when it costs no Energy, always take one.
- **Every action shows its cost and effects on the screen. Use those numbers every time. Never rely on remembered values.**
- Reviews come every six months: months 6, 12, 18, 24, 30, 36, 42 and 48. Promotion looks at Skill, Network and Output together; the bar rises with each level.

## Step 1. Which quarter is it?
- **SPRINT:** the next review is within the next three months.
- **RESET:** a review has just happened.
- **FINAL:** no review is left. Go to step 5.

## Step 2. Satisfied, dropped, hardest gap
Compare Skill, Network and Output with the values in your last quarter note.
- **Satisfied** (our own rule, not a game rule): it has not risen since the last quarter note, although you bought actions for it. Health or Dignity at 10 is also satisfied. Re-check every quarter and after every promotion.
- **Dropped:** it is lower than in the last quarter note. Dropped comes first.
- **Hardest gap:** among the areas that are not satisfied, the one that grew the least since the last quarter note.
- In the first quarter there is no earlier note: treat nothing as satisfied and choose the lowest-looking area of the three.

## Step 3. Plan the 3 Energy points
Read every action's cost, which areas it raises, which it lowers, and any risk. Value = gain for areas that still need effort, per Energy point. Gains on a satisfied area count as zero.

The "lower half" and "upper half" of the 0 to 10 range below are our own caution margins, not game rules.

In order:
1. **Safety.** Health or Dignity in the lower half of 0 to 10, or lower than in the last note: one point on its recovery first. Also check the carried unresolved accumulated-risk concern. Before optional growth, use an affordable action with a listed protective effect relevant to that concern when available. If safety needs compete, respond to the more immediate failure threat and retain the unmet concern. This safety check also applies in a FINAL quarter and is not blocked by the satisfied-area growth rule.
2. **The gap.** Most points on the best-value action for the dropped area or the hardest gap.
3. **The rest.** The next need. In a RESET quarter, bring Health and Dignity back to the upper half, not to 10.

Rules:
- Never buy an action whose only effect is on a satisfied area or on a stat at 10.
- An action that lowers Health or Dignity: only in a SPRINT quarter, and only when both are in the upper half.
- Avoid actions that raise hidden risk. If you take one, take a risk-lowering action in the next quarter. A warning from monthly events also requires the safety check; protection must not depend on having deliberately selected a risk-raising quarterly action. After protection, distinguish response taken from confirmed mitigation or resolution using specific feedback.
- Reserve only if no affordable action helps an area that needs effort.
- Take the actions one by one and keep count of the Energy left.

## Step 4. Main action
First reassess the carried safety concerns after the Energy actions. If an accumulated-risk concern remains unresolved, choose a suitable main action with a listed protective effect before optional growth when feasible, unless a more immediate failure threat requires another response. Do not assume an Energy action cured the concern merely because the action succeeded. Otherwise pick the action whose listed effects best raise the dropped area or the hardest gap; if two are close, pick the one that raises more areas that need effort. "No action" only if nothing helps.

## Step 5. FINAL quarter
Promotions are over. Output no longer counts. Spend on what the ending counts, in this order:
1. Health and Dignity up to 10.
2. Lower hidden risk when the feed or carried notes indicate an unresolved concern, including exposure from monthly events; apply the safety check before optional growth.
3. Skill, then Network.

## Step 6. After every review
- **Promoted:** the bar is higher, so earlier "satisfied" areas need effort again. Next quarter is RESET.
- **Not promoted:** next quarter is RESET. Use a different action or main action for the area that stayed behind than you used before, then sprint again.
- Write `review: M<month> grade <X> promoted yes/no` in the next note.

## Step 7. The quarter note (every quarter-end action)
`Q<n> M<month> L<level> <SPRINT|RESET|FINAL> | S<skill> N<network> O<output> H<health> D<dignity> | gap: <area> | satisfied: <areas> | did: <action> | left: <plan>`
If an accumulated-risk concern is unresolved, carry `risk: <concern>; response: <pending/taken>; state: <open/mitigated>` in the note, shortening repeated statistics to keep it compact. Omit the tag only after specific feedback supports resolution. Never repeat last quarter's plan unless the current state and carried warnings show it still works.

## Example
This situation is invented to show the method.
Last note: `S30 N12 O9`. Now: `S33 N12 O8`, Health 8, Dignity 10, review in two months: SPRINT. Network did not rise although you bought Network actions: satisfied. Output dropped: first. Plan: most Energy on the best Output action shown on the screen, the last point on the best Skill action that fits. Main action: the biggest listed Output gain. Nothing on Dignity (10) or Network (satisfied).
`Q11 M33 L3 SPRINT | S33 N12 O8 H8 D10 | gap: Output | satisfied: Network, Dignity | did: report action | left: Skill action, main: Output action`
