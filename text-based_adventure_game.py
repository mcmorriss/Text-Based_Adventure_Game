from dataclasses import dataclass, field
import random
from functools import partialmethod

from entities import Entities


@dataclass
class Game:
    entities: Entities = field(default_factory=lambda: Entities())

    @partialmethod
    def look(self, name=None):
        if name is not None:
            self.look_at(name)
            return
        location = self.entities.entity(self.entities.player.location)
        print(f"> {location.description_long}")
        print("> This room contains: ", end="")
        print(
            *[entity.name for entity in self.entities.get_inventory(location)], sep=", "
        )

    def look_at(self, name):
        for entity in self.entities.get_surroundings(self.entities.player):
            if entity.name == name:
                print(entity.description_long)

    @partialmethod
    def go(self, name):
        door = self.entities.get_local_entity(self.entities.player, name)
        if not door:
            print("Cannot be found or does not exist")
        elif not door.destination:
            print("This does not appear to be traversable")
        elif (
            door.unlocked_by and door.unlocked_by not in self.entities.player.inventory
        ):
            print(
                "You are missing something in your inventory required to traverse through this"
            )
        else:
            self.entities.player.location = door.destination
            door.inventory.append(self.entities.player.id)
            print(
                f"You travel through {name} and arrive at {self.entities.get_global_entity(door.destination).name}"
            )
            self.look()

    @partialmethod
    def take(self, name):
        entity = self.entities.get_local_entity(self.entities.player, name)
        if not entity:
            print("Cannot be found or does not exist")
        elif not entity.takeable:
            print("Cannot be taken")
        else:
            print(f"You take {entity.name}")
            self.entities.player.inventory.append(entity.id)
            self.entities.get_global_entity(
                self.entities.player.location
            ).inventory.remove(entity.id)
            entity.location = self.entities.player.id

    @partialmethod
    def drop(self, name):
        entity = self.entities.get_inventory_entity(name)
        drop_location = self.entities.player.location
        if not entity:
            print("Cannot be found or does not exist.")
        else:
            print(f"You drop {entity.name}.")
            self.entities.player.inventory.remove(entity.id)
            entity.location = self.entities.player.id
            self.entities.get_global_entity(drop_location).inventory.append(entity.id)

    @partialmethod
    def equip(self, name):
        """equips an entity from the player's inventory to be used in an attack"""
        entity = self.entities.get_inventory_entity(name)
        if not entity:
            print(f"{name} cannot be found or does not exit")
            return
        if not entity.equipable:
            print(f"{name} cannot be equiped")
            return
        if self.entities.player.equiped != None:
            currently_equiped = self.entities.entity(self.entities.player.equiped)
            print(f"You unequip {currently_equiped.name}")
            print(f"{currently_equiped.name} sent to your inventory")
        self.entities.player.equiped = entity.id
        print(f"You equip {entity.name}")

    @partialmethod
    def attack(self, name):
        entity = self.entities.get_local_entity(self.entities.player, name)
        if not entity:
            print(f"{name} Cannot be found or does not exist")
        if not self.entities.player.equiped:
            print(f"Nothing equiped. Equip a weapon before attacking")
        else:
            held_item = self.entities.player.equiped
            weapon = self.entities.get_global_entity(held_item)
            damage = random.randint(weapon.damage[0], weapon.damage[1])
            total_damage = int(damage * self.entities.player.combat_level) + 1
            entity.hit_points -= total_damage
            if entity.hit_points <= 0:
                entity.hit_points = 0
            print(
                f"The {weapon.name} did {total_damage} points of damage to {entity.name}. {entity.hit_points} remain"
            )
            self.entities.set_exp_level("combat_level")
            if entity.hit_points <= 0:
                print(f"The {entity.name} has been destroyed by your {weapon.name}!")
                entity.lootable = True
                # Add "dead" label?
                self.entities.set_exp_level("combat_level")

    @partialmethod
    def loot(self, name):
        entity = self.entities.get_local_entity(self.entities.player, name)
        if not entity:
            print(f"The {name} Cannot be found or does not exist.")
        elif not hasattr(entity, 'lootable'):
            print(f"{name} cannot be looted or has no items")
        elif entity.lootable is not True:
            print(f"{name} cannot be looted right now.")
        else:
            looted_item = entity.inventory[0]
            entity.inventory.remove(looted_item)
            self.entities.player.inventory.append(looted_item)
            print(f"You take {looted_item}. It has been stored in your inventory.")
            self.entities.set_exp_level("loot_level")

    @partialmethod
    def help(self):
        print("> possible actions include: ", end="")
        actions = list(self.entities.words.keys())
        for i in range(len(actions) - 1):
            print(f"{actions[i]}, ", end="")
        print(actions[-1])

    @partialmethod
    def talk(self, npc):
        npc = self.entities.get_local_entity(self.entities.player, npc)
        if not npc:
            print("Cannot be found or does not exist")
        elif not npc.dialogue:
            print("Does not appear to be very talkative. Best left to its own devices.")
        else:
            print(npc.dialogue)

    @partialmethod
    def loadgame(self):
        self.entities.load_entities("data/save")

    @partialmethod
    def savegame(self):
        for entity in self.entities():
            with open(f"data/save/{entity.name}.json", "w") as file:
                file.write(entity.to_json())

    @partialmethod
    def inventory(self):
        print(
            f"Your inventory currently holds {[entity.name for entity in self.entities.get_inventory(self.entities.player)]}"
        )

    def get_level(self, level_type):
        level = 0
        if level_type == "combat" or level_type == "combat_level":
            level = self.entities.player.combat_level
            print(f"Your combat level is {level}")
        if level_type == "looting" or level_type == "looting_level":
            level = self.entities.player.loot_level
            print(f"Your combat level is {level}")
        else:
            print(
                f"'{level_type}' is not a valid entry. Please enter 'combat' or 'looting'"
            )

    def loop(self):
        while True:
            self.parse_input(iter(input(": ").split()), self.entities.parser, None)

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
                self.entities.words[next_word],
                getattr(self, next_word)
                if action is None
                else lambda: action(next_word),
            )
        # if the next word is a name of an entity in the player's inventory
        # pass that entity as an argument to our action
        elif next_word in [
            entity.name for entity in self.entities.get_inventory(self.entities.player)
        ]:
            self.parse_input(input, current_word, lambda: action(next_word))
        # if the next word is a name of an entity in our player's location
        # pass that entity as an argument to our action
        elif next_word in [
            entity.name
            for entity in self.entities.get_surroundings(self.entities.player)
        ]:
            self.parse_input(input, current_word, lambda: action(next_word))
        # if the next word isn't a known word
        # skip it
        else:
            self.parse_input(input, current_word, action)


game = Game()
game.entities.load_entities("data/new")
game.loop()
