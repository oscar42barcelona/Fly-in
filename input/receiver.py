from sys import argv


class receiver:
    def reader(self) -> list[str]:
        """Lee las líneas del archivo indicado como argumento."""
        with open(argv[1], "r") as file:
            return file.readlines()

    def FormatMap(self, line: str) -> dict[str, int | str]:
        """Formatea la línea que declara nb_drones."""
        clave, valor = line.split(":", 1)
        return {clave.strip(): valor.strip()}

    def FormatHub(self, line: str, number: int) -> dict[str, int | str]:
        """Formatea una línea de hub, inicio o destino."""
        line = line.split(":", 1)[1].strip()
        name_coord, zone_color_max = line.split("[", 1)
        """
            s'ha acabat
        """

    def FormatConnection(self, line: str) -> dict[str, int | str]:
        """Formatea una línea de conexión."""
        ...

    def slicer(self, lines: list[str]) -> dict[str, object]:
        hubs: list[dict[str, int | str]] = []
        connections: list[dict[str, int | str]] = []
        mapa: dict[str, object] = {}

        for number, line in enumerate(lines, start=1):
            line = line.split("#", 1)[0].strip()

            if not line:
                continue

            if line.startswith("nb_drones:"):
                mapa.update(self.FormatMap(line, numero))

            elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                hub = self.FormatHub(line)
                hubs.append(hub)

                if line.startswith("start_hub:"):
                    mapa["start_hub"] = hub["name"]
                elif line.startswith("end_hub:"):
                    mapa["end_hub"] = hub["name"]

            elif line.startswith("connection:"):
                connection = self.FormatConnection(line)
                connections.append(connection)

            raise ValueError(
                f"Line {number}: Unknown prefix. Content: {line}"
                )

        mapa["hubs"] = hubs
        mapa["connections"] = connections

    return mapa
