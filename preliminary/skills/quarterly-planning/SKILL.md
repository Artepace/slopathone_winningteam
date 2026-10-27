---
name: quarterly-planning
description: Decides how to spend the 3 Energy points and which quarterly main action to select, using the published action effects. Use whenever observe shows the end-of-quarter action phase.
---

# Quarterly Planning

## Purpose
At the end of each quarter the agent gets 3 Energy points that do not carry over, and may pick one main action or none. These have the largest long-term effect on the career trajectory. This Skill builds the plan from the current state and the stage of the run. Use only the published effects below. Anything beyond them is learned from in-run feedback.

## Published action effects (from the public handbook)
Energy actions:
- High-intensity work (cost 2): Output up, Health down, Dignity down.
- Skill learning (cost 2): Skill up, Health down.
- Network maintenance (cost 1): Network up, Dignity up.
- Defuse legacy risk (cost 2): no published direct statistical effect. It targets accumulated hidden risk.
- Mental recovery (cost 1): Dignity up.
- Health recovery (cost 1): Health up.
- Prepare report materials (cost 1): Output up, Dignity up.

Main actions (one per quarter, or none):
- Apply for a key project: Output, Skill, Network up.
- Report results to your manager: Output, Network, Dignity up.
- Fight for resources: Output, Network up.
- Apply for rotation: Skill, Network up.
- Showcase results: Output, Dignity up.
- Build a mentorship: Skill, Network up.
- Repair a key relationship: Network, Dignity up.
- Lay low and reduce risk: Health up.

## Procedure
1. **Diagnose.** Read the current state and compare it with the previous quarter. Name the weakest dimension, any falling trend and any warning. Note whether a six-month review or promotion window is near.
2. **Cover urgent needs first.**
   - Health low or falling: spend on Health recovery, and consider the "Lay low and reduce risk" main action.
   - Dignity low or falling: spend on Mental recovery, Network maintenance or Prepare report materials, and consider "Repair a key relationship" or "Showcase results".
   - Warnings about hidden or accumulated risk: spend 2 Energy on Defuse legacy risk.
   - Network at or near zero: prioritise Network maintenance and a Network-raising main action.
3. **Spend the rest on growth.** Use the remaining Energy to build long-term value. Prefer actions that raise a dimension without hurting Health or Dignity, such as Network maintenance and Prepare report materials. Use the 2-cost actions that cost Health or Dignity (High-intensity work, Skill learning) only when Health and Dignity are comfortably healthy, and balance them with a recovery action in the same or next quarter.
4. **Choose the main action.** Match it to the need:
   - Balanced and stable: the action that raises the most dimensions you need, for example "Apply for a key project" for broad growth, or "Report results to your manager" when Dignity and Network also matter.
   - Weak Skill: "Apply for rotation" or "Build a mentorship".
   - Weak Output before a review or promotion window: "Showcase results" or "Report results to your manager".
   - Health or risk pressure: "Lay low and reduce risk".
   - No suitable action: select no main action. Do not force one.
5. **Use all 3 Energy points each quarter**, unless an action would worsen a vulnerable dimension. Unused Energy is lost.
6. **Write a note** with the diagnosis and the plan in one or two sentences, then call `take_action` for each step the interface requires.

## Stage of the run
- Early quarters: favour Skill and Network, because they compound and are slow to build. Keep Health and Dignity healthy.
- Middle quarters: convert capability into Output and promotion readiness, with recovery actions whenever Health or Dignity slips.
- Final quarters: favour actions whose effect lands before month 48. Avoid long investments that cannot pay off. Do not run Health or Dignity down in the last stretch, because they count in the ending.

## Avoid
- Repeating the same Health-costing or Dignity-costing action every quarter.
- Ignoring Network until it reaches zero. A long period at zero is a public failure direction.
- Chasing Output alone. The ending score covers level, wealth, health and dignity, skill, risk control and network together.

## Adapting
Action costs, effects or availability may differ from this list in other settings. If the interface shows different options or costs, follow what the interface shows and apply the same diagnosis-then-plan logic.
