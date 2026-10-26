#import Drone, la libreria de range, import Node, Connection, Graph, Node

class Factory()
    self.drone_id: int = 0

    def create_drone(self, start_node: Node) -> Drone:
        self.drone_id += 1
        
        return Drone(self.drone_id, start_node)

    def create_drones(self,nb_drones, start_node) -> list[Drone]:
        drone_list: list[drone] = []
        
        for _ in range(nb_drones):

            drone = self.create_drone(start_node: Node)
            drone_list.append(drone)
    
        return drone_list

    def create_node(self, hub: Hub) -> Node:
        """crear instancias Node a partir de los datos 
        validados de cada hub."""
        return Node(name=hub.NAME, x=hub.X,
                    y=hub.y, zone_type=hub.type, 
                    color=hub.COLOR,
                    max_drones=hub.MAX)

    def create_nodes(self, node_list: HUBS) -> list[Node]:
        """crear una lista de instancias Node a partir de los datos 
        validados de cada hub."""
        node_list: list[Node] = []

        for hub in node_list:
            node_list.append(self.create_node(hub))

    def create_connection(self, 
                        connection: Connection,
                        node_list: list[Node]) -> Connection:
        
        for node in node_list:
            if node.name == connection.HUB1:
                node_A = node
            elif node.name == connection.HUB2:
                node_B = node
        
        return Connection(node_a=Node_A,
                 node_b=Node_B,
                 max_link_capacity=connection.LINK_CAPACITY)

    def create_connections(self, connect_list: Connections, 
                            node_list: list[Node]
                            ) -> list[connection]:
        connection_list: list[Connection] = []        

        for connection i connect_list:
            con = self.create_connection(connection, node_list)
            connection_list.append(con)

        return connection_list
                    
    def create_graph(self, hubs: Hubs, 
                    connections: Connections) -> Graph:
        """organizar la creación de todos los nodos, 
            luego las conexiones y 
            devolver Graph completo. """
        node_list = self.create_nodes(hubs)
        connection_list = self.create_connections(connect_list=connections,
                                                node_list=node_list)

        return Graph(node_list, connection_list)
