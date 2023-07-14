from abc import ABC
from dataclasses import dataclass, field
from uuid import UUID
import uuid
from typing import NewType
import json
import sys
import os
import pickle
from functools import partialmethod

EntityId = NewType("EntityId", str)


@dataclass
class Entity:
    id: str = str(uuid.uuid4())
    name: str = ""
    inventory: list[str] = field(default_factory=lambda: [])
    location: list[str] = field(default_factory=lambda: [])
    connections: list[str] = field(default_factory=lambda: [])
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
    player: Entity = field(default_factory=lambda: Entity())
    parser: Entity = field(default_factory=lambda: Entity())
    entities: dict[str, Entity] = field(default_factory=lambda: {})
    words: dict[str, Entity] = field(default_factory=lambda: {})

    @partialmethod
    def look(self, name=None):
        if name is not None:
            self.look_at(name)
            return
        location = self.entities[self.player.location[-1]]
        print(f"> {location.description_long}")
        print("> This room contains: ", end="")
        for i in range(len(location.inventory) - 1):
            print(f"{self.entities[location.inventory[i]].name}, ", end="")
        print(self.entities[location.inventory[-1]].name)

    def look_at(self, name):
        for entity in self.get_surroundings(self.player):
            if entity.name == name:
                print(entity.description_long)

    def go(self, name):
        for entity in self.get_surroundings(self.player):
            if entity.name == name:
                self.player.location.append(entity.id)
                entity.inventory.append(self.player.id)

    def take(self, name):
        for entity in self.get_surroundings(self.player):
            if entity.name == name:
                entity.inventory.remove(entity.id)
                self.player.inventory.append(entity.id)

    @partialmethod
    def help(self):
        print("> possible actions include: ", end="")
        actions = list(self.words.keys())
        for i in range(len(actions) - 1):
            print(f"{actions[i]}, ", end="")
        print(actions[-1])

    def inventory(self):
        print(
            f"Your inventory currently holds {[entity.name for entity in self.get_inventory(self.player)]}"
        )

    def get_surroundings(self, entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.location[0]].inventory]

    def get_surroundings_by_name(self, entity, name) -> Entity:
        return next(
            (
                entity
                for entity in self.get_surroundings(self.player)
                if entity.name == name
            ),
            None,
        )

    def get_inventory(self, entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.id].inventory]

    def get_inventory_by_name(self, entity, name) -> Entity:
        return next(
            (entity for entity in entity.inventory if entity.name == name), None
        )

    def loop(self):
        while True:
            self.parse_input(iter(input(": ").split()), self.parser, None)

    def parse_input(self, input, current_word, action):
        next_word = next(input, None)
        if not next_word:
            try:
                action()
            except:
                print("I'm sorry; I'm not sure what you mean.")
        elif next_word in current_word.inventory:
            self.parse_input(
                input,
                self.words[next_word],
                getattr(self, next_word)
                if action is None
                else lambda: action(next_word),
            )
        elif next_word in [entity.name for entity in self.get_inventory(self.player)]:
            self.parse_input(input, current_word, lambda: action(next_word))
        elif next_word in [
            entity.name for entity in self.get_surroundings(self.player)
        ]:
            self.parse_input(input, current_word, lambda: action(next_word))
        else:
            self.parse_input(input, current_word, action)

    def load_entities(self):
        for root, dirs, files in os.walk("Data"):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as data:
                        entity = Entity.from_json(data.read())
                        if entity.name == "you":
                            self.player = entity
                        if entity.name == "parser":
                            self.parser = entity
                        self.entities[entity.id] = entity
                        match root:
                            case "Data":
                                self.entities[entity.id] = entity
                            case "Data\Words":
                                self.words[entity.name] = entity


game = Game()
game.load_entities()
game.loop()
