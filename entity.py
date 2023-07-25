from ast import List
from dataclasses import dataclass, field
import json
import sys
from typing import List, NewType
import uuid

EntityId = NewType("EntityId", str)

@dataclass
class Entity:
    id: EntityId = str(uuid.uuid4())
    name: str = ""
    inventory: list[str] = field(default_factory=lambda: [])
    location: EntityId = ""
    description_long: str = ""
    description_short: str = ""
    hit_points: int = sys.maxsize
    unlocked_by: EntityId = ""
    destination: EntityId = ""
    dialogue: str = None
    takeable: bool = False
    lootable: bool = False
    damage: List[int] = field(default_factory=list)
    combat_level: int = None
    combat_experience: int = None
    loot_level: int = None
    loot_experience: int = None
    equiped: EntityId = None
    equipable: bool = False
    discovered: bool = False
    feature_one: EntityId = ""
    feature_two: EntityId = ""
    color: str = ""

    def to_json(self):
        return json.dumps(self, indent=4,default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, payload):
        return cls(**json.loads(payload))