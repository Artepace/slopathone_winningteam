# slopathone_winningteam — Career Survival Agent

Official TechArena starter plus an initial preliminary design.

## Start here

- `preliminary/manifest.json`: team identity and single-agent instructions.
- `preliminary/design/skills_design.md`: proposed strategy, responsibilities, risks, and validation plan.
- `preliminary/skills/career-strategy/SKILL.md`: initial decision instructions.

The preliminary design is untested. Confirm that `slopathone_winningteam` matches your registered team name before submitting it.

Submit the filled `preliminary/` package on https://techarena-uk.hydro.ac/ for organiser verification and an API key. Pushing to GitHub does not submit an entry. No presentation video is needed for the preliminary package.

## Local development

Follow the official quickstart:
https://techarena-career-sim.readthedocs.io/en/latest/quickstart.html

1. Run `make sync` to install the pinned dependencies, including JiuwenSwarm 0.2.4b3.
2. After receiving organiser-issued credentials, copy `.env.example` to `.env` and enter the supplied values locally.
3. Follow the quickstart to configure and start the instance.
4. Copy `example_submission_structure/` to `solution/`. Transfer the preliminary manifest, design, and career-strategy Skill into the working copy; remove the example skill-name folder.
5. Replace the remaining sample documents before final submission. The example video is empty; supply your own English video for the final ZIP.
6. Use `make play`, `make score`, and `make replay` to develop and inspect results.

The official starter ignores `solution/`; this repository tracks the initial design under `preliminary/`. Decide how to version the completed working solution when final development begins.

Keep API keys and `.env` out of version control. Never commit the local simulation database or attempt to read hidden game internals.

## Final submission

The final ZIP must contain one `solution/` directory with the manifest, README, presentation video, both required design documents, and at least one Skill. Run the official validation command before packaging:

```sh
uv run python -m career_sim_runner validate --submission solution
```

A preliminary design is not a complete final submission.

## Source and licence

Starter source: https://github.com/RAI-Internal/techarena-career-sim
Imported tree: `00b084a88732d81e595db88b26dde90d44e72d87`.

The original starter README is preserved in [STARTER_README.md](STARTER_README.md). The upstream MIT licence is preserved in [LICENSE](LICENSE). The official documentation and competition rules remain authoritative.
