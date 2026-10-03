from pydantic import BaseModel, Field, ValidationError, model_validator
from enum import Enum

class HubType(str, Enum):
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    EXIT = "exit"


class Zone(str, Enum):
    """Posponer hasta realizar quizzes y pildoras"""
    ...

class Map(BaseModel): 
    NB_DRONES: int = Field(alias="nb_drones", ge=1, le=100)
    HUBS: list[Hub]
    START_HUB: str = Field(alias="start_hub") #hay que hacer reglas con estte.
    END_HUB: str = Field(alias="end_hub")
    CONNECTIONS: list(Connections) #hay que hacer reglas aqui tambien


class Hub(BaseModel):
    NAME: str = Field(alias="name")
    X: int = Field(alias="x")
    Y: int = Field(alias="y")
    TYPE: Type = Field(alias="type", default=____)
    ZONE: Zone = Field(alias="zone", default=____)
    COLOR: str | None = Field(alias="color", default=____)
    MAX_DRONES: int = Field(alias="max_drones", default=____)
