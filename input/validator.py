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

    @field_validator("NAME")
    @classmethod
    def valid_names(cls, NAME: str) -> str:
        if " " in name or "-" in name:
            raise ValueError(
                "Zone names cannot contain dashes or spaces")
        return name
 

class Connections(BaseModel):
    HUB1: str = Field(alias="hub1")
    HUB2: str = Field(alias="hub2")
    LINK_CAPACITY: int | None = Field(alias="link_capacity", default=1)

    @model_validator(mode="after")
    def UniqueHub(self) -> "Conections"
        if self.HUB1 == self.HUB2:
            raise ValueError("A Hub cannot connect to itself :(")
        return self
    

class Map_(BaseModel): 
    NB_DRONES: int = Field(alias="nb_drones", ge=1, le=100)
    HUBS: list[Hub] = Field(alias="Hubs", ge=3)
    START_HUB: str = Field(alias="start_hub") #hay que hacer reglas con estte.
    END_HUB: str = Field(alias="end_hub")
    CONNECTIONS: list[Connections] = Field(alias="Connections") #hay que hacer reglas aqui tambien


    @field_validator("HUBS")
    @classmethod
    def one_start_end(cls, HUBS: list[hub]) -> "HUBS"
        for hub_type in (HubType.ENTRY, HubType.EXIT):
            amount = sum(node.TYPE == hub_type for node in HUBS)

            if amount != 1:
                raise ValueError(
                    f"There must be exactly one {hub_type.value} hub")
        return HUBS

    @field_validator(CONNECTIONS, mode="after")
    def UniqueConnections(cls, CONNECTIONS: list[Connections]) -> "CONNECTIONS":
        list_: list[tuple[tuple, tuple]] = [] #bidirectional list
        counter: int = 0
        i: int = 1

        for con in CONNECTIONS:
            tuple1 = (con.HUB1, con.HUB2)
            tuple2 = (con.HUB2, con.HUB1)
            list_.append((tuple1, tuple2))

        for item in list_:
            pair = item[0]
            counter += 1
            i = 1
            for valores in list_:
                if i == counter:
                    i += 1
                    continue
                if pair in valores:
                    raise ValueError("Pair or Hub Connections must be unique")
                i += 1
        return CONNECTIONS

