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
        name_coord = line

        if "[" in line:
            name_coord, features = line.split("[", 1)
            name_coord = name_coord.strip()
            features = features.strip()

            if not features.endswith("]"):
                raise ValueError(
                    f"Line {number}: Missing ']'. Content: {line}"
                )

            features = features[:-1]
            for item in features.split(" ", 3):
                item = item.strip()
                if "=" not in item:
                    raise ValueError(
                        f"Line {number}: Missing '=' or extra space. "
                        f"Content: {line}"
                    )

                key, value = item.split("=", 1)
                if key not in permitted:
                    raise ValueError(
                        f"Line {number}: wrong spelling :(. "
                        f"Content: {line}"
                    )

                if key in seen:
                    raise ValueError(
                        f"Line {number}: Non repeated features, please :) "
                        f"Content: {line}"
                    )
                seen.add(key)
                result[key.strip()] = value.strip()

        if name_coord.count(" ") != 2:
            raise ValueError(
                f"Line {number}: Missing or extra Space. Content: {line}"
            )

        name, x, y = name_coord.split(" ", 2)
        result["name"] = name.strip()
        result["x"] = x.strip()
        result["y"] = y.strip()
        return result

    def FormatConnection(self, line: str, number: int) -> dict[str, str]:
        """Read a link declaration and optional capacity metadata."""
        result: dict[str, str] = {}

        if ":" not in line:
            raise ValueError(
                f"Line {number}: Missing ':'. Content: {line}"
            )

        line = line.split(":", 1)[1].strip()
        connection_text = line

        if "[" in line:
            connection_text, capacity = line.split("[", 1)
            capacity = capacity.strip()

            if not capacity.endswith("]"):
                raise ValueError(
                    f"Line {number}: Missing ']'. Content: {line}"
                )

            capacity = capacity[:-1].strip()
            if " " in capacity:
                raise ValueError(
                    f"Line {number}: Extra Space or args. Content: {line}"
                )

            if "=" not in capacity:
                raise ValueError(
                    f"Line {number}: Missing '='. Content: {line}"
                )

            key, value = capacity.split("=", 1)
            if key.strip() != "max_link_capacity":
                raise ValueError(
                    f"Line {number}: Invalid connection capacity key. "
                    f"Content: {line}"
                )
            result["link_capacity"] = value.strip()

        connection_text = connection_text.strip()
        if "-" not in connection_text:
            raise ValueError(
                f"Line {number}: Missing '-'. Content: {line}"
            )

        hub1, hub2 = connection_text.split("-", 1)
        result["hub1"] = hub1.strip()
        result["hub2"] = hub2.strip()
        return result

    def slicer(self, lines: list[str]) -> dict[str, object]:
        """Split declarations into hubs, connections and map metadata."""
        hubs: list[dict[str, str]] = []
        connections: list[dict[str, str]] = []
        data: dict[str, object] = {}

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
                data.update(self.FormatMap(line))
                self.index_nbdrones.append(number)

            elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                hub = self.FormatHub(line, number)
                hubs.append(hub)
                self.index_hubs.append(number)

                if line.startswith("start_hub:"):
                    data["start_hub"] = hub["name"]
                elif line.startswith("end_hub:"):
                    data["end_hub"] = hub["name"]

            elif line.startswith("connection:"):
                connection = self.FormatConnection(line, number)
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

    def Process(self) -> Map_ | None:
        """Read, parse and validate the map; print input errors if needed."""
        try:
            lines = self.reader()
            parsed = self.slicer(lines)
            context = self.context_creator()
            return Map_.model_validate(parsed, context=context)
        except IndexError:
            print("We need a map to run :)")
        except (FileNotFoundError, PermissionError) as error:
            print(error)
        except ValidationError as error:
            for item in error.errors():
                self.print_error(item, context)
        except ValueError as error:
            print(error)
        return None
