# Reading sources and design adaptations

Accessed on **30 October 2026**, Europe/London. The material reviewed consists of public book excerpts and author/publisher material linked below, not full copies of five books. No purchase, private library access, pirated mirror, or claim of complete-book reading is involved. The summaries are paraphrases. Sources inform the design; they do not establish simulator mechanics or prove effectiveness.

## 1. Donella H. Meadows — Thinking in Systems: A Primer (2008)

- [Author-project book excerpt: Bathtubs 101, draft chapter](https://donellameadows.org/wp-content/userfiles/bathtubs101.pdf), especially the opening distinction between stocks/flows and the later discussion of inflows versus outflows.
- [Author-project excerpt: Dancing With Systems](https://donellameadows.org/dancing-with-systems/), especially observation history, visible assumptions, feedback-responsive policy, and attention to unmeasured concerns.

A stable stock can conceal simultaneous inflows and outflows. Models remain incomplete and should change with feedback. Our adaptation: `feedback-learning` treats a flat visible statistic as an unexplained net result, and `threat-control` preserves concerns not represented by a visible number. Neither procedure assumes that all game effects are observable immediately.

## 2. Eliyahu M. Goldratt and Jeff Cox — The Goal: A Process of Ongoing Improvement (1984)

- [North River Press: The Five Steps of Focusing](https://northriverpress.com/wp-content/uploads/2018/01/Free-download-5FS.pdf), pages 2–4. This publisher companion is explicitly adapted from Goldratt's *What Is This Thing Called the Theory of Constraints?*; it is not an excerpt of the complete novel. It connects the method to *The Goal*.

Prioritize a limiting constraint, coordinate resources around it, and revisit the diagnosis when conditions change. Our adaptation: select an evidence-backed provisional focus and a coherent allocation, then expire the focus at the next checkpoint. The game may have several interacting constraints; we do not assume its promotion system has exactly one bottleneck or that the smallest raw statistic identifies it.

## 3. Annie Duke — Thinking in Bets (2018)

- [Author's discussion of the book's uncertainty section](https://www.annieduke.com/trio-unlikely-truly-magical-words-annies-newsletter-jan-26th-2018/), paragraphs explaining incomplete knowledge and calibrated beliefs.
- [Publisher's book page](https://www.penguinrandomhouse.com/books/552885/thinking-in-bets-by-annie-duke/), description distinguishing a decision from its outcome.

Uncertain predictions should stay uncertain; a result alone does not establish decision quality. Our adaptation: distinguish expected from observed effects, avoid fabricated probabilities, compare a leading option with a credible alternative, and revise hypotheses without rewriting the original forecast. The game policy does not require numeric expected-value calculations unsupported by the interface.

## 4. Atul Gawande — The Checklist Manifesto: How to Get Things Right (2009)

- [Macmillan's authorised opening excerpt and book description](https://us.macmillan.com/books/9780312430009/thechecklistmanifesto/), especially the discussion that expertise alone does not prevent missed steps.

Knowledge can fail at execution when essential steps are omitted. Our adaptation: a short pre-action check and a fixed observation/action handoff in `session-ledger` and `event-judgment`. The particular fields and execution protocol were designed for the public game interface; they are not copied from a medical checklist or claimed to reproduce a full method from the book.

## 5. Richard Rumelt — Good Strategy/Bad Strategy (2011)

- [Profile Books authorised preview](https://profilebooks.com/wp-content/uploads/wpallimport/files/PDFs/9781847657466_preview.pdf), printed pages 6–7 (PDF pages 15–16), especially the distinction between ambition and coordinated action.

A useful strategy links a diagnosis to a guiding approach and feasible actions. Our adaptation: every quarter checkpoint states the obstacle, selects a policy, and produces one joint Energy/main-action plan. A goal such as promotion is not itself a diagnosis. No resource commitment is treated as feasible before checking the displayed budget.

## Task-specific authority

The local public participant documentation under `team/docs/` supplies the actual handbook, published action effects, official MCP interface, permitted platform/mode, language, and submission requirements. Retrospective failure evidence comes from the three local reviews named in `decision_report.md`. Those sources, not the books, determine task constraints. Their exact file fingerprints are preserved in the candidate's outer provenance record.

The books are design-time sources only. No Skill instructs the game agent to access these pages or load design documents during play.
