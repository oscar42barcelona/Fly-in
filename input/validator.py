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
    MAX_DRONES: int = Field(alias="max_drones", default=1)


class Connections(BaseModel):
    HUB1: str = Field(alias="hub1")
    HUB2: str = Field(alias="hub2")
    LINK_CAPACITY: int | None = Field(alias="link_capacity", default=1)


class Map_(BaseModel): 
    NB_DRONES: int = Field(alias="nb_drones", ge=1, le=100)
    HUBS: list[Hub]
    START_HUB: str = Field(alias="start_hub") #hay que hacer reglas con estte.
    END_HUB: str = Field(alias="end_hub")
    CONNECTIONS: list[Connections] #hay que hacer reglas aqui tambien

