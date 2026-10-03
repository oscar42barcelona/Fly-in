def FormatHub(self, line: str, number: int) -> dict[str, int | str]:
    """Formatea una línea de hub, inicio o destino."""
    line = line.split(":", 1)[1].strip()
    hub_dict: dict[str, int | str] = {}
    name_coord: str = line

    if '[' in line:
        name_coord, zone_color_max = line.split("[", 1)
        name_coord = name_coord.strip()
        zone_color_max = zone_color_max.strip()

        if not zone_color_max.endswith(']'):
            raise ValueError(
                f"Line {number}: Missing ']'. Content: {line}")

        zone_color_max = zone_color_max[:-2]
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

if __name__ == "__main__":
    print(FormatHub(
        None,
        "hub: roof1 3 4 [zone=restricted color=red max_drones=2]",
        1
    ))

