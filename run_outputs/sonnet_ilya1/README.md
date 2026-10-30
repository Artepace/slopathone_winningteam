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
