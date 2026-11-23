*This project has been created as part of the 42 curriculum by osuarez-*

# Fly-in

## Description

Fly-in is a Python drone-routing and turn-scheduling simulation for 42. A
text file describes connected zones, their coordinates, capacities, and
traffic rules. The program calculates routes and schedules simultaneous
movements until every drone reaches the exit.

The objective is to finish in as few simulation turns as possible while
respecting zone and connection capacities. Entering a **restricted** zone
takes two turns: a drone occupies its incoming connection during the first
turn and must arrive at the zone during the next.

The project includes command-line movement output, a Plotly map and turn
animation, and a Streamlit interface with playback and drone metrics.

## Instructions

### Installation

Use Python 3.12 or later. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

### Run from the terminal

```bash
make run MAP=maps/easy/01_linear_path.txt
```

Equivalent direct command:

```bash
python3 cli.py maps/easy/01_linear_path.txt
```

Each output line represents a turn. A movement is written as
`D<ID>-<zone>`, or `D<ID>-<connection>` while crossing a restricted
connection. Drones that do not move are omitted. Standard output contains
the movement records, not progress messages.

### Visualize the simulation

Export a standalone animated Plotly HTML:

```bash
python3 cli.py maps/medium/03_priority_puzzle.txt --visualize
```

This creates `flyin_preview.html` in the working directory without
launching a browser process. Open it manually in a browser.

Start the interactive Streamlit interface:

```bash
python3 -m streamlit run ui/interface/app.py
```

Select a map and use **Previous**, **Next**, **Play**, or **Pause**.
The interface displays the selected turn and three counts:

- **Delivered:** drones that have reached the exit.
- **In transit:** drones occupying a connection on the way to a restricted
  zone.
- **Waiting:** drones at non-exit zones that did not move during that turn.

Streamlit runs a local server. Stop it with **Ctrl+C** in the terminal;
closing the browser window alone does not stop the server.

### Development commands

```bash
make debug MAP=maps/easy/01_linear_path.txt
make lint
make clean
python3 -m pytest -q
```

`make lint` runs Flake8 and Mypy using the same Python interpreter as
the application. If `.venv/bin/python` exists, Make automatically uses
that environment even when it has not been activated. The Flake8 configuration
excludes virtual environments so installed libraries are not checked.
If either tool reports missing dependencies, run `make install` and retry.
Mypy retains the flags required by the subject.

The GitHub Actions workflow also verifies the nine mandatory
benchmark maps and capacity invariants.

## Example input and expected output

Save the following as `/tmp/flyin_example.txt`:

```text
nb_drones: 1
start_hub: start 0 0
hub: mid 1 0
end_hub: goal 2 0
connection: start-mid
connection: mid-goal
```

Run:

```bash
python3 cli.py /tmp/flyin_example.txt
```

Expected standard output:

```text
D1-mid
D1-goal
```

The drone moves one zone per turn, so this map takes two turns.

## Algorithm choices and implementation

The application has separate responsibilities rather than one combined
algorithm:

1. **Parsing and validation:** `input.receiver` reads declarations, and
   Pydantic models in `input.validator` check names, zone types,
   connections, capacities and other input constraints.
2. **Graph construction:** `DroneGen.Graph.MapFactory.Factory` creates
   `Node`, `Connection`, `Graph`, and `Drone` objects.
3. **Pathfinding:** `DroneGen.Flygorithm.Algorithm` uses Dijkstra to find
   a minimum-cost route and Yen's algorithm to generate alternative simple
   paths. Zone movement costs are used as edge-to-destination costs.
   Priority zones are preferred when total movement costs tie.
4. **Initial distribution:** `DroneGen.Orchestrator.orchestrator` assigns
   routes using estimated path cost plus the number of drones already
   allocated to each route. If all moves become blocked, it can reassign
   drones to viable, already computed alternative routes.
