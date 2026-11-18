"""Pygame diagnostic viewer for Fly-in movement records.

This standalone debugging utility does not mutate the graph or drones.
Install: python -m pip install pygame
Run demo: python render_tester.py
Integration: render_tester.launch(graph, turn_movements, start_name='hub')
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
import math


@dataclass(frozen=True)
class Issue:
    turn: int
    message: str


@dataclass
class Snapshot:
    turn: int
    positions: dict[int, str]
    issues: list[Issue]


def _value(item: Any) -> str:
    return str(getattr(item, 'value', item)).lower().split('.')[-1]


def _is_start(node: Any) -> bool:
    return 'start' in _value(getattr(node, 'type', ''))


def _is_end(node: Any) -> bool:
    return 'end' in _value(getattr(node, 'type', ''))


def _zone(node: Any) -> str:
    return _value(getattr(node, 'zone', 'normal'))


def _edge_name(edge: Any) -> str:
    return f'{edge.node_a.name}-{edge.node_b.name}'


def _lookup_edge(label: str, edges: list[Any]) -> Any | None:
    for edge in edges:
        a, b = edge.node_a.name, edge.node_b.name
        if label in (f'{a}-{b}', f'{b}-{a}'):
            return edge
    return None


def _prepare(graph: Any, movements: dict[int, list[Any]],
             start_name: str | None) -> tuple[list[Snapshot], dict[str, Any]]:
    nodes = {node.name: node for node in graph.nodes}
    edges = list(graph.connections)
    starts = [n.name for n in graph.nodes if _is_start(n)]
    ends = {n.name for n in graph.nodes if _is_end(n)}
    issues: list[Issue] = []
    if not starts and start_name is None:
        raise ValueError('No start node detected; pass start_name=...')
    start = start_name if start_name is not None else starts[0]
    if start not in nodes:
        raise ValueError(f'Unknown start node: {start}')
    if len(starts) != 1:
        issues.append(Issue(0, f'Expected 1 start, found {len(starts)}'))
    if len(ends) != 1:
        issues.append(Issue(0, f'Expected 1 end, found {len(ends)}'))
    if len(nodes) != len(graph.nodes):
        issues.append(Issue(0, 'Duplicate node names'))
    known: set[int] = {int(r.drone_id) for records in movements.values() for r in records}
    positions: dict[int, str] = {drone_id: start for drone_id in known}
    expected_arrival: dict[int, tuple[str, int]] = {}
    snapshots = [Snapshot(0, positions.copy(), issues.copy())]
    max_turn = max(movements, default=0)
    for turn in range(1, max_turn + 1):
        turn_issues: list[Issue] = []
        seen: set[int] = set()
        changes: dict[int, str] = {}
        for record in movements.get(turn, []):
            drone_id = int(record.drone_id)
            state = _value(record.state)
            location = str(record.location)
            if drone_id in seen:
                turn_issues.append(Issue(turn, f'D{drone_id}: duplicate record'))
                continue
            seen.add(drone_id)
            previous = positions.get(drone_id, start)
            if previous in ends:
                turn_issues.append(Issue(turn, f'D{drone_id}: moved after delivery'))
            if state == 'transit':
                edge = _lookup_edge(location, edges)
                if edge is None:
                    turn_issues.append(Issue(turn, f'D{drone_id}: unknown connection {location}'))
                elif previous.startswith('edge:'):
                    turn_issues.append(Issue(turn, f'D{drone_id}: transit lasted more than one turn'))
                else:
                    a, b = edge.node_a.name, edge.node_b.name
                    if previous not in (a, b):
                        turn_issues.append(Issue(turn, f'D{drone_id}: not at an endpoint of {location}'))
                    destination = b if previous == a else a
                    if _zone(nodes[destination]) != 'restricted':
                        turn_issues.append(Issue(turn, f'D{drone_id}: transit not aimed at restricted zone'))
                    expected_arrival[drone_id] = (destination, turn + 1)
                    changes[drone_id] = 'edge:' + _edge_name(edge)
            elif state in ('movement', 'stay'):
                if location not in nodes:
                    turn_issues.append(Issue(turn, f'D{drone_id}: unknown node {location}'))
                    continue
                if state == 'stay' and location != previous:
                    turn_issues.append(Issue(turn, f'D{drone_id}: STAY changed position'))
                if state == 'movement':
                    if previous.startswith('edge:'):
                        expected = expected_arrival.get(drone_id)
                        if expected and (location, turn) != expected:
                            turn_issues.append(Issue(turn, f'D{drone_id}: wrong restricted arrival'))
                    elif previous == location:
                        turn_issues.append(Issue(turn, f'D{drone_id}: MOVEMENT to same node'))
                    elif not any({previous, location} == {e.node_a.name, e.node_b.name} for e in edges):
                        turn_issues.append(Issue(turn, f'D{drone_id}: {previous} -> {location} not connected'))
                    elif _zone(nodes[location]) == 'restricted':
                        turn_issues.append(Issue(turn, f'D{drone_id}: restricted arrival without transit'))
                if _zone(nodes[location]) == 'blocked':
                    turn_issues.append(Issue(turn, f'D{drone_id}: entered blocked zone {location}'))
                changes[drone_id] = location
            else:
                turn_issues.append(Issue(turn, f'D{drone_id}: invalid state {state}'))
        for drone_id, (_, arrival_turn) in list(expected_arrival.items()):
            if arrival_turn == turn:
                expected_destination = expected_arrival[drone_id][0]
                if changes.get(drone_id) != expected_destination:
                    turn_issues.append(Issue(turn, f'D{drone_id}: required arrival at {expected_destination} missing'))
                expected_arrival.pop(drone_id)
        positions.update(changes)
        occupants = Counter(pos for pos in positions.values() if not pos.startswith('edge:') and pos not in ends and pos != start)
        for name, count in occupants.items():
            capacity = int(getattr(nodes[name], 'capacity', 1))
            if count > capacity:
                turn_issues.append(Issue(turn, f'{name}: occupancy {count} > {capacity}'))
        transits = Counter(pos for pos in positions.values() if pos.startswith('edge:'))
        for label, count in transits.items():
            edge = _lookup_edge(label[5:], edges)
            if edge and count > int(getattr(edge, 'capacity', 1)):
                turn_issues.append(Issue(turn, f'{label[5:]}: transit occupancy {count} > {edge.capacity}'))
        snapshots.append(Snapshot(turn, positions.copy(), turn_issues))
        issues.extend(turn_issues)
    return snapshots, {'nodes': nodes, 'edges': edges, 'issues': issues, 'start': start}


def launch(graph: Any, turn_movements: dict[int, list[Any]],
           start_name: str | None = None) -> None:
    """Render the graph and inspect per-turn simulation anomalies."""
    try:
        import pygame
    except ImportError as error:
        raise RuntimeError('Install pygame: python -m pip install pygame') from error
    snapshots, data = _prepare(graph, turn_movements, start_name)
    pygame.init()
    screen = pygame.display.set_mode((1150, 740), pygame.RESIZABLE)
    pygame.display.set_caption('Fly-in | Render tester')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 17)
    small = pygame.font.SysFont('monospace', 14)
    current = 0
    playing = False
    elapsed = 0.0
    def text(surface: Any, msg: str, x: int, y: int, color: tuple[int, int, int] = (218, 226, 235), tiny: bool = False) -> None:
        surface.blit((small if tiny else font).render(msg, True, color), (x, y))
    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_RIGHT:
                    current = min(current + 1, len(snapshots) - 1)
                    playing = False
                elif event.key == pygame.K_LEFT:
                    current = max(current - 1, 0)
                    playing = False
                elif event.key == pygame.K_SPACE:
                    playing = not playing
                elif event.key == pygame.K_HOME:
                    current = 0
                    playing = False
        if playing:
            elapsed += dt
            if elapsed >= 0.65:
                elapsed = 0.0
                current = min(current + 1, len(snapshots) - 1)
                if current == len(snapshots) - 1:
                    playing = False
        width, height = screen.get_size()
        sidebar = 335
        graph_width = max(200, width - sidebar)
        screen.fill((16, 22, 34))
        pygame.draw.rect(screen, (27, 36, 51), (graph_width, 0, sidebar, height))
        nodes = list(data['nodes'].values())
        xs = [float(n.x) for n in nodes] or [0.0]
        ys = [float(n.y) for n in nodes] or [0.0]
        min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
        scale = min((graph_width - 120) / max(max_x - min_x, 1), (height - 170) / max(max_y - min_y, 1))
        def point(node: Any) -> tuple[int, int]:
            return (int(60 + (float(node.x) - min_x) * scale), int(90 + (max_y - float(node.y)) * scale))
        for edge in data['edges']:
            pygame.draw.line(screen, (86, 106, 132), point(edge.node_a), point(edge.node_b), 3)
            ax, ay = point(edge.node_a)
            bx, by = point(edge.node_b)
            text(screen, str(edge.capacity), (ax + bx) // 2, (ay + by) // 2, (175, 185, 202), True)
        for node in nodes:
            x, y = point(node)
            category = _zone(node)
            color = (117, 145, 182)
            if category == 'restricted':
                color = (235, 156, 74)
            elif category == 'blocked':
                color = (109, 109, 109)
            elif category == 'priority':
                color = (115, 195, 165)
            if _is_start(node):
                color = (71, 190, 111)
            elif _is_end(node):
                color = (240, 199, 86)
            pygame.draw.circle(screen, color, (x, y), 18)
            text(screen, node.name, x - 20, y - 37, tiny=True)
            text(screen, str(getattr(node, 'capacity', '?')), x - 5, y - 7, (12, 23, 31), True)
        snapshot = snapshots[current]
        groups: dict[str, list[int]] = {}
        for drone_id, location in snapshot.positions.items():
            groups.setdefault(location, []).append(drone_id)
        for location, drone_ids in groups.items():
            if location.startswith('edge:'):
                edge = _lookup_edge(location[5:], data['edges'])
                if edge is None:
                    continue
                ax, ay = point(edge.node_a)
                bx, by = point(edge.node_b)
                x, y = (ax + bx) // 2, (ay + by) // 2
            else:
                node = data['nodes'].get(location)
                if node is None:
                    continue
                x, y = point(node)
            for offset, drone_id in enumerate(sorted(drone_ids)):
                col = offset % 4
                row = offset // 4
                dx = -19 + col * 13
                dy = 19 + row * 15
                pygame.draw.circle(screen, (73, 183, 247), (x + dx, y + dy), 7)
                text(screen, str(drone_id), x + dx - 4, y + dy - 5, (10, 20, 30), True)
        text(screen, f'TURN {snapshot.turn} / {snapshots[-1].turn}', 16, 18)
        text(screen, 'LEFT/RIGHT: step    SPACE: play/pause    HOME: reset    ESC: quit', 16, height - 28, tiny=True)
        px = graph_width + 14
        text(screen, 'DIAGNOSTICS', px, 20)
        text(screen, f'Nodes: {len(nodes)}   Links: {len(data["edges"])}', px, 54, tiny=True)
        text(screen, f'Drones: {len(snapshot.positions)}', px, 75, tiny=True)
        all_issues = data['issues']
        text(screen, f'Total issues: {len(all_issues)}', px, 106, (243, 126, 126) if all_issues else (131, 209, 161))
        text(screen, f'Issues this turn: {len(snapshot.issues)}', px, 137)
        y = 170
        for issue in snapshot.issues[:12]:
            words = issue.message.split()
            lines = ['']
            for word in words:
                if len(lines[-1]) + len(word) > 35:
                    lines.append('')
                lines[-1] += word + ' '
            for line in lines:
                text(screen, line, px, y, (251, 151, 151), True)
                y += 19
        if not snapshot.issues:
            text(screen, 'No detected errors this turn', px, y, (131, 209, 161), True)
        pygame.display.flip()
    pygame.quit()


def _demo() -> tuple[Any, dict[int, list[Any]]]:
    """Demonstration with deliberately invalid moves to test diagnostics."""
    def node(name: str, x: int, y: int, kind: str, zone: str = 'normal', capacity: int = 1) -> Any:
        return SimpleNamespace(name=name, x=x, y=y, type=kind, zone=zone, capacity=capacity)
    start = node('start', 0, 2, 'start')
    a = node('a', 2, 4, 'hub')
    b = node('b', 2, 0, 'hub', 'restricted')
    c = node('c', 5, 4, 'hub')
    end = node('end', 7, 2, 'end')
    edges = [SimpleNamespace(node_a=u, node_b=v, capacity=1) for u, v in ((start, a), (start, b), (a, c), (c, end), (b, end))]
    def rec(i: int, state: str, location: str) -> Any:
        return SimpleNamespace(drone_id=i, state=state, location=location)
    moves = {
        1: [rec(1, 'movement', 'a'), rec(2, 'transit', 'start-b')],
        2: [rec(1, 'movement', 'c'), rec(2, 'movement', 'b')],
        3: [rec(1, 'movement', 'end'), rec(2, 'movement', 'end')],
        4: [rec(1, 'movement', 'a')],  # deliberate issue: already delivered
    }
    return SimpleNamespace(nodes=[start, a, b, c, end], connections=edges), moves


if __name__ == '__main__':
    example_graph, example_movements = _demo()
    launch(example_graph, example_movements)
