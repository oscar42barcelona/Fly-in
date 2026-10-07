from sys import argv
from validator import Map_
from pydantic import ValidationError

class receiver:
    def reader(self) -> list[str]:
        """Lee las líneas del archivo indicado como argumento."""
        with open(argv[1], "r") as file:
            return file.readlines()

    def FormatMap(self, line: str) -> dict[str, int | str]:
        """Formatea la línea que declara nb_drones."""
        clave, valor = line.split(":", 1)
        return {clave.strip(): valor.strip()}

    def typer(self, hub_type: str) -> str:
        if hub_type.startswith("start_hub"):
            return "entry"
        elif hub_type.startswith("end_hub"):
            return "exit"
        else:
            return "intermediate"

    def FormatHub(self, line: str, number: int) -> dict[str, int | str]:
        """Formatea una línea de hub, inicio o destino."""
        hub_dict: dict[str, int | str] = {}

        if not line.__contains__(':'):
            raise ValueError(
                f"Line {number}: Missing ':'. Content: {line}")

        hub_type, line = line.split(":", 1)
        hub_type = hub_type.strip()
        hub_dict["type"] = self.typer(hub_type)

        line = line.strip()
        name_coord: str = line

        if '[' in line:
            name_coord, zone_color_max = line.split("[", 1)
            name_coord = name_coord.strip()
            zone_color_max = zone_color_max.strip()

            if not zone_color_max.endswith(']'):
                raise ValueError(
                    f"Line {number}: Missing ']'. Content: {line}")

            zone_color_max = zone_color_max[:-1]
            zone_color_max = zone_color_max.split(' ', 3)

            for item in zone_color_max:
                item = item.strip()

                if not item.__contains__('='):
                    raise ValueError(
                    f"Line {number}: Missing '='. Content: {line}")

                clave, valor = item.split('=', 1)
                hub_dict[clave.strip()] = valor.strip()

        if name_coord.count(' ') != 2:
            raise ValueError(
                f"Line {number}: Missing Space. Content: {line}")

        name, x, y = name_coord.split(' ', 2)
        hub_dict["name"] = name.strip()
        hub_dict["x"] = x.strip()
        hub_dict["y"] = y.strip()

        return hub_dict
            

    def FormatConnection(self, line: str, number: int) -> dict[str, int | str]:
        """Formatea una línea de conexión."""
        connections_dict: dict[str, int | str] = {}

        if not line.__contains__(':'):
            raise ValueError(
                f"Line {number}: Missing ':'. Content: {line}")

        line = line.split(":", 1)[1].strip()

        connections: str = line

        if '[' in line:
            connections, link_capacity = line.split("[", 1)
            link_capacity = link_capacity.strip()
        
            if not link_capacity.endswith(']'):
                raise ValueError(
                    f"Line {number}: Missing ']'. Content: {line}")

            link_capacity = link_capacity[:-1]

            if not link_capacity.__contains__('='):
                    raise ValueError(
                    f"Line {number}: Missing '='. Content: {line}")

            link_capacity = link_capacity.split('=', 1)[1].strip()
            connections_dict["link_capacity"] = link_capacity

        connections = connections.strip()

        if not connections.__contains__('-'):
                    raise ValueError(
                    f"Line {number}: Missing '-'. Content: {line}")
        
        hub1, hub2 = connections.split('-', 1)
        hub1 = hub1.strip()
        hub2 = hub2.strip()

        connections_dict["hub1"] = hub1
        connections_dict["hub2"] = hub2

        return connections_dict
        
    def slicer(self, lines: list[str]) -> dict[str, object]:
        hubs: list[dict[str, int | str]] = []
        connections: list[dict[str, int | str]] = []
        mapa: dict[str, object] = {}

        for number, line in enumerate(lines, start=1):

            if number == 1 and not line.startswith("nb_drones:"):
                raise ValueError(
                    f"Line {number}: Nb_drones must be at the very",
                    f"first_line. Content: {line}")

            line = line.split("#", 1)[0].strip()

            if not line:
                continue

            if line.startswith("nb_drones:"):
                mapa.update(self.FormatMap(line))

            elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                hub = self.FormatHub(line, number)
                hubs.append(hub)

                if line.startswith("start_hub:"):
                    mapa["start_hub"] = hub["name"]
                elif line.startswith("end_hub:"):
                    mapa["end_hub"] = hub["name"]

            elif line.startswith("connection:"):
                connection = self.FormatConnection(line, number)
                connections.append(connection)
            else:
                raise ValueError(
                    f"Line {number}: Unknown prefix. Content: {line}")

        mapa["hubs"] = hubs
        mapa["connections"] = connections

        return mapa
    
    def Process(self) -> Map_ | None:
        try:
            list_lines: list[str] = self.reader()
            dictforpy: dict[str, object] = self.slicer(list_lines)
            return Map_.model_validate(dictforpy)

        except IndexError as error:
            print(f"We need a map to run :)")
        except FileNotFoundError as error:
            print(error)
        except PermissionError as error:
            print(error)
        except ValidationError as error:
            for item in error.errors():
                print(item["loc"])
                print(item["msg"])
                print(item["input"])
        except ValueError as error:
            print(error)
