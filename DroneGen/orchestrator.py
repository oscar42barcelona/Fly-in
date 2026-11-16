from .base import flychestrator
from Graph.Map import Node, Connection
from Graph.Drone import Drone

class orchestrator(flychestrator):

    def plan(drones: list[Drone],
        routes: list[tuple[int, tuple[Node, ...]]]
        ) -> dict[int, list[MovementRecord]]:
        #muevo el primer drone al primer nodo
        drone_1 = drones[0]

        mapa_1 = routes[1][1]

        nodo_1 = mapa_1[1]

        drone_1.move_to_node(nodo_1)

        nodo_1.enter_drone(drone=drone_1)

        #creo diccionario donde registraremos los movimientos de cada nodo por cada turno
        turn_movement_record = {}
        
        #Instancio la clase para poder registrar el primer movimiento
        primer_movimiento = MovementRecord(
            drone_id=drone_1.id,
            state=drone_1.state,
            location=drone_1.current_node)

        #y ahora lo guardamos en una lista
        movement_record = []

        movement_record.append(primer_movimiento)

        #ahora vamos con el segundo drone. 

        #muevo el segundo drone al primer nodo
        drone_2 = drones[1]

        mapa_1 = routes[1][1]

        nodo_1 = mapa_1[1]

        if drone_2.available_drone(nodo_1) is False:
            mapa_2 = routes[1][2]
            nodo_1 = mapa_2[1]
            if drone_2.available_drone(nodo_1) is False:
                mapa_3 = routes[1][3]
                nodo_1 = mapa_3[1]
                if drone_2.available_drone(nodo_1) is False:
                    ...
                else:
                    if cost_till_end < coste de mapa + #el conteo de la cola para entrar en el nodo siguiente count(queueing_drones):
                        drone_2.move_to_node(nodo_1)

                        nodo_1.enter_drone(drone=drone_2)
                    else:
                        drone_2.move_to_node(self.current_node)
                        nodo_1.queueing_drones(nodo_1) 
