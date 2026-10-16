from pydantic import BaseModel, Field, ValidationError, model_validator, field_validator, ConfigDict
from enum import Enum


class HubType(str, Enum):
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    EXIT = "exit"


class Zone(str, Enum):
    cost: int | None
    
    NORMAL = ("normal", 1)
    BLOCKED = ("blocked", None)
    RESTRICTED = ("restricted", 2)
    PRIORITY = ("priority", 1)

    def __new__(cls, text: str, cost: int | None) -> "Zone":
        objeto = str.__new__(cls, text)
        objeto._value_ = text
        objeto.cost = cost
        return objeto


class Hub(BaseModel):
    NAME: str = Field(alias="name")
    X: int = Field(alias="x")
    Y: int = Field(alias="y")
    TYPE: HubType = Field(alias="type", default="intermediate")
    ZONE: Zone = Field(alias="zone", default="normal")
    COLOR: str | None = Field(alias="color", default="grey")
    MAX_DRONES: int = Field(alias="max_drones", ge=1, default=1)

    @field_validator("NAME")
    @classmethod
    def valid_names(cls, NAME: str) -> str:
        if " " in NAME or "-" in NAME:
            raise ValueError(
                "Zone names cannot contain dashes or spaces")
        return NAME

    @field_validator("COLOR")
    @classmethod
    def OneWordColor(cls, COLOR: str) -> str:
        """color admite cualquier cadena válida de una sola palabra."""
        if COLOR is not None:
            color = COLOR.split()
            if len(color) > 1:
                raise ValueError(
                    "Color must be a single word")
        return COLOR
 

class Connections(BaseModel):
    HUB1: str = Field(alias="hub1")
    HUB2: str = Field(alias="hub2")
    LINK_CAPACITY: int | None = Field(alias="link_capacity", ge=1, default=1)

    @model_validator(mode="after")
    def UniqueHub(self) -> "Conections":
        if self.HUB1 == self.HUB2:
            raise ValueError("A Hub cannot connect to itself :(")
        return self


class Map_(BaseModel): 
    NB_DRONES: int = Field(alias="nb_drones", ge=1)
    HUBS: list[Hub] = Field(alias="Hubs", min_length=3)
    START_HUB: str = Field(alias="start_hub") #hay que hacer reglas con estte.
    END_HUB: str = Field(alias="end_hub")
    CONNECTIONS: list[Connections] = Field(alias="Connections") #hay que hacer reglas aqui tambien


    @field_validator("HUBS")
    @classmethod
    def one_start_end(cls, HUBS: HUBS) -> "HUBS":
        for hub_type in (HubType.ENTRY, HubType.EXIT):
            amount = sum(node.TYPE == hub_type for node in HUBS)

            if amount != 1:
                raise ValueError(
                    f"There must be exactly one {hub_type.value} hub")
        return HUBS

    @field_validator("HUBS")
    @classmethod
    def UniqueHubNames(cls, HUBS: HUBS) -> "HUBS":
        """Cada zona tiene un nombre único."""
        for index_hub, hub in enumerate(HUBS):
            if any (node.NAME == hub.NAME
                    for index_node, node in enumerate(HUBS)
                    if index_hub != index_node):
                raise ValueError(
                    f"Hubs name must be unique")
        return HUBS

    @field_validator("CONNECTIONS")
    def UniqueConnections(cls, CONNECTIONS) -> "CONNECTIONS":

        pairs: list[tuple[str | str]] = [(con.HUB1, con.HUB2) for con in CONNECTIONS]

        seen = set()

        for a, b in pairs:

            pair = frozenset((a, b)) # bidirectional set
            
            if pair in seen:
                raise ValueError("Pair or Hub Connections must be unique")

            seen.add(pair)

        return CONNECTIONS

    @model_validator(mode="after")
    def defined_connections(self) -> "CONNECTIONS":

        hub_names: list[str] = [hub.NAME for hub in self.HUBS]
        
        for name in hub_names:
            if any(con.HUB1 not in hub_names or con.HUB2 not in 
                   hub_names for con in self.CONNECTIONS):
                raise ValueError("Connections and hubs must coincide")

        return self

