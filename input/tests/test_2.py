def FormatConnection(self, line: str, number: int) -> dict[str, str]:
    """Formatea una línea de conexión."""
    connections_dict: dict[str, int | str] = {}

    line = line.split(":", 1)[1].strip()

    connections: str = line

    if '[' in line:
        connections, link_capacity = line.split("[", 1)
        link_capacity = link_capacity.strip()

        if not link_capacity.endswith(']'):
            raise ValueError(
                f"Line {number}: Missing ']'. Content: {line}")

        link_capacity = link_capacity[:-1]

        if not link_capacity.__contains__("="):
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

def main() -> None:
    pruebas = [
        "connection: hub-roof1",
        "connection: hub-corridorA [max_link_capacity=2]",
        "connection: roof1-roof2 [max_link_capacity=1]",
        "connection: tunnelB-goal [max_link_capacity=3]",
        "connection: A-B [max_link_capacity=10]",
    ]

    for number, line in enumerate(pruebas, start=1):
        print(f"Prueba {number}: {line}")
        try:
            resultado = FormatConnection(None, line, number)
            print(resultado)
        except Exception as error:
            print(f"{type(error).__name__}: {error}")
        print()


if __name__ == "__main__":
    main()
