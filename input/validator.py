"""Pydantic models for Fly-in map hubs, zones and connections."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError


class HubType(str, Enum):
    """Whether a node is the entry, a waypoint, or the exit."""

    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    EXIT = "exit"


class Zone(str, Enum):
    """Traffic class including its traversal cost and route preference."""

    cost: int | None
    priority: int

    NORMAL = ("normal", 1, 1)
    BLOCKED = ("blocked", None, 3)
    RESTRICTED = ("restricted", 2, 2)
    PRIORITY = ("priority", 1, 0)

    def __new__(
        cls, text: str, cost: int | None, priority: int
    ) -> Zone:
        """Create an enum value carrying the zone's path-finding weights."""
        zone = str.__new__(cls, text)
        zone._value_ = text
        zone.cost = cost
        zone.priority = priority
        return zone


class Hub(BaseModel):
    """One validated map node."""

    NAME: str = Field(alias="name")
    X: int = Field(alias="x")
    Y: int = Field(alias="y")
    TYPE: HubType = Field(alias="type", default=HubType.INTERMEDIATE)
    ZONE: Zone = Field(alias="zone", default=Zone.NORMAL)
    COLOR: str | None = Field(alias="color", default="grey")
    MAX_DRONES: int = Field(alias="max_drones", ge=1, default=1)

    @model_validator(mode="before")
    @classmethod
    def ignore_terminal_capacity(
        cls, values: dict[str, object]
    ) -> dict[str, object]:
        """Entry and exit have unlimited capacity by the subject rules."""
        if values.get("type") in (HubType.ENTRY, HubType.EXIT):
            return {**values, "max_drones": 1}
        return values

    @field_validator("NAME")
    @classmethod
    def valid_names(cls, name: str) -> str:
        """Reject separators that conflict with the map text format."""
        if " " in name or "-" in name:
            raise ValueError("Zone names cannot contain dashes or spaces")
        return name

    @field_validator("COLOR")
    @classmethod
    def OneWordColor(cls, color: str | None) -> str | None:
        """Accept one-word color names and optional custom colors."""
        if color is not None and len(color.split()) > 1:
            raise ValueError("Color must be a single word")
        return color


class Connection(BaseModel):
    """Validated undirected connection between two map hubs."""

    HUB1: str = Field(alias="hub1")
    HUB2: str = Field(alias="hub2")
    LINK_CAPACITY: int | None = Field(
        alias="link_capacity", ge=1, default=1
    )

    @model_validator(mode="after")
    def UniqueHub(self) -> Connection:
        """Forbid a connection from a node to itself."""
        if self.HUB1 == self.HUB2:
            raise ValueError("A Hub cannot connect to itself :(")
        return self


class Map_(BaseModel):
    """Complete validated map using existing uppercase property names."""

    NB_DRONES: int = Field(alias="nb_drones", ge=1)
    HUBS: list[Hub] = Field(alias="Hubs", min_length=2)
    START_HUB: str = Field(alias="start_hub")
    END_HUB: str = Field(alias="end_hub")
    CONNECTIONS: list[Connection] = Field(alias="Connections")

    @field_validator("HUBS")
    @classmethod
    def one_start_end(cls, hubs: list[Hub]) -> list[Hub]:
        """Prevent more than one entry or exit in a map."""
        for hub_type in (HubType.ENTRY, HubType.EXIT):
            amount = 0
            for index, node in enumerate(hubs):
                if node.TYPE == hub_type:
                    amount += 1
                if amount == 2:
                    raise PydanticCustomError(
                        "custom_validation_error",
                        f"There must be exactly one {hub_type.value} hub",
                        {"Hubs": index},
                    )
        return hubs

    @field_validator("HUBS")
    @classmethod
    def UniqueHubNames(cls, hubs: list[Hub]) -> list[Hub]:
        """Enforce unique names for every map hub."""
        seen: set[str] = set()
        for index, node in enumerate(hubs):
            if node.NAME in seen:
                raise PydanticCustomError(
                    "custom_validation_error",
                    "Hubs name must be unique",
                    {"Hubs": index},
                )
            seen.add(node.NAME)
        return hubs

    @field_validator("CONNECTIONS")
    @classmethod
    def UniqueConnections(
        cls, connections: list[Connection]
    ) -> list[Connection]:
        """Forbid duplicate undirected links."""
        seen: set[frozenset[str]] = set()
        for index, connection in enumerate(connections):
            pair = frozenset((connection.HUB1, connection.HUB2))
            if pair in seen:
                raise PydanticCustomError(
                    "custom_validation_error",
                    "Pair or Hub Connections must be unique",
                    {"Connections": index},
                )
            seen.add(pair)
        return connections

    @model_validator(mode="after")
    def defined_connections(self) -> Map_:
        """All link endpoints must be declared map hubs."""
        hub_names = {hub.NAME for hub in self.HUBS}
        for index, connection in enumerate(self.CONNECTIONS):
            if (
                connection.HUB1 not in hub_names
                or connection.HUB2 not in hub_names
            ):
                raise PydanticCustomError(
                    "custom_validation_error",
                    "Connections and hubs must coincide",
                    {"Connections": index},
                )
        return self
