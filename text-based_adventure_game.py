from abc import ABC
from dataclasses import dataclass, field
import uuid
from typing import NewType, List
import json
import sys
import os
import random
from functools import partialmethod
from pathlib import PurePath

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
    taken: bool = False
    damage: List[int] = field(default_factory=list)
    combat_level: int = None
    combat_experience: int = None
    equiped: EntityId = None
    equipable: bool = False
    discovered: bool = False

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
    
    def get_inventory_entity(self, name):
        """Gets an entity by name from the player's inventory"""
        return next(
            (
                entity
                for entity in self.get_inventory(self.player)
                if entity.name == name
            ),
            None,
        )
    
    def get_inventory(self, entity) -> list[Entity]:
        """returns a list of the player's inventory"""
        return [self.entities[id] for id in self.entities[entity.id].inventory]

    def check_inventory(self, name):
        """Gets an entity by name from the entity's inventory."""
        for i in range(0, len(self.player.inventory)):
            check = self.get_global_entity(self.player.inventory[i])
            if check.name == name:
                return check
        return False

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


    @partialmethod
    def drop(self, name):
        entity = self.check_inventory(name)
        drop_location = self.player.location[-1]
        if not entity:
            print("Cannot be found or does not exist.")
        elif not entity.taken:
            print(f'{entity.name} cannot be dropped, because it is not in the player`s inventory.')
        else:
            print(f'You drop {entity.name} on the floor in this room.')
            self.player.inventory.remove(entity.id)
            self.get_global_entity(drop_location).inventory.append(entity.id)
            entity.taken = False

    @partialmethod
    def equip(self, name):
        """equips an entity from the player's inventory to be used in an attack"""
        entity = self.get_inventory_entity(name)
        if not entity:
            print("Cannot be found or does not exit")
            return
        if not entity.equipable:
            print("Cannot be equiped")
            return
        if self.player.equiped != None:
            currently_equiped = self.entities[self.player.equiped]
            print(f'You unequip {currently_equiped.name}')
            print(f'{currently_equiped.name} sent to your inventory')
        self.player.equiped = entity.id
        print(f'You equip {entity.name}')

    @partialmethod
    def attack(self, name):
        for entity in self.get_surroundings(self.player):
            if entity.name == name:
                held_item = self.player.equiped
                weapon = self.get_global_entity(held_item)
                damage = random.randint(weapon.damage[0], weapon.damage[1])
                entity.hit_points -= (damage * self.player.combat_level) + 1
                print(
                    f"{weapon.name} did {damage} points of damage to {entity.name}"
                )
                self.set_exp_level("combat_level")
                if entity.hit_points <= 0:
                    print(
                        f"{entity.name} has been destroyed by your {weapon}!"
                    )
                    self.get_global_entity(self.player.location[-1]).inventory.remove(entity.id)
                    self.set_exp_level("combat_level")

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

    def get_level(self, level_type):
        level = 0
        if level_type == "combat" or level_type == "combat_level":
            level = self.player.combat_level
            print(
                f"Your combat level is {level}"
            )

    def set_exp_level(self, exp_type):
        """ Leveling system called by functions that allow players to do actions associated with the 3 skills"""
        exp = self.player.combat_experience
        level = 0
        if exp_type == "combat_level":
            exp = self.player.combat_experience
            level = self.player.combat_level
        # Can add the other 2 leveling features when base action is implemented

        exp += 1
        if exp == 1:
            level = 1
        if exp == 4:
            level = 2
        if exp >= 7:
            level = 3
        if exp == 1 or exp == 4 or exp == 7:
            print(
                f"Your {exp_type} is now level {level}!"
            )

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
            root = os.path.join(root).replace("\\","/")
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as data:
                        match root:
                            case "Data/Words":
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
