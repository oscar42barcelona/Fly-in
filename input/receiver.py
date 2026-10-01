from sys import argv

class receiver():
    def reader() ->  list[str]:
        """Read the configuration file.

    Returns:
        The lines contained in the configuration file.

    Raises:
        IndexError: If no configuration file argument is provided.
        FileNotFoundError: If the configuration file does not exist.
        PermissionError: If the file cannot be read due to permissions.
    """
        with open(argv[1], "r") as file:
            return file.readlines()

    def formatter(lines: list[str])

        """
            Para manyana como ya tenemos mas o menos una estructura de lo que queremos que reciba pydantic
            ver que es lo que tendremos que hacer, puede que debamos decidir bien como gestionar lo de conexiones, es que hay varias cosas que pensar, si e cuesta mucho te ayudas de la ia, despues hariamos un return para cada clase y que se haga la validacion en la de map al fninal"""  
