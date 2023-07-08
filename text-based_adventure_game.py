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
    player: Entity = Entity()
    entities: dict[str, Entity] = field(default_factory = lambda: {})

    def look(self):
        location = self.entities[self.player.location[-1]]
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
                self.player.location.append(entity.id)
                entity.inventory.append(self.player.id)

    def take(self, name):
        for entity in self.get_surroundings():
            if entity.name == name:
                entity.inventory.remove(entity.id)
                self.player.inventory.append(entity.id)

    def help(self):
        print('> help')

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
        return [self.entities[id] for id in self.entities[self.player.location[0]].inventory]

    def loop(self):
        while True:
            self.parse_input(input('< ').split())

    def parse_input(
        self, input
    ):
        for token in input:
            if token in self.actions.keys():
                self.actions[token](self)


with open('Data/player.json', 'r') as data:
    player = Entity.from_json(data.read())
    print(player)

game = Game()
game.loop()
