from abc import ABC


class Node()
	"""Aquí va todo lo relacionado con los nodos:
		- capacidad
		- peso
		- origen
		- entrada
		- salida
	"""

class Connections(ABC, Node)
	"""
		Aquí va todo sobre las conexiones entre drones
	"""
	@abstractmethod
	def nodeconnector(self, node_a: Node, node_b) -> dict[tuple[node | node]]
		...

	@abstractmethod
	def listofconnections(self, edge: tuple[node | node]) -> list[tuple[node | node]]:
		...


class Map(Connections, Node):
	"""Para unirlo todo o crear automaticamente un mapa
	como en el modulo 7 de python aquí podria ser donde se isntancien las cosas como si fueranfabricas 
	o puede que esto sea lo que le pasemos a la clase de algoritmos de python"""
