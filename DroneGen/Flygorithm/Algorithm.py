from input.validator import Zone
from .base import MovementRecord, flygorithm
from ..Graph.Drone import Drone
from ..Graph.Map import Node, Connection, Graph
from heapq import heappush, heappop, heapify
from input.validator import HubType
from itertools import count


class Algorithm(flygorithm):
    def solve(self, drone: Drone, graph: Graph) -> dict[int, list[MovementRecord]]:
        ...

    

def YensAlgorithm(
    self,
    drone: Drone,
    graph: Graph,
    route: tuple[Node, ...],
    k: int = 3
) -> list[tuple[int, tuple[Node, ...]]]:

    if k <= 0 or not route:
        return []

    if route[0].name != drone.current_node.name:
        raise ValueError("La ruta no comienza en el nodo del dron")

    if route[-1].name != "goal":
        raise ValueError("La ruta no termina en goal")

    # A: caminos aceptados.
    goal_routes = [(self.cost_route(route[-1], route), route)]

    # B: caminos candidatos pendientes.
    candidate_heap = []
    contador = count()

    # Evitar candidatos duplicados.
    known_routes = {
        tuple(node.name for node in route)
    }

    while len(goal_routes) < k:

        # Última ruta aceptada.
        route = goal_routes[-1][1]

        # Recorrer todos sus puntos de desviación,
        # excepto el destino.
        for index, route_node in enumerate(route[:-1]):

            heap = []

            # Prefijo fijo hasta el spur node.
            root_path = route[:index + 1]

            root_cost = self.cost_route(route_node, root_path)

            # Estado inicial de esta búsqueda.
            next_node = route_node
            tuple_list = (route_node,)
            previous_cost = 0

            # Nodos anteriores al spur node.
            blocked_nodes = {
                node.name for node in root_path[:-1]
            }

            # Aristas excluidas por prefijos compartidos.
            blocked_edges = set()

            for _, accepted_route in goal_routes:

                if accepted_route[:index + 1] == root_path:

                    if len(accepted_route) > index + 1:
                        blocked_edges.add((
                            accepted_route[index].name,
                            accepted_route[index + 1].name
                        ))

            # Mejor coste conocido desde el spur node.
            best_cost = {route_node.name: 0}

            while next_node.name != "goal":

                connection_list = [
                    node
                    for node in graph.get_connections(next_node)
                    if node.name not in blocked_nodes
                    and node.name not in {
                        visited.name for visited in tuple_list
                    }
                    and (next_node.name, node.name)
                        not in blocked_edges
                ]

                for node in connection_list:

                    if node.zone.cost is None:
                        continue

                    if node.zone.cost < 0:
                        raise ValueError(
                            "Dijkstra requiere costes no negativos"
                        )

                    cumulative_cost = (
                        previous_cost + node.zone.cost
                    )

                    # Relajación de Dijkstra.
                    if cumulative_cost >= best_cost.get(
                        node.name, float("inf")
                    ):
                        continue

                    best_cost[node.name] = cumulative_cost

                    heappush(
                        heap,
                        (
                            cumulative_cost,
                            node.zone.priority,
                            next(contador),
                            node,
                            tuple_list
                        )
                    )

                # La desviación no tiene continuación.
                if not heap:
                    break

                previous_cost, _, _, next_node, previous_tuple = (
                    heappop(heap)
                )

                tuple_list = previous_tuple + (next_node,)

                # Ignorar entradas antiguas del heap.
                while (
                    previous_cost > best_cost.get(
                        next_node.name, float("inf")
                    )
                ):
                    if not heap:
                        next_node = None
                        break

                    previous_cost, _, _, next_node, previous_tuple = (
                        heappop(heap)
                    )
                    tuple_list = previous_tuple + (next_node,)

                if next_node is None:
                    break

            # No se ha encontrado una desviación válida.
            if next_node is None or next_node.name != "goal":
                continue

            # Unir prefijo y desviación sin repetir spur node.
            complete_route = root_path[:-1] + tuple_list

            total_cost = root_cost + previous_cost

            route_key = tuple(
                node.name for node in complete_route
            )

            if route_key in known_routes:
                continue

            known_routes.add(route_key)

            heappush(
                candidate_heap,
                (
                    total_cost,
                    next(contador),
                    complete_route
                )
            )

        # No quedan más caminos candidatos.
        if not candidate_heap:
            break

        # Seleccionar el candidato más barato.
        cost, _, selected_route = heappop(candidate_heap)

        goal_routes.append((cost, selected_route))

    return goal_routes


