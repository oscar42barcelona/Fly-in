def plan(drones: list[Drone],
        routes: dict[int, tuple[int, tuple[Node, ...]]]
        ) -> dict[int, list[MovementRecord]]:

        movement_record: list[MovementRecord] = []

        while all nodes are .deivered:
            for drone in drones:

                occupied_nodes: list[Node] = []

                for _, (route_cost, route) in routes.items():

                    #De esta manera identificamos el siguiente nodo
                    index = pos_next_node(drone.current_node, route)
                    next_node = route[index]

                    if drone.current_route == 0: #primera ruta:

                        if next_node.available_node():

                            #avanzamos el drone.
                            drone.current_node.exit_drone(drone)
                            drone.move_to_node(next_node)
                            next_node.enter_drone(drone)

                            #registramos el movement_record
                            #movement = "movement_" + "" + Como cuento los turnos?
                            movement_record.append(MovementRecord( #lo estoy metiendo sin instanciar
                                drone.id,
                                drone.state,
                                current_node))
                            break
                    else:
                            if next_node.available_node():

                            previous_path_cost = path_cost("""node""", route)

                            current_path_cost = path_cost(drone.current_node, route)

                            waiting_cost = len(occupied_nodes[0].queueing_drones)

                            previous_total_cost = previous_path_cost + waiting_cost

                            #Para escoger la ruta

                            if previous_total_cost > current_path_cost:
                                #avanzamos el drone.
                                drone.current_node.exit_drone(drone)
                                drone.move_to_node(next_node)
                                next_node.enter_drone(drone)

                                #registramos el movement_record
                                #movement = "movement_" + "" + Como cuento los turnos?
                                movement_record.append(MovementRecord( #lo estoy metiendo sin instanciar
                                    drone.id,
                                    drone.state,
                                    current_node))
                                break

                        #Si hemos visitado todas las rutas y en ninguna tiene sentido avanzar                           
                        drone.move_to_node(next_node) #si pero tendria que ser el nodo que mas me rentaria esperar
                        next_node.enter_drone(drone)

                        #registramos el movement_record
                        #movement = "movement_" + "" + Como cuento los turnos?
                        movement_record.append(MovementRecord(
                            drone.id,
                            drone.state,
                            current_node))




















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

