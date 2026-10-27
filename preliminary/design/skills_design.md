# Preliminary Skills design

## Status and task understanding

Team: Winning team.

This is an initial proposed design, not a tested or scored solution. The agent manages a new employee through a 48-month career. Monthly choices, quarterly resource allocation, and six-month reviews require decisions whose consequences can extend beyond the current event.

The implementation uses JiuwenSwarm 0.2.4b3 in single-agent mode. One Skill, career-strategy, provides the decision process. Multiple people may develop the submission, but the evaluated execution uses one agent.

## Skill responsibilities

The career-strategy Skill is responsible for:
- establishing the current phase, visible statistics, warnings, and legal choices;
- comparing monthly options using immediate risk and longer-term development;
- coordinating quarterly Energy spending with the optional main action;
- checking outcomes and adjusting priorities after reviews;
- keeping a concise summary and stopping at the reported ending.

Keeping these responsibilities in one Skill avoids contradictory priorities and duplicated context in this first version. The same agent combines all evidence into a single decision; there are no teammate agents or parallel roles.

## Evidence and decision approach

The agent uses the public handbook and rules, current observations, available event choices, action results, review feedback, and official logs from its current run. The five official MCP tools provide game interaction. No internal package contents, database inspection, hidden evaluation information, or external services are used.

The decision sequence is: understand the situation, identify urgent visible risks, compare legal actions, choose a sustainable response, and inspect its consequences. Serious warnings take priority over speculative progress. In stable conditions the agent develops Skill, Network, and Output while preserving Health, Dignity, and financial resilience. These are qualitative priorities, not assertions about hidden scoring weights or exact thresholds.

Quarterly planning considers a combination of actions within the visible budget. The agent reassesses after each action rather than assuming that the initial plan remains valid. Six-month feedback guides changes in emphasis without being treated as proof of a hidden formula.

## Risks and intended mitigation

Incomplete information can hide accumulating problems. The agent therefore checks warnings and trends and keeps uncertain interpretations separate from observations.

An excessively cautious policy could survive but progress poorly. Reviews and observed development trends should help the agent recognise this and invest more in sustainable progress when immediate risks are controlled.

An excessively aggressive policy could sacrifice wellbeing for short-term output. The Skill explicitly considers recovery and the consequences of repeated tradeoffs.

Tool loops and excessive context can waste tokens. The agent uses returned results first, consults logs when needed, and maintains a concise summary.

Development events may differ from evaluation events. The design contains no event-specific answer mappings, memorised sequences, or unpublished numerical limits. Scripts and reference files are omitted because the initial strategy needs only instructions and official tools.

## Planned validation

After obtaining organiser-issued access, install the pinned dependencies with make sync and test through the official runner. For local play, prepare solution/ using the official final template and transfer this manifest and Skill into it.

Inspect complete run outcomes, early exits, warnings, reviews, invalid action attempts, and token use across repeated runs. Revise instructions using evidence from those runs, documenting actual changes and limitations. No runs, performance gains, or scores are claimed at this stage.

Before preliminary submission, confirm the registered team name and review all English documents. For the final submission, add the required README, decision report, and original English presentation video, then run the official validator.
