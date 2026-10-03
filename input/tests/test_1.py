def typer( hub_type: str) -> str:
    if hub_type.startswith("start_hub"):
        return "entry"
    elif hub_type.startswith("end_hub"):
        return "exit"
    else:
        return "intermediate"

def FormatHub(self, line: str, number: int) -> dict[str, int | str]:
    """Formatea una línea de hub, inicio o destino."""
    hub_dict: dict[str, int | str] = {}
    

    hub_type, line = line.split(":", 1)
    hub_type = hub_type.strip()
    hub_dict["type"] = typer(hub_type)

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

def main() -> None:
    pruebas = [
        "hub: roof1 3 4",
        "start_hub: entrada 0 0 [color=green]",
        "end_hub: salida 10 10 [color=yellow]",
        "hub: roof2 6 2 [zone=normal color=blue]",
        "hub: corridorA 4 3 [zone=priority color=green max_drones=2]",
        "hub: tunnelB 7 4 [max_drones=3 color=red zone=restricted]",
        "hub: obstacleX 5 5 [zone=blocked color=gray]",
    ]

    for number, line in enumerate(pruebas, start=1):
        print(f"Prueba {number}: {line}")
        resultado = FormatHub(None, line, number)
        print(resultado)


if __name__ == "__main__":
    main()
