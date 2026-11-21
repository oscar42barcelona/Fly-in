"""Busca rutas por coste y favorece zonas PRIORITY en caso de empate."""

# CAMBIO 1: anotaciones de tipos evaluadas de forma diferida.
from __future__ import annotations

from heapq import heappop, heappush
from itertools import count

from input.validator import HubType
from .base import flygorithm
from ..Graph.Drone import Drone
from ..Graph.Map import Graph, Node


class Algorithm(flygorithm):
    """Dijkstra para la primera ruta y Yen para rutas alternativas."""

    def solve(
        self,
        drone: Drone,
        graph: Graph,
        k: int = 3,
    ) -> dict[int, tuple[int, tuple[Node, ...]]]:
        # CAMBIO 2: validar k antes de buscar y mantener el formato de solve().
        if k <= 0:
            return {}

        first_route = self.djikstra_route_finding(drone, graph)
        routes = self.YensAlgorithm(drone, graph, first_route, k)
        return {index: value for index, value in enumerate(routes)}

    # CAMBIO 3: localizar la salida por HubType.EXIT, no por el nombre "goal".
    @staticmethod
    def _goal(graph: Graph) -> Node:
        for node in graph.nodes:
            if node.type == HubType.EXIT:
                return node
        raise ValueError("No exit node found in graph")

    # CAMBIO 4: comparar rutas completas por (coste, penalizacion PRIORITY).
    # Si tienen el mismo coste, gana la que acumula menor penalizacion.
    @staticmethod
    def _rank(route: tuple[Node, ...]) -> tuple[int, int]:
        """Coste de turnos primero; penalizacion de prioridad despues."""
        cost = 0
        priority_penalty = 0
        for node in route[1:]:
            if node.zone.cost is None:
                raise ValueError("A route cannot cross a blocked node")
            cost += node.zone.cost
            priority_penalty += node.zone.priority
        return cost, priority_penalty

    # CAMBIO 5: Dijkstra reutilizable para la ruta inicial y los desvios de Yen.
    # Sustituye la busqueda anterior que gestionaba el heap manualmente.
    def _shortest_path(
        self,
        start: Node,
        goal: Node,
        graph: Graph,
        blocked_nodes: set[Node] | None = None,
        blocked_edges: set[frozenset[Node]] | None = None,
    ) -> tuple[Node, ...] | None:
        """Dijkstra con desempate de prioridad sobre la ruta completa."""
        excluded_nodes = blocked_nodes if blocked_nodes is not None else set()
        excluded_edges = blocked_edges if blocked_edges is not None else set()
        serial = count()
        heap: list[tuple[int, int, int, Node, tuple[Node, ...]]] = [
            (0, 0, next(serial), start, (start,))
        ]
        # Cada nodo guarda su mejor par (coste, prioridad), no solo el coste.
        best: dict[Node, tuple[int, int]] = {start: (0, 0)}

        while heap:
            cost, penalty, _, current, path = heappop(heap)
            # Descartamos entradas antiguas del heap sin borrarlas a mano.
            if (cost, penalty) != best[current]:
                continue
            if current is goal:
                return path

            for neighbor in graph.get_connections(current):
                if neighbor in excluded_nodes or neighbor in path:
                    continue
                # El grafo es bidireccional: bloqueamos ambos sentidos.
                if frozenset((current, neighbor)) in excluded_edges:
                    continue
                step_cost = neighbor.zone.cost
                if step_cost is None:
                    continue
                if step_cost < 0:
                    raise ValueError("Dijkstra requires nonnegative costs")

                # Desempate por prioridad acumulada en todo el recorrido.
                # En validator.py PRIORITY=0 y NORMAL=1.
                score = (
                    cost + step_cost,
                    penalty + neighbor.zone.priority,
                )
                if score >= best.get(neighbor, (float("inf"), float("inf"))):
                    continue
                best[neighbor] = score
                heappush(
                    heap,
                    (
                        score[0],
                        score[1],
                        next(serial),  # Evita comparar objetos Node en empates.
                        neighbor,
                        path + (neighbor,),
                    ),
                )

        return None

    # CAMBIO 6: interfaz publica conservada; delega en _shortest_path().
    def djikstra_route_finding(
        self,
        drone: Drone,
        graph: Graph,
    ) -> tuple[Node, ...]:
        """Devuelve la mejor ruta; mantiene el nombre usado por el proyecto."""
        start = drone.current_node
        if start is None:
            raise ValueError("Drone has no current node")
        route = self._shortest_path(start, self._goal(graph), graph)
        if route is None:
            raise ValueError("No route exists from start to exit")
        return route

    # CAMBIO 7: Yen busca desviaciones con el mismo Dijkstra y desempate.
    # Reemplaza el bucle de busqueda dentro de cada desviacion original.
    def YensAlgorithm(
        self,
        drone: Drone,
        graph: Graph,
        route: tuple[Node, ...],
        k: int = 3,
    ) -> list[tuple[int, tuple[Node, ...]]]:
        """Genera hasta k rutas simples, ordenadas por coste y prioridad."""
        if k <= 0 or not route:
            return []

        goal = self._goal(graph)
        if route[0] is not drone.current_node:
            raise ValueError("Route does not start at the drone's node")
        if route[-1] is not goal:
            raise ValueError("Route does not reach the exit")

        accepted: list[tuple[Node, ...]] = [route]
        # Evita que la misma ruta se incorpore varias veces.
        known: set[tuple[Node, ...]] = {route}
        serial = count()
        candidates: list[tuple[int, int, int, tuple[Node, ...]]] = []

        while len(accepted) < k:
            previous = accepted[-1]
            for index in range(len(previous) - 1):
                prefix = previous[:index + 1]
                # No podemos volver a visitar nodos anteriores del prefijo.
                forbidden_nodes = set(prefix[:-1])
                # Excluir la arista que generaria una ruta ya aceptada.
                forbidden_edges = {
                    frozenset((existing[index], existing[index + 1]))
                    for existing in accepted
                    if len(existing) > index + 1
                    and existing[:index + 1] == prefix
                }
                suffix = self._shortest_path(
                    prefix[-1], goal, graph, forbidden_nodes, forbidden_edges
                )
                if suffix is None:
                    continue
                candidate = prefix[:-1] + suffix
                if candidate in known:
                    continue
                known.add(candidate)
                # Antes Yen ordenaba solo por coste; ahora desempata por prioridad.
                cost, penalty = self._rank(candidate)
                heappush(
                    candidates,
                    (cost, penalty, next(serial), candidate),
                )

            if not candidates:
                break
            _, _, _, selected = heappop(candidates)
            accepted.append(selected)

        return [(self._rank(path)[0], path) for path in accepted]

    # CAMBIO 8: se conserva cost_route() por compatibilidad, pero se
    # simplifica el calculo y se comprueban rutas vacias o bloqueadas.
    def cost_route(
        self,
        route_node: Node,
        route: tuple[Node, ...] | list[Node],
    ) -> int:
        """Coste acumulado desde el inicio hasta route_node."""
        if not route:
            raise ValueError("Empty route")
        cost = 0
        if route[0] is route_node:
            return cost
        for node in route[1:]:
            if node.zone.cost is None:
                raise ValueError(f"Node {node.name} has no valid cost")
            cost += node.zone.cost
            if node is route_node:
                return cost
        raise ValueError("Node is not part of the route")
