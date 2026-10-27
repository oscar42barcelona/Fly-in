from .Map import Node, Connection, Drone, Graph
from input.validator import Map_, Hub
from input.validator import Connection as VConnection
from .Drone import Drone

class Factory():
    drone_id: int = 0

    def create_drone(self, start_node: Node) -> Drone:
        self.drone_id += 1
        
        return Drone(self.drone_id, start_node)

    def create_drones(self,nb_drones, start_node) -> list[Drone]:
        drone_list: list[drone] = []
        
        for _ in range(nb_drones):

            drone = self.create_drone(start_node)
            drone_list.append(drone)
    
        return drone_list

    def create_node(self, hub: Hub) -> Node:
        """crear instancias Node a partir de los datos 
        validados de cada hub."""
        return Node(name=hub.NAME, x=hub.X,
                    y=hub.Y, zone_type=hub.TYPE, 
                    color=hub.COLOR,
                    max_drones=hub.MAX_DRONES)

    def create_nodes(self, node_list: list[Hub]) -> list[Node]:
        """crear una lista de instancias Node a partir de los datos 
        validados de cada hub."""
        list_nodes: list[Node] = []

        for hub in node_list:
            list_nodes.append(self.create_node(hub))

        return list_nodes

    def create_connection(self, 
                        connection: Connection,
                        node_list: list[Node]) -> Connection:
        
        for node in node_list:
            if node.name == connection.HUB1:
                node_A = node
            elif node.name == connection.HUB2:
                node_B = node
        
        return Connection(node_a=node_A,
                 node_b=node_B,
                 max_link_capacity=connection.LINK_CAPACITY)

    def create_connections(self, connect_list: Connection, 
                            node_list: list[Node]
                            ) -> list[Connection]:
        connection_list: list[Connection] = []        

        for connection in connect_list:
            con = self.create_connection(connection, node_list)
            connection_list.append(con)

        return connection_list
                    
    def create_graph(self, hubs: Hub, 
                    connections: list[Connection]) -> Graph:
        """organizar la creación de todos los nodos, 
            luego las conexiones y 
            devolver Graph completo. """
        node_list = self.create_nodes(hubs)
        connection_list = self.create_connections(connect_list=connections,
                                                node_list=node_list)

        return Graph(node_list, connection_list)
