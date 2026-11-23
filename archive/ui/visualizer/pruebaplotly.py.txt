
from plotly.graph_objects import Figure, Scatter, Frame

fig = Figure()

# Estado inicial
fig.add_trace(
    Scatter(
        x=[0],
        y=[0],
        mode="markers",
        marker=dict(size=20, color="orange")
    )
)

# Estados posteriores
fig.frames = [
    Frame(
        data=[Scatter(x=[1], y=[1])],
        traces=[0],
        name="1"
    ),
    Frame(
        data=[Scatter(x=[2], y=[1])],
        traces=[0],
        name="2"
    ),
    Frame(
        data=[Scatter(x=[3], y=[2])],
        traces=[0],
        name="3"
    )
]

# Botón para reproducir la secuencia
fig.update_layout(
    xaxis=dict(range=[-1, 4]),
    yaxis=dict(range=[-1, 3], scaleanchor="x"),
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(
                    label="Reproducir",
                    method="animate",
                    args=[None]
                )
            ]
        )
    ]
)

fig.write_html("animacion_prueba.html")
