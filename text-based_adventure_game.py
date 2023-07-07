from abc import ABC
from dataclasses import dataclass, field
from uuid import UUID
import uuid
from typing import NewType
import json
import sys


EntityId = NewType("EntityId", str)


@dataclass
class Entity:
    id: str = str(uuid.uuid4())
    name: str = ""
    inventory: list[str] = field(default_factory=lambda: [])
    location: list[str] = field(default_factory=lambda: [])
    description_long: str = ""
    description_short: str = ""
    hit_points: int = sys.maxsize

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, payload):
        return cls(**json.loads(payload))


@dataclass
class Game:
    player: Entity
    entities: dict[EntityId, Entity]

    def look(self):
        location = self.entities[self.player.location[0]]
        print(location.description_long)
        contains = ""
        for entity in location.inventory:
            contains += self.entities[entity].name.join(", ")
        print(f"contains {contains}")

    def look_at(self, name):
        for entity in self.get_surroundings():
            if entity.name == name:
                print(entity.description_long)

    def go(self, name):
        for entity in self.get_surroundings():
            if entity.name == name:
                self.player.location[0].remove(self.player.id)
                entity.append(self.player.id)

    def take(self):
        pass

    def help(self):
        pass

    def inventory(self):
        pass

    actions = {
        "look": look,
        "look_at": look_at,
        "go": go,
        "take": take,
        "help": help,
        "inventory": inventory,
    }

    def get_surroundings(self) -> list[Entity]:
        return self.entities[self.player.location[0]].inventory

    def loop(self, prompt):
        input = input().split()

    def parse_input(
        self,
    ):
        for token in input:
            pass
