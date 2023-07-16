from abc import ABC
from dataclasses import dataclass, field
import uuid
from typing import NewType, List
import json
import sys
import os
import pickle
import random
from functools import partialmethod

EntityId = NewType("EntityId", str)

class Entity:
    pass

@dataclass
class Entity:
    id: EntityId = str(uuid.uuid4())
    name: str = ""
    inventory: list[str] = field(default_factory=lambda: [])
    location: list[str] = field(default_factory=lambda: [])
    description_long: str = ""
    description_short: str = ""
    hit_points: int = sys.maxsize
    unlocked_by: EntityId = None
    destination: EntityId = None
    dialogue: str = None
    takeable: bool = False
    damage: List[int] = field(default_factory=list)

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

    def get_global_entity(self, identifier):
        """Attempts to get the entity associated with the identifier
        the identifier can be the id or a name"""
        try:
            return self.entities[identifier]
        except:
            for entity in self.entities:
                if entity.name == identifier:
                    return entity
                
    def get_local_entity(self, entity, name) -> Entity:
        """Gets an entity by name from the entity's immediate surroundings"""
        return next(
            (
                entity
                for entity in self.get_surroundings(self.player)
                if entity.name == name
            ),
            None,
        )

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

    @partialmethod
    def go(self, name):
        door = self.get_local_entity(self.player, name)
        if not door:
            print("Cannot be found or does not exist")
        elif not door.destination:
            print("This does not appear to be traversable")
        elif door.unlocked_by and door.unlocked_by not in self.player.inventory:
            print("You are missing something in your inventory required to traverse through this")
        else:
            self.player.location.append(door.destination)
            door.inventory.append(self.player.id)
            print(f'You travel through {name} and arrive at {self.get_global_entity(door.destination).name}')
            self.look()


    @partialmethod
    def take(self, name):
        entity = self.get_local_entity(self.player, name)
        if not entity:
            print("Cannot be found or does not exist")
        elif not entity.takeable:
            print("Cannot be taken")
        else:
            print(f'You take {entity.name}')
            self.player.inventory.append(entity.id)
            self.get_global_entity(self.player.location[-1]).inventory.remove(entity.id)

    def attack(self, name):
        for entity in self.get_surroundings(self.player):
            if entity.name == name:
                items = self.get_inventory(self.player)
                weapon = items[0]
                # Need to rethink how to access the damage value in the weapon; will likely be easier once we have the
                # "equiped" slot implemented.
                damage = [random.randint(weapon.damage[0], weapon.damage[1]) for _ in range(1)]
                entity.hit_points -= damage
                if entity.hit_points >= 0:
                    print(
                        f"{entity.name} has been destroyed by your {weapon}!"
                    )
                    # Need to remove from entity from room, need to rethink how to access it
                    # entity.inventory.remove(entity.id)

    @partialmethod
    def help(self):
        print("> possible actions include: ", end="")
        actions = list(self.words.keys())
        for i in range(len(actions) - 1):
            print(f"{actions[i]}, ", end="")
        print(actions[-1])

    @partialmethod
    def talk(self, npc):
        npc = self.get_local_entity(self.player, npc)
        if not npc:
            print("Cannot be found or does not exist")
        elif not npc.dialogue:
            print("Does not appear to be very talkative. Best left to its own devices.")
        else:
            print(npc.dialogue)

    def inventory(self):
        print(
            f"Your inventory currently holds {[entity.name for entity in self.get_inventory(self.player)]}"
        )

    def get_surroundings(self, entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.location[-1]].inventory]

    def get_inventory(self, entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.id].inventory]

    def loop(self):
        while True:
            self.parse_input(iter(input(": ").split()), self.parser, None)

    def parse_input(self, input, current_word, action):
        """Looks through the player's input from left to right
        if the word is a known action, treat that action as a method
        then we can build up a method call by currying.
        See https://en.wikipedia.org/wiki/Currying and
        https://docs.python.org/3/library/functools.html#functools.partialmethod
        for further information."""
        next_word = next(input, None)
        # we've reached the end of the user input
        # try to call the method we've built up
        if not next_word:
            try:
                action()
            except Exception as e:
                print(e)
                print("I'm sorry; I'm not sure what you mean.")
        # if the next word links to the current word
        # pass that word as an argument it our action
        elif next_word in current_word.inventory:
            self.parse_input(
                input,
                self.words[next_word],
                getattr(self, next_word)
                if action is None
                else lambda: action(next_word),
            )
        # if the next word is a name of an entity in the player's inventory
        # pass that entity as an argument to our action
        elif next_word in [entity.name for entity in self.get_inventory(self.player)]:
            self.parse_input(input, current_word, lambda: action(next_word))
        # if the next word is a name of an entity in our player's location
        # pass that entity as an argument to our action
        elif next_word in [
            entity.name for entity in self.get_surroundings(self.player)
        ]:
            self.parse_input(input, current_word, lambda: action(next_word))
        # if the next word isn't a known word
        # skip it
        else:
            self.parse_input(input, current_word, action)

    def load_entities(self):
        for root, dirs, files in os.walk("Data"):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as data:
                        match root:
                            case "Data\\Words":
                                entity = Entity.from_json(data.read())
                                self.words[entity.name] = entity
                            case _:
                                entity = Entity.from_json(data.read())
                                self.entities[entity.id] = entity
                        if entity.name == "you":
                            self.player = entity
                        if entity.name == "parser":
                            self.parser = entity

game = Game()
game.load_entities()
game.loop()
