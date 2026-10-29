# Career experiment tools

These tools prepare immutable solution versions, run approved experiments and build a small version/result catalog under `lab/`.

- `controller.py`: one isolated snapshot per approved run, live output, status, report attribution and local validation.
- `parallel.py`: prepare two or three independent Linux workers sharing installed Python dependencies, then explicitly launch one fixed batch.
- `catalog.py`: register immutable solution labels and import compact results, with report-hash deduplication and source checks.
- `github_sources.py`: discover solution ZIPs on an exact public GitHub commit and inspect/download them without executing archive contents.
- `Career-Lab.ps1`: optional Windows/WSL launcher. Pass `-LinuxWorkspace` and `-Distro` if your paths differ from its local defaults.

Use Python 3.11+; run actual Career Survival experiments with the competition-pinned project environment (JiuwenSwarm 0.2.4b3). Do not update the official runner or model configuration to use these scripts.

Example commands inside Linux (replace paths and identifiers):

```bash
python tools/experiments/controller.py --workspace /path/to/project stage /path/to/solution.zip --name v4
python tools/experiments/parallel.py --workspace /path/to/project prepare CANDIDATE_ID --version V4 --count 3
python tools/experiments/parallel.py --workspace /path/to/project status
```

Preparation creates private child homes, ports, model settings and workspaces but does not start services or games. It copies the three model configuration fields from the project's local `.env`; neither private homes nor `.env` belong in Git. Dependencies are linked from the existing environment to save disk space.

The next command really launches a paid three-game batch. Run it only after the person controlling the API balance has authorized all three games:

```bash
python tools/experiments/parallel.py --workspace /path/to/project run BATCH_ID --approved
```

Each worker remains a single-agent competition run. Workers use separate databases, memory, configuration and service ports. The supervisor prevents overlapping batches and leaves other existing games untouched. Failed games do not automatically retry. One failed worker does not cancel its siblings. Insufficient RAM or API concurrency limits can prevent the expected speedup.

Populate the catalog locally:

```bash
python tools/experiments/catalog.py --root lab register V5 /path/to/new.zip --provenance IMMUTABLE_SOURCE_URL
python tools/experiments/catalog.py --root lab import-managed V4 /path/to/project/.experiments/runs/RUN_ID
python tools/experiments/catalog.py --root lab import-batch /path/to/project BATCH_ID
```

Different files cannot replace a registered version. Re-importing the same report is idempotent. Results use version labels such as `V4_1`, `V4_2`; a later batch continues numbering instead of overwriting them. Compact reports omit credentials, databases, local absolute paths and raw transcripts. Imported historical results state their source limitations.

These scripts never commit or push. Review `lab/` and `tools/experiments/` before publishing and preserve unrelated working-tree changes.

Tests use local synthetic processes and sanitized report fixtures; they do not start real games or call model APIs:

```bash
python -m unittest discover -s tools/experiments/tests -v
```