5. **Simultaneous turn scheduling:** `DroneGen.Planning.TurnPlanner`
   proposes movements, checks zone occupancy and connection capacities,
   accounts for simultaneous departures, and commits an approved set
   together. The planner reserves next-turn arrival space for restricted
   moves. It permits consecutive restricted crossings when the previous
   drone's next-turn departure directly to the unlimited exit is assured
   and the outgoing link has sufficient capacity.
6. **Presentation:** the CLI prints movement records.
   `ui.visualizer.plotly_test` builds Plotly figures; the historical
   snapshots and metrics are prepared by dedicated classes, and
   `ui.interface.app.FlyInApp` presents them through Streamlit.

The initial route allocation and greedy conflict resolution are
heuristics; finding several shortest paths does not guarantee globally
optimal multi-drone scheduling on every possible map.

## Mandatory subject benchmarks

The subject requires no more than **125% of the optimal turn count**
for each of its nine supplied easy, medium, and hard maps. The current
GitHub Actions benchmark tests check completion, movement output and
these limits; the movement-invariant tests separately check occupancy
and restricted-zone timing after every turn.

| Map | Subject optimum | Required maximum | Verified turns |
| --- | ---: | ---: | ---: |
| Easy 1 — Linear path | 4 | 5 | 4 |
| Easy 2 — Simple fork | 4 | 5 | 4 |
| Easy 3 — Basic capacity | 4 | 5 | 4 |
| Medium 1 — Dead end trap | 8 | 10 | 8 |
| Medium 2 — Circular loop | 10 | 12 | 10 |
| Medium 3 — Priority puzzle | 6 | 7 | 7 |
| Hard 1 — Maze nightmare | 13 | 16 | 13 |
| Hard 2 — Capacity hell | 16 | 20 | 20 |
| Hard 3 — Ultimate challenge | 26 | 32 | 27 |

Re-run `python3 -m pytest -q -s tests/test_subject_benchmarks.py` to
verify the results after changes to the routing engine.

## Project organization

```text
Fly-in/
├── cli.py
├── Makefile
├── dependencies.txt
├── input/                  # Map parsing, Pydantic models, CLI integration
├── DroneGen/
│   ├── Graph/              # Nodes, links, drones and factories
│   ├── Flygorithm/         # Dijkstra and Yen route search
│   ├── Planning/           # Simultaneous movement intents and capacities
│   └── Orchestrator.py     # Initial routes and turn execution
├── ui/
│   ├── visualizer/         # Historical positions, metrics, Plotly figures
│   └── interface/          # Streamlit controls and turn presentation
├── maps/                   # Subject examples, grouped by difficulty
├── tests/                  # Regression, movement and benchmark tests
└── archive/                # Superseded learning experiments as text
```

## Resources

- [Python documentation: `heapq`](https://docs.python.org/3/library/heapq.html)
  — priority queues used in shortest-path search.
- [Python documentation: `dataclasses`](https://docs.python.org/3/library/dataclasses.html)
  — immutable records and typed simulation data.
- [Pydantic documentation](https://docs.pydantic.dev/)
  — input validation and model field rules.
- [Plotly Python documentation](https://plotly.com/python/)
  — graph traces, frames and HTML animation.
- [Streamlit documentation](https://docs.streamlit.io/)
  — interface controls, fragments, state and caching.
- [NetworkX documentation: shortest paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
  — conceptual reference for pathfinding and graph traversal; Fly-in
  implements its own pathfinding logic.

### Use of AI

ChatGPT was used as a programming support tool for architectural
discussion, explanations of Dijkstra/Yen and scheduling concepts,
reviewing Python type annotations, correcting formatting and static
analysis issues, proposing Plotly/Streamlit visualization code,
investigating turn-capacity conflicts, and creating regression tests and
GitHub Actions benchmark checks. AI-assisted changes affect the
`DroneGen`, `input`, `ui`, testing, and documentation layers.
The repository code and the automated tests are the source of truth;
AI-generated suggestions must be reviewed and verified before submission.
