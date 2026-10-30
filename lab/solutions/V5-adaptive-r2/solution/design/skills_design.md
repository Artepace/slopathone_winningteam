# Skill architecture

## Purpose and boundaries

V5 adaptive r2 is a revision of the five-Skill policy for the 48-month Career Survival task. Its objective is strong career outcomes while avoiding early failure across all published failure directions. Single-agent JiuwenSwarm 0.2.4b3 performs all decisions. The design uses public documentation and evidence returned by the official tools; it does not require hidden state or event recognition.

The five Skills divide ownership rather than create five independent opinions. There is one execution loop, one ledger, one protection policy, and one feasible plan. No Skill starts an additional session or agent.

## Responsibilities and interfaces

| Skill | Inputs | Output to the same agent | Boundary |
| --- | --- | --- | --- |
| session-ledger | Session ID, observation, recent notes, tool results | Recovered ledger, phase routing, one valid action call, actual terminal report | Does not invent strategic effects or hidden state. |
| threat-control | Specific warnings, trends, response history, current menu | Persistent concerns and protection requirements, with conflict handling | Does not clear a warning on praise or prescribe exact hidden risk reductions. |
| event-judgment | Visible story/options, concerns, provisional focus | One supported event choice and concise expectation | Does not allocate quarterly Energy or use event-answer mappings. |
| resource-planning | Menu, budget, concerns, review feedback, baseline/focus | A joint Energy/main-action plan, revised only on material evidence | Does not define its own competing risk policy or promotion formula. |
| feedback-learning | Before/after observations, quarter baseline, review feedback | Provisional diagnosis, allocation change, expiry/check condition | Does not turn a plateau into a cap or launch experiments. |

The decision path is observation -> concern update -> checkpoint if needed -> phase-specific selection -> action -> observation. A checkpoint is a short procedure, not another tool call or a repeated debate.

## One ordering for competing needs

First respect current feasibility and imminent evidenced survival threats. Next meet protective obligations from `threat-control`, adjusting for simultaneous threats that cannot wait. Allocate remaining resources to the most consequential untreated concern, then sustained career development. Select among viable choices by supported benefit and downside. All Skills share that ordering.

An urgent risk generally receives the dedicated Energy treatment and protective main action if feasible. A mild unresolved risk receives a relevant protective measure while leaving room for a growth/performance main action. A clear state does not impose routine protection. These are candidate policy choices, not claims about engine thresholds or the optimal protective dose. Their opportunity cost requires gameplay evaluation.

## Memory contract

Every action records a compact pre-action state, unresolved concerns, risk-specific evidence, last response, quarter baseline, review, provisional focus/expiry, remaining plan, and directional expectation. The next observation supplies actual effects. The next action note carries the updated ledger, so a context reset need not rediscover a warning from its original log entry.

The baseline changes only at the next quarter's first allocation checkpoint, after comparison. Focus expires at the next quarter; it can change earlier on promotion, a serious warning, or contradiction. Risk evidence has a different lifetime: it persists until specific feedback changes it. These lifetimes prevent both forgetting threats and carrying an unsupported promotion hypothesis forever.

The note is intentionally shorter than the public runner's maximum. On overflow, retain concerns and checkpoint data before the explanatory reason. Missing historical evidence remains unknown.

A weak formal review activates a delivery check through the next review. The ledger carries one observed comparison at the current level. Resource and event choices use it within the same protection priorities. A promotion expires the old comparison.

## Generalisation and runtime cost

Action IDs, availability, costs, and effects come from the current menu. The Skills have no event titles, answer tables, fixed review-phase assumptions, fitted numeric margins, or invented success probabilities. They use the public horizon, published statistic ranges, and the interface contract. They continue to actual terminal feedback even at month 48.

All operational instructions are in five `SKILL.md` files. The bibliography stays in design documentation, so the game agent does not fetch books or read a theory library each turn. Runtime scripts and per-Skill reference trees would add unnecessary tool use for these decisions. Loading five Skills still has an input cost; no token-saving claim is made before measurement.

## How the reading informed the design

The source notes in [sources.md](sources.md) distinguish actual excerpts from companion materials. Meadows informed the separation of net observation from causal explanation. Goldratt informed a revisable development focus. Duke informed uncertainty labels. Gawande informed short checks at transitions. Rumelt informed the requirement that a diagnosis lead to a feasible coordinated plan. Translating those ideas into this game's rules is our design work, not a strategy prescribed by those authors.
