"""Read, parse and validate textual Fly-in map files."""

from __future__ import annotations

from sys import argv

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from .validator import Map_


class receiver:
    """Convert the map text format into the project's validated model."""

    def __init__(self, path: str | None = None) -> None:
        """Store the map path and line numbers used for error messages."""
        self.path = path
        self.index_hubs: list[int] = []
        self.index_connections: list[int] = []
        self.index_nbdrones: list[int] = []

    def reader(self) -> list[str]:
        """Read a supplied map or the first command-line argument."""
        if self.path is None and len(argv) <= 1:
            raise ValueError("Line 1: map file path is required")
        path = self.path if self.path is not None else argv[1]
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()

    def FormatMap(self, line: str) -> dict[str, str]:
        """Read the declared number of drones."""
        key, value = line.split(":", 1)
        return {key.strip(): value.strip()}

    def typer(self, hub_type: str) -> str:
        """Classify a hub declaration."""
        if hub_type.startswith("start_hub"):
            return "entry"
        if hub_type.startswith("end_hub"):
            return "exit"
        return "intermediate"

    def FormatHub(self, line: str, number: int) -> dict[str, str]:
        """Read a hub declaration and its optional attributes."""
        result: dict[str, str] = {}
        seen: set[str] = set()
        permitted = {"color", "max_drones", "zone"}

        if ":" not in line:
            raise ValueError(
                f"Line {number}: Missing ':'. Content: {line}"
            )

        hub_type, line = line.split(":", 1)
        result["type"] = self.typer(hub_type.strip())

        line = line.strip()
        if line.count("[") > 1 or line.count("]") > 1:
            raise ValueError(f"Line {number}: invalid metadata: {line}")
        if "]" in line and "[" not in line:
            raise ValueError(f"Line {number}: stray ']': {line}")

        name_coord = line
        if "[" in line:
            name_coord, features = line.split("[", 1)
            if not features.endswith("]"):
                raise ValueError(
                    f"Line {number}: missing closing ']': {line}"
                )
            entries = features[:-1].split()
            if not entries:
                raise ValueError(f"Line {number}: empty metadata: {line}")
            for item in entries:
                if item.count("=") != 1:
                    raise ValueError(
                        f"Line {number}: invalid metadata item: {item}"
                    )
                key, value = item.split("=", 1)
                if key not in permitted:
                    raise ValueError(
                        f"Line {number}: unknown hub metadata: {key}"
                    )
                if key in seen:
                    raise ValueError(
                        f"Line {number}: duplicate hub metadata: {key}"
                    )
                if not value:
                    raise ValueError(
                        f"Line {number}: empty value for {key}"
                    )
                seen.add(key)
                result[key] = value

        coordinates = name_coord.split()
        if len(coordinates) != 3:
            raise ValueError(
                f"Line {number}: expected name and two coordinates: {line}"
            )
        name, x, y = coordinates
        result["name"] = name
        result["x"] = x
        result["y"] = y
        return result

    def FormatConnection(self, line: str, number: int) -> dict[str, str]:
        """Read a link declaration and optional capacity metadata."""
        result: dict[str, str] = {}

        if ":" not in line:
            raise ValueError(
                f"Line {number}: Missing ':'. Content: {line}"
            )

        line = line.split(":", 1)[1].strip()
        if line.count("[") > 1 or line.count("]") > 1:
            raise ValueError(f"Line {number}: invalid metadata: {line}")
        if "]" in line and "[" not in line:
            raise ValueError(f"Line {number}: stray ']': {line}")

        connection_text = line
        if "[" in line:
            connection_text, metadata = line.split("[", 1)
            if not metadata.endswith("]"):
                raise ValueError(
                    f"Line {number}: missing closing ']': {line}"
                )
            entries = metadata[:-1].split()
            if len(entries) != 1 or entries[0].count("=") != 1:
                raise ValueError(
                    f"Line {number}: expected one link capacity: {line}"
                )
            key, value = entries[0].split("=", 1)
            if key != "max_link_capacity" or not value:
                raise ValueError(
                    f"Line {number}: invalid connection metadata: {line}"
                )
            result["link_capacity"] = value

        connection_text = connection_text.strip()
        if connection_text.count("-") != 1:
            raise ValueError(
                f"Line {number}: expected zone1-zone2: {line}"
            )
        hub1, hub2 = connection_text.split("-", 1)
        if not hub1 or not hub2:
            raise ValueError(
                f"Line {number}: connection endpoints missing: {line}"
            )
        result["hub1"] = hub1.strip()
        result["hub2"] = hub2.strip()
        return result

    def slicer(self, lines: list[str]) -> dict[str, object]:
        """Split declarations into hubs, connections and map metadata."""
        hubs: list[dict[str, str]] = []
        connections: list[dict[str, str]] = []
        data: dict[str, object] = {}
        declared_hubs: set[str] = set()
        self.index_hubs.clear()
        self.index_connections.clear()
        self.index_nbdrones.clear()

        first_data_line = True
        for number, line in enumerate(lines, start=1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

            if first_data_line:
                if not line.startswith("nb_drones:"):
                    raise ValueError(
                        f"Line {number}: nb_drones must be the first "
                        f"declaration. Content: {line}"
                    )
                first_data_line = False

            if line.startswith("nb_drones:"):
                if self.index_nbdrones:
                    raise ValueError(
                        f"Line {number}: duplicate nb_drones declaration"
                    )
                data.update(self.FormatMap(line))
                self.index_nbdrones.append(number)

            elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                hub = self.FormatHub(line, number)
                hubs.append(hub)
                declared_hubs.add(hub["name"])
                self.index_hubs.append(number)

                if line.startswith("start_hub:"):
                    data["start_hub"] = hub["name"]
                elif line.startswith("end_hub:"):
                    data["end_hub"] = hub["name"]

            elif line.startswith("connection:"):
                connection = self.FormatConnection(line, number)
                if (
                    connection["hub1"] not in declared_hubs
                    or connection["hub2"] not in declared_hubs
                ):
                    raise ValueError(
                        f"Line {number}: connection endpoints must "
                        "refer to previously defined zones"
                    )
                connections.append(connection)
                self.index_connections.append(number)
            else:
                raise ValueError(
                    f"Line {number}: Unknown prefix. Content: {line}"
                )

        data["Hubs"] = hubs
        data["Connections"] = connections
        return data

    def context_creator(self) -> dict[str, list[int]]:
        """Provide source line numbers for field validation errors."""
        return {
            "nb_drones": self.index_nbdrones,
            "Hubs": self.index_hubs,
            "Connections": self.index_connections,
        }

    def print_error(
        self, item: ErrorDetails, context: dict[str, list[int]]
    ) -> None:
        """Print a Pydantic validation error with its source line."""
        loc = item["loc"]
        size = len(loc)

        if loc and loc[0] == "nb_drones":
            print(f"Error in {loc} line: {context['nb_drones']}", end=". ")
        elif item["type"] == "custom_validation_error":
            details = item.get("ctx") or {}
            if details:
                key, index = next(iter(details.items()))
                key = str(key)
                if isinstance(index, int) and key in context:
                    if loc:
                        print(
                            f"Error in {loc} line: {context[key][index]}",
                            end=". ",
                        )
                    else:
                        print(
                            f"Error in line: {context[key][index]}",
                            end=". ",
                        )
        elif size > 1:
            location = str(loc[0])
            index = loc[1]
            if location in context and isinstance(index, int):
                print(
                    f"Error in {loc} line: {context[location][index]}",
                    end=". ",
                )

        print(item["msg"])

    def load(self) -> Map_:
        """Parse a map or raise a readable error with its source line."""
        lines = self.reader()
        parsed = self.slicer(lines)
        context = self.context_creator()
        try:
            return Map_.model_validate(parsed, context=context)
        except ValidationError as error:
            first = error.errors()[0]
            message = self._validation_message(first, len(lines))
            raise ValueError(message) from error

    def _validation_message(
        self, error: ErrorDetails, line_count: int
    ) -> str:
        """Resolve the location of a Pydantic error to a source line."""
        location = error["loc"]
        indices = self.context_creator()
        line_number = line_count + 1

        if location:
            category = str(location[0])
            if category in indices and indices[category]:
                location_index = (
                    location[1]
                    if len(location) > 1 and isinstance(location[1], int)
                    else 0
                )
                if location_index < len(indices[category]):
                    line_number = indices[category][location_index]

        details = error.get("ctx") or {}
        for category, index in details.items():
            if (
                category in indices
                and isinstance(index, int)
                and index < len(indices[category])
            ):
                line_number = indices[category][index]
                break

        return f"Line {line_number}: {error['msg']}"

    def Process(self) -> Map_ | None:
        """Retain the historical non-raising parser interface."""
        try:
            return self.load()
        except (OSError, ValueError) as error:
            print(error)
            return None
