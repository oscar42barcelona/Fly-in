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

