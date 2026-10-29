---
name: event-choice-evaluation
description: "How to handle a monthly story event. Use it every time observe shows a workplace situation with numbered choices, including follow-ups of an earlier situation. Event choices usually show only text, so this Skill turns the wording of each choice into likely stat effects and risk, then applies the decision-mind procedure."
---

# Event Choice Evaluation

Story events are most of the turns in a run. Their choices usually describe actions in words and do not show numbers.
Your job is to turn the words into likely effects, then decide with `decision-mind`.
Decide from the situation in front of you. Never decide from an event's title or from memory of other runs.

## 1. Read everything first
1. Read the monthly feed above the event. It may contain a warning, a review result or a comment about your standing.
2. Read the whole situation text.
3. Read EVERY choice to the end before judging any of them.
4. Check whether this is a follow-up of a situation you already answered. If it is, remember what you chose and why, and check whether that earlier choice now has consequences.

## 2. Translate wording into effects
Use these general language cues to fill step A of `decision-mind`. They describe common workplace meanings, not answers to specific events. If a lesson from earlier in this run says otherwise, the lesson wins.

| If a choice involves... | Likely effect |
|---|---|
| extra hours, weekends, pushing through, taking on everything | Output up, Health down, often Dignity down |
| learning, a course, a mentor, studying a new area | Skill up, short-term tiredness (Health slightly down) |
| volunteering for visible work with a reasonable scope, a stretch project, owning a delivery | Output up, Skill up, often Network up, small Health cost |
| delivering on time, finishing what you promised, shipping a result | Output up, sometimes Dignity up |
| helping a colleague, building trust, keeping in touch | Network up, sometimes Dignity up |
| presenting your work, writing it up, getting credit openly | Output up, Dignity up |
| standing up for yourself calmly, stating facts, setting a fair limit | Dignity up, small Network risk |
| agreeing to a cost just to keep the peace, accepting unfair blame | Dignity down, risk moved onto you |
| spending money, paying for something, giving up a payment | Wealth down |
| a payment, a bonus, extra paid work | Wealth up, check what it costs elsewhere |
| secrecy, doing it quietly, skipping checks, signing without reading, bending a rule | hidden risk (rate `risk: high` in step B) |
| confronting someone publicly, blaming others, escalating in anger | Network down, conflict risk |
| reading the details first, asking, clarifying, negotiating openly | low risk, usually protects every stat |
| resting, saying no to unreasonable extra load | Health up, small Output cost |

If a cue does not fit, mark the effect `?` and treat the option more conservatively.

## 3. Decide with decision-mind
1. Run the **pressure check** (`decision-mind` section 2).
2. Decide **fast or slow** (section 3). Any option with a hidden-risk cue, or any warning in the feed, means slow.
3. In slow mode, write the rows with the futures (steps A and B), then apply the ruin filter, dominance, long-term value and tie-breaks (steps C to F).
4. **Verify** (step G): the number matches the option you analysed, and it is still listed.
5. Call `take_action` with the ledger note (step H).

## 4. Patterns to remember
- An option that gathers information first (read, ask, clarify) is often the best first move when the situation is unclear. It keeps future options open.
- Honest and bounded usually beats both silent compliance and open conflict.
- A quick gain that the text says "may" cause trouble later is a bad case to simulate in step B, not something to ignore.
- Events with only two choices still deserve the full check when a trigger applies.
- Many small Dignity or Health losses add up. If the same kind of cost keeps appearing, count that stat as falling in the pressure check, even if each loss is small.
- **Do not hide from growth.** Promotion needs Output as well as Skill and Network. When Health and Dignity both have a safe margin, they are a buffer to spend: prefer the option that grows Output, Skill or Network even if it costs a little Health or Dignity. Refusing reasonable work every time leads to a safe but low-level career.

## 5. Short example
This situation is invented to show the method.
State: all stats with a safe margin. A manager asks you to take over a struggling project this weekend, and offers public credit.
- opt1 accept and work the weekend: `H- D0 S0 N+ O+ W0 | likely: tired, credited | bad: tiredness lingers | m48: small help | risk: low`
- opt2 accept from Monday and agree a realistic scope: `H0 D+ S0 N+ O+ W0 | likely: credited, rested | bad: slower start | m48: helps | risk: none`
- opt3 decline: `H0 D0 S0 N- O0 W0 | likely: missed chance | bad: seen as unhelpful | m48: small hurt | risk: low`

Dominance: opt2 is at least as good as opt1 and opt3 on every stat and on risk. Choose opt2.
