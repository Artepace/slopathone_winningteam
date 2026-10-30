# SONNET_ILYA1 — full public run outputs

Three simultaneous games used the final sonnet_ilya1_solution.zip from commit 5a171f075ad11c489eef04f60d1c59dbdc3e354a. The earlier sequential launch was cancelled by the user and is excluded.

| Run | Score | Months | Level | Outcome | Full outputs |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 61.16 | 48 | L5 | Completed | [run_1](run_1/) |
| 2 | 65.88 | 48 | L5 | Completed | [run_2](run_2/) |
| 3 | 73.25 | 48 | L5 | Completed, report export failed | [run_3](run_3/) |

The mean of the three verified game outcomes is 66.76. All three completed 48 months. The [verified game results](verified_game_results.json) keep game outcomes separate from report export reliability.

## Files and recovery

Runs 1 and 2 contain the original score_report.json and full public events JSONL.

Run 3 contains the original events JSONL, recovered-ending-score.json and runner_status.json. Its runner exited with code 1 and did not create score_report.json. The exact ending_score was recovered from a terminal public observe response in its own event stream. It reports 73.25 points, completed=true and 48 survival months. It was copied from the game response rather than calculated from the visible stats. The recovery file records the source line and event-file SHA256, and preserves the failed runner status separately.

The [index](index.json) records source identity and file SHA256 values. The three sessions are distinct and their frozen submissions all match the same solution SHA256.

Only the simultaneous batch 20261030T212442Z-55c222 is included.

## Full recovery and diagnosed export error

Run 3 now includes a [reconstructed score report](run_3/score_report.recovered.json), a [full readable replay](run_3/full_replay.md) and [diagnosis](run_3/diagnosis.json).

The terminal game response arrived at 22:03:37 UTC. The preserved service diagnostic then records a WebSocket close with code 1011 and reason keepalive ping timeout at 22:04:13 UTC. The runner exited before the normal score-report export. The underlying reason the keepalive response was missed is unknown.

All 203 successful chosen actions are preserved. The official replay renderer pairs 202 with preceding observations; the additional successful action is included explicitly in the replay appendix. All six final scoring dimensions and the 73.25 score are copied from the game response.

The reconstructed JSON retains runner exit code 1. Final token and cost totals are unknown and use null values. The usage blocks received before the failure are supplied separately under recorded_token_usage. Their subtotal is incomplete.
