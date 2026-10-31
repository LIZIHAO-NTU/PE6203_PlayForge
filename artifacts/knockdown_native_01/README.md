# Knockdown generated project and run evidence

This folder contains the saved native Python game and its original generation traces.
It is an artifact snapshot, not a change to the main agent or the frozen S1–S5 evaluation.

## Run locally

Download or clone this branch, then open a terminal in this folder:

```sh
cd artifacts/knockdown_native_01
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash knockdown/run.sh
```

A desktop graphical session is required. The game opens in a standalone window;
GitHub and GitHub Pages do not run this Python game. No API key is needed to play.
If needed, select the installed interpreter with `PLAYFORGE_PYTHON`.

## Controls

- Left / Right: orbit camera.
- Up / Down: adjust view and aim.
- Hold Space: charge; release Space: throw.
- R: reset.
- Q / Escape: quit.

## Contents and verification scope

- `knockdown/`: original generated game, README and launcher, unchanged.
- `traces/`: original specification, plan, API request/response and controller events.
- `summary.json` and `REPORT.md`: original generation status.
- `SHA256SUMS.json`: hashes of the original uploaded run files.

Recorded model: DeepSeek Flash. One API attempt generated this project.
The recorded status is `native_generated_manual_pending`. Source syntax validation
passed. Actual-window screenshots, required-key checks, physics and gameplay
acceptance were not verified by the controller. Do not describe this artifact as
fully tested. The generated game's README describes its intended behavior, not
independent proof of compliance.

The added requirements and this README are handoff documentation; the generated
code and original run records have not been rewritten. Configured API credentials
were checked against the proposed upload. No local .env or virtual environment
is included. Retain original failures and verification limits when reporting.
