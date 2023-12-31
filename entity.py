from dataclasses import dataclass, field
import json
import sys
from typing import List, NewType
import uuid

EntityId = NewType("EntityId", str)
EntityName = NewType("EntityName", str)


@dataclass
class Entity:
    id: EntityId = str(uuid.uuid4())
    name: str = ""
    inventory: List[str] = field(default_factory=lambda: [])
    location: EntityId = ""
    description_long: str = ""
    description_short: str = ""
    hit_points: int = sys.maxsize
    unlocked_by: EntityId = ""
    destination: EntityId = ""
    dialogue: str = ""
    takeable: bool = False
    lootable: bool = False
    spawnable: bool = False
    spawns: EntityId = ""
    damage: List[int] = field(default_factory=list)
    combat_level: int = None
    combat_experience: int = None
    loot_level: int = 0
    loot_experience: int = 0
    equiped: EntityId = None
    equipable: bool = False
    drinkable: bool = False
    discovered: bool = False
    color: str = ""
    crouched: bool = False
    ingredient: EntityId = None
    produces: EntityId = None
    use: str = ""
    usable: bool = False
    take: str = ""
    go_interrupt: str =""
    north: EntityId = None
    south: EntityId = None
    east: EntityId = None
    west: EntityId = None

    def __callable__(self):
        pass

    def to_json(self):
        return json.dumps(self, indent=4, cls=EntityEncoder)

    @classmethod
    def from_json(cls, payload):
        return cls(**json.loads(payload))


class EntityEncoder(json.JSONEncoder):
    def default(self, obj):
        obj_dict = obj.__dict__
        obj_dict.pop("inventory")
        return obj_dict
