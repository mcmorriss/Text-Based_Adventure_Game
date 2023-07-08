from abc import ABC
from dataclasses import dataclass, field
from uuid import UUID
import uuid
from typing import NewType
import json
import sys
import os


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
    player: Entity = field(default_factory = lambda : Entity())
    entities: dict[str, Entity] = field(default_factory = lambda: {})

    def look(self):
        location = self.entities[self.player.location[-1]]
        print(f'> {location.description_long}')
        print("> This room contains: ", end="")
        for i in range(len(location.inventory) - 1):
            print(f'{self.entities[location.inventory[i]].name}, ', end="")
        print(self.entities[location.inventory[-1]].name)
            
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
        print("> possible actions include: ", end="")
        actions = list(self.actions.keys())
        for i in range(len(actions) - 1):
            print(f'{actions[i]}, ', end="")
        print(actions[-1])


    def inventory(self):
        pass

    actions = {
        "look": look,
        "look at": look_at,
        "go": go,
        "take": take,
        "help": help,
        "inventory": inventory,
    }

    def get_surroundings(self) -> list[Entity]:
        return [self.entities[id] for id in self.entities[self.player.location[0]].inventory]

    def loop(self):
        while True:
            self.parse_input(iter(input(': ').split()))

    def parse_input(
        self, input
    ):
        match next(input):
            case "look":
                try:
                    match next(input):
                        case "at":
                            self.look_at(input.next())
                except:
                    self.look()
            case "help":
                self.help()
            case _:
                print("> I'm not sure what you mean")

    def load_entities(self):
        for filename in os.listdir('Data'):
            if filename.endswith('.json'):
                with open(f'Data/{filename}', 'r') as data:
                    entity = Entity.from_json(data.read())
                    if entity.name == 'you':
                        self.player = entity
                    self.entities[entity.id] = entity

game = Game()
game.load_entities()
game.loop()
