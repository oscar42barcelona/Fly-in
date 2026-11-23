# Mandatory Submission Audit

This checklist covers the **required** Fly-in project only. There is no
optional optimization or additional challenge work in this audit.

## Architecture and responsibilities

Fly-in uses object-oriented classes for its behavior:

| Area | Class | Responsibility |
| --- | --- | --- |
| CLI | `FlyInCLI` | Parse options, classify errors and handle Ctrl+C |
| Execution | `SimulationRunner` | Validate input, build a graph, run and print the simulation |
| Map input | `receiver`, `Map_`, `Hub`, `Connection` | Parse and validate map records |
| Graph | `Factory`, `Graph`, `Node`, `Drone` | Represent drones and zone/link capacities |
| Routing | `Algorithm` | Compute paths using project-owned Dijkstra and Yen implementations |
| Turn scheduling | `orchestrator`, `TurnPlanner` | Assign routes and approve simultaneous moves |
| Visualization | `plotlyzer`, `TurnPositionReplayer` | Replay positions without mutating graph state |
| Streamlit | `SimulationService`, `FlyInApp`, `PlaybackController` | Prepare display data and control playback |

The `main()` functions in `cli.py` and
`input/formatter_algorithm_integrado.py` are compatibility wrappers
rather than implementations of the business logic. The older lowercase
class names remain unchanged to avoid breaking existing imports.

**SRP:** parsing, turn scheduling and presentation live in distinct
components. This allows parser errors to be tested without opening Plotly.

**DIP / coupling boundary:** graph and route-planning modules do not import
Streamlit or Plotly. The visualization depends on the engine, not vice
versa. No external graph algorithms are used.

The static checks in `tests/test_architecture.py` guard these boundaries.
They check class entry points and forbidden imports; they are not a
mathematical proof of every possible design property.

## Mandatory evaluation coverage

- Nine provided maps: enforce the subject's 125% turn budget per map,
  check exact delivery and validate movement output formatting.
- Capacity invariants: inspect each simulated turn for illegal node or
  connection occupancy and delayed restricted-zone arrivals.
- Unseen valid maps: test direct links, large drone queues, restricted
  bottlenecks, priority alternatives, blocked zones, cycles and comments.
- Parser errors: test duplicate fields, unknown metadata, bad syntax,
  invalid types/capacities, undefined or forward-referenced zones,
  duplicate links and missing declarations. Invalid input must emit a
  line and cause without a Python traceback.
- Unsolvable but syntactically valid maps: report no route clearly.
- Deterministic loop protection: stop on a repeated global drone state
  with a clear error rather than running forever.
- Ctrl+C: print a concise interruption message, exit with code 130 and
  do not dump a traceback.
- Static checks: repository-wide Flake8 and Mypy with mandatory flags.
- Installation and execution: GitHub Actions creates a fresh `.venv`,
  runs `make install`, `make lint`, `make run` and validates the README.

## Commands for the final local check

From the project root, in a clean checkout:

```bash
python3 -m venv .venv
make install
make lint
.venv/bin/python -m pytest -q -s tests/test_subject_benchmarks.py
.venv/bin/python -m pytest -q -s tests/test_parser_adversarial.py
.venv/bin/python -m pytest -q -s tests/test_cli_interruptions.py
.venv/bin/python -m pytest -q -s tests/test_unseen_maps.py
.venv/bin/python -m pytest -q -s tests/test_architecture.py
make run MAP=maps/easy/01_linear_path.txt
python3 cli.py maps/medium/03_priority_puzzle.txt --visualize
make clean
git status --short
```

The visualizer creates `flyin_preview.html` locally; it is ignored by
Git and removed by `make clean`.

## Known boundaries

- Exact turn counts for **unfamiliar** maps are not benchmarked against
  an unknown optimum. The subject's compulsory 125% thresholds apply to
  the nine provided maps.
- Routing and conflict resolution use heuristics. An unfamiliar solvable
  map can still expose a scheduling limitation; the program should fail
  clearly rather than run indefinitely.
- Human review should still verify Streamlit interaction, geometry,
  custom colors and local browser settings.
- This audit makes no claims about optional performance goals or
  evaluation exercises beyond the mandatory submission behavior.
