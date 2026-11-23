
from input.receiver import receiver
from DroneGen.Graph.MapFactory import Factory
from ui.visualizer.plotly_test import plotlyzer


def main():
    mapa = receiver("maps/medium/03_priority_puzzle.txt").Process()

    grafo = Factory().create_graph(
        hubs=mapa.HUBS,
        connections=mapa.CONNECTIONS,
    )

    fig = plotlyzer(grafo).create_figure()
    fig.write_html("flyin_preview.html", auto_open=True)


if __name__ == "__main__":
    main()

