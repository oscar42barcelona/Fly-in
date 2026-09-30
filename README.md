# Fly-in

A 42 project that simulates drones moving through a network of connected zones. It includes input validation, movement planning, interactive visualization, and terminal output.

**Currently developed by:** `osuarez-`.

## Project Structure

```text
flyin/
├── cli.py                     # Coordinates the flow between input, DroneGen, and UI.
│
├── input/                     # Data reception, validation, and formatting.
│   ├── __init__.py            # Marks this directory as a package.
│   ├── receiver.py            # Receives input data.
│   ├── validator.py           # Validates input data using Pydantic.
│   └── formatter.py           # Converts validated data into the format DroneGen expects.
│
├── dronegen/                  # Graph, drones, and movement planning.
│   ├── flygorithm/            # Algorithmic logic.
│   │   ├── __init__.py        # Marks this directory as a package.
│   │   └── base.py            # Defines inputs, outputs, and the abstract method.
│   │
│   └── graph/                 # Objects containing the information the algorithm needs.
│       ├── __init__.py        # Marks this directory as a package.
│       ├── node.py            # Represents a graph node or zone.
│       └── drone.py           # Represents a drone and its state.
│
└── ui/                        # Visualization, interface, and terminal output.
    ├── __init__.py            # Marks this directory as a package.
    │
    ├── visualizer/            # Translates domain data into visual properties.
    │   ├── __init__.py        # Marks this directory as a package.
    │   └── ...                # Internal files will build traces and a Figure using Plotly.
    │
    ├── interface/             # Displays the Figure, controls, metrics, and text.
    │   ├── __init__.py        # Marks this directory as a package.
    │   └── ...                # Internal files will use Streamlit.
    │
    └── terminal.py            # Formats and prints drone movements for each turn.
```

## Responsibilities

### Orchestrator

`cli.py` coordinates the flow between the three main blocks.

### Input

- `receiver.py`: receives data from the corresponding input source.
- `validator.py`: validates the received data using Pydantic.
- `formatter.py`: converts validated data into the format consumed by DroneGen.

### DroneGen

- `graph/`: contains the objects representing nodes and drones, together with the information required by the algorithm.
- `flygorithm/`: contains the logic for planning and resolving drone movements.
- `flygorithm/base.py`: defines the algorithm's input, output, and required abstract method.

### UI

- `visualizer/`: translates domain data into visual properties and builds Plotly traces and a Figure.
- `interface/`: receives the Figure and simulation summaries, then displays them with controls, metrics, and text using Streamlit.
- `terminal.py`: formats and prints simulation movements using the required terminal output format.

The translation into visual properties belongs to `visualizer/`, keeping the graph logic independent of Plotly. Directory names describe responsibilities rather than technologies.
