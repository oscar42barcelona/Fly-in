from .base import MovementRecord, flygorithm

class Algorithm(flygorithm):
    def solve(drones: list[Drone], graph: Graph) -> dict[int, list[MovementRecord]]:
        ...