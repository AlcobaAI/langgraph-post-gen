This folder contains simple root-level workflow test helpers for the main app.

They run the `/generate` workflow for these scenarios:

- `1 post x 1 platform`
- `1 post x 3 platforms`
- `3 posts x 1 platform`
- `3 posts x 3 platforms`
- `3 posts x all platforms`
- `10 posts x all platforms`

The scripts save only pretty-printed JSON outputs.

Output folders are separated by persona mode:

- `workflow_tests/outputs/single_persona/`
- `workflow_tests/outputs/multi_persona/`

Prerequisites:

```bash
docker compose up --build -d
```

Run all scenarios with a single persona (`sharp_operator`):

```bash
docker compose exec app python workflow_tests/run_workflow_tests.py
```

Run persona comparison scenarios:

```bash
docker compose exec app python workflow_tests/run_workflow_tests_multi_persona.py
```

The persona comparison runner keeps `angleCount=1` and focuses on:

- single-persona comparisons across `linkedin`, `instagram`, and `x`
- one explicit `platformPersonaPairs` example