def cost_route(
    self,
    route_node: Node,
    route: tuple[Node, ...] | list[Node]
) -> int:

    cost = 0

    for node in route[1:]:

        if node.zone.cost is None:
            raise ValueError(
                f"El nodo {node.name} no tiene coste"
            )

        cost += node.zone.cost

        if node.name == route_node.name:
            return cost

    if route[0].name == route_node.name:
        return 0

    raise ValueError("El nodo no pertenece a la ruta")

"""
    def YensAlgorithm(self, drone: Drone,
            graph: Graph, route: tuple[Node]) -> list[int, tuple[Node]]:

        route = list(route)
        goal_routes = []
        tuple_list = (route.pop(),) #quito el start hub

        for index, route_node in enumerate(route):

            if route_node.name == "goal": 
                break

            heap = []
            next_node = route_node
            flag = True
            previous_cost = self.cost_route(route_node, route)

            while next_node.name != "goal":

                connection_list = [node for node in graph.get_connections(next_node) if node not in tuple_list]

                if flag:
                    connection_list = connection_list.remove(route[index + 1])
                    flag = False

                for node in connection_list:

                    if node.zone.cost is not None:

                        cumulative_cost = node.zone.cost + previous_cost

                        flag, index = self.comprob_menor_coste(heap, node, cumulative_cost)

                        if flag:
                            if not index:
                                continue
                            heap.pop(index)

                            heapify(heap)

                        heappush(heap, (cumulative_cost, node.zone.priority, node.name, node, tuple_list))

                previous_cost, _, _, next_node, previous_tuple = heappop(heap)

                tuple_list = (previous_tuple + (next_node,))
            
                if next_node.name == "goal":
                    goal_routes.append((previous_cost, tuple_list))

        return goal_routes
        
        
    def cost_route(self, route_node: Node, route: list[Node]) -> int:
    
        cost = 0

        for index, node in enumerate(route):

            if node.name == route_node.name:
                break

            cost = node.zone.cost + cost

        return cost
   """         
                
    def original_djikstra_route_finding(self, drone: Drone,
            graph: Graph) -> tuple[Node]:
        """
        Contemplar el caso en que no exista ningún camino entre origen y destino.
        """
        heap = []

        cumulative_cost: int = 0

        next_node = drone.current_node

        tuple_list = (next_node,)

        while next_node.name != "goal":

            connection_list = [node for node in graph.get_connections(next_node) if node not in tuple_list]

            for node in connection_list:

                if node.zone.cost is not None:

                    if next_node.type == "entry":
                        cumulative_cost = node.zone.cost
                    else:
                        cumulative_cost = node.zone.cost + previous_cost

                    flag, index = self.comprob_menor_coste(heap, node, cumulative_cost)

                    if flag:
                        if not index:
                            continue
                        heap.pop(index)

                        heapify(heap)

                    heappush(heap, (cumulative_cost, node.zone.priority, node.name, node, tuple_list))

            previous_cost, _, _, next_node, previous_tuple = heappop(heap)

            tuple_list = (previous_tuple + (next_node,))


        return tuple_list


    def comprob_menor_coste(self, heap, node, cumulative_cost) -> tuple[bool, int | None]:

        if not heap:
            return (False, 0)
        for index, tupla in enumerate(heap):
            if node == tupla[3]:

                if tupla[0] < cumulative_cost:
                    return (True, None)

                else:
                    return (True, index)

        return (False, 0)


    def uniform_cost_path_enumeration(self, drone: Drone, graph: Graph):

        heap = []
        contador = count()
        goal_routes = []

        next_node = drone.current_node
        tuple_list = (next_node,)

        heappush(heap, (
            0,
            next_node.zone.priority,
            next(contador),
            next_node,
            tuple_list
        ))

        while heap:

            previous_cost, _, _, next_node, tuple_list = heappop(heap)

            if next_node.name == "goal":
                goal_routes.append((previous_cost, tuple_list))
                continue

            connection_list = [
                node
                for node in graph.get_connections(next_node)
                if node not in tuple_list
                ]

            for node in connection_list:

                if node.zone.cost is not None:

                    cumulative_cost = previous_cost + node.zone.cost

                    heappush(heap, (
                        cumulative_cost,
                        node.zone.priority,
                        next(contador),
                        node,
                        tuple_list + (node,)
                    ))

        return goal_routes
