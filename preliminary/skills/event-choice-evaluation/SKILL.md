---
name: event-choice-evaluation
description: Method for choosing among the options of a monthly story event. Use every time observe returns a story event with choices, regardless of how the event is worded or ordered.
---

# Event Choice Evaluation

## Purpose
Each month presents up to three story events. This Skill turns the event text and the listed choices into a decision using the current statistics and the public meaning of each statistic. It never depends on the event title. It works from the effects and risks the text describes.

## Procedure
1. **Read the state first.** Note Health, Dignity, Wealth, Skill, Network, Output and Level. Identify the weakest or fastest-falling statistic, and any warning in the text.
2. **Read every choice fully.** For each choice, list the statistics it plausibly raises, lowers or leaves alone. Use any explicit effect shown in the choice. Where none is shown, infer direction from the wording, and note which choices are riskier or less certain.
3. **Classify each choice by risk.**
   - *Safe*: improves or protects a core statistic and is not described as deferring a problem.
   - *Trade-off*: gains in one dimension at a cost in another.
   - *Gamble*: uncertain, secret, shortcut-based, confrontational or dependent on luck, with possible hidden consequences.
4. **Apply the priority rule.**
   - If any core statistic is low or falling, prefer the choice that protects or restores it, unless it triggers a worse downside elsewhere.
   - If the state is stable, prefer the choice with the best long-term value: Skill, Network, sustained Output and Dignity over short-term gain.
   - Choose a gamble only when the state is clearly robust and the upside is meaningful. Never gamble while Health, Dignity or Wealth is under pressure.
5. **Check for compounding.** Ask whether repeating this kind of choice every month would be sustainable. Avoid choices whose cost repeats or accumulates, such as sustained overwork, repeated loss of standing, or ongoing spending.
6. **Write a short note** with the key reasoning, such as "protects Dignity, small Output cost". Then call `take_action`.

## Consistency principles
- Overwork, humiliation and unethical shortcuts yield short-term Output or Wealth at the expense of Health, Dignity or hidden risk. Treat them as costly unless the state is strong and no warnings exist.
- Honest communication, reliable delivery and relationship-building tend to support Network, Dignity and long-term standing.
- Wealth matters, but a persistent negative balance is a public failure direction. Avoid choices that put wealth in sustained deficit, and accept small short-term gains in wealth only when other dimensions are safe.
- Between two similar options, prefer the one that keeps more options open for later months.
- If the text does not make the effect of a choice clear, choose the option that is more conservative for Health and Dignity.

## Adapting to new wording
Event wording, order and parameters may differ from run to run. Do not memorise events or map event names to answers. Re-derive the decision each time from the current state and the stated or implied effects of the choices.

## Learning inside the run
After each action, compare the next observation with what you expected. If the change was worse than predicted, make later choices of that general type more cautious. If it was better, you may use that type slightly more. Record the lesson in the note, not in your assumptions about hidden formulas.
