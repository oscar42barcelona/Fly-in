"""Static checks for mandatory object orientation and module boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

CORE_CLASSES = (
    ("cli.py", "FlyInCLI"),
    ("input/formatter_algorithm_integrado.py", "SimulationRunner"),
    ("input/formatter_algorithm_integrado.py", "SimulationResult"),
    ("input/receiver.py", "receiver"),
    ("input/validator.py", "Map_"),
    ("DroneGen/Graph/Drone.py", "Drone"),
    ("DroneGen/Graph/Map.py", "Graph"),
    ("DroneGen/Graph/MapFactory.py", "Factory"),
    ("DroneGen/Flygorithm/Algorithm.py", "Algorithm"),
    ("DroneGen/Orchestrator.py", "orchestrator"),
    ("DroneGen/Planning/TurnPlanner.py", "TurnPlanner"),
    ("ui/visualizer/plotly_test.py", "plotlyzer"),
    ("ui/visualizer/turn_positions.py", "TurnPositionReplayer"),
    ("ui/visualizer/simulation_service.py", "SimulationService"),
    ("ui/interface/turn_view.py", "TurnFigureView"),
    ("ui/interface/app.py", "FlyInApp"),
)


class ArchitectureInspector:
    """Analyze Python syntax without importing optional UI dependencies."""

    def __init__(self, root: Path) -> None:
        """Locate source modules in the checkout."""
        self.root = root

    def tree(self, relative_path: str) -> ast.Module:
        """Parse a source file into an AST."""
        source = (self.root / relative_path).read_text(
            encoding="utf-8"
        )
        return ast.parse(source, filename=relative_path)

    @staticmethod
    def imports(tree: ast.Module) -> set[str]:
        """Collect import roots including imports nested in methods."""
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        return names


@pytest.mark.parametrize(("path", "class_name"), CORE_CLASSES)
def test_core_implementation_is_class_based(
    path: str, class_name: str
) -> None:
    """Require each main subsystem to retain its OO entry point."""
    tree = ArchitectureInspector(ROOT).tree(path)
    classes = {
        node.name for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    assert class_name in classes, path


def test_engine_has_no_forbidden_graph_libraries() -> None:
    """Graph representation and routing must use project code only."""
    inspector = ArchitectureInspector(ROOT)
    forbidden = {"networkx", "graphlib", "igraph", "rustworkx"}
    for path in (ROOT / "DroneGen").rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        assert not (inspector.imports(inspector.tree(relative)) & forbidden), (
            f"Forbidden graph library imported by {relative}"
        )


def test_algorithm_and_input_do_not_depend_on_presentation() -> None:
    """The engine and parser should remain usable without Plotly/Streamlit."""
    inspector = ArchitectureInspector(ROOT)
    for package in ("DroneGen", "input"):
        for path in (ROOT / package).rglob("*.py"):
            if "tests" in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            imports = inspector.imports(inspector.tree(relative))
            assert not (imports & {"plotly", "streamlit"}), relative


def test_cli_and_simulation_have_no_unguarded_module_side_effects() -> None:
    """Importing the CLI must not start a simulation or open a browser."""
    inspector = ArchitectureInspector(ROOT)
    for relative in ("cli.py", "input/formatter_algorithm_integrado.py"):
        tree = inspector.tree(relative)
        operations = [
            node for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
        ]
        assert not operations, relative


def test_shared_runner_returns_typed_engine_result() -> None:
    """Both CLI and visualization can consume the same calculated turns."""
    from input.formatter_algorithm_integrado import (
        SimulationResult,
        SimulationRunner,
    )

    result = SimulationRunner(
        str(ROOT / "maps/easy/01_linear_path.txt")
    ).simulate()
    assert isinstance(result, SimulationResult)
    assert result.total_drones == 2
    assert len(result.movements) == 4
