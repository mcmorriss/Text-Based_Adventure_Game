from dataclasses import dataclass, field
import inspect
import random
from entities import Entities
from typing import List


@dataclass
class Action:
    entities: Entities = field(default_factory=lambda: Entities())
    actions: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.actions = [
            action
            for action, _ in inspect.getmembers(self)
            if not action.startswith("_")
        ]
        self.actions.remove("actions")
        self.actions.remove("entities")

    def warp(self, name):
        destination = self.entities.entity(name)
        if not destination:
            print(f"{name} does not appear to be a valid destination")
        else:
            self.entities.player.location = destination.id
            destination.inventory.append(self.entities.player.id)
            self.look()

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

    def attack(self, name):
        entity = self.entities.get_local_entity(name, self.entities.player)
        if not entity:
            print(f"{name} Cannot be found or does not exist")
            return
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

    def open(self, name):
        self.loot(name)
    
    def loot(self, name=None, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        entity = self.entities.get_local_entity(name, subject)
        if not entity:
            print(f"{name} cannot be found or does not exist.")
        elif hasattr(entity, "spawnable") and entity.spawnable:
            spawn_entity = self.entities.get_global_entity(entity.spawns)
            spawn_location = self.entities.get_global_entity(self.entities.player.location)
            spawn_entity.location = entity.location
            entity.inventory.remove(spawn_entity.id)
            spawn_location.inventory.append(spawn_entity.id)
            print(f"A {spawn_entity.name} appears after you attempt to loot the {entity.name}! \n Be prepared to engage in combat!")
        elif not hasattr(entity, "lootable"):
            print(f"{name} cannot be looted or has no items")
        elif entity.lootable is not True:
            print(f"{name} cannot be looted right now.")
        elif len(entity.inventory) == 0:
            print(f"{name} contains no loot")
        else:
            looted_item = self.entities.get_inventory_entity(
                entity.inventory[-1], entity
            )
            entity.inventory.remove(looted_item.id)
            subject.inventory.append(looted_item.id)
            print(
                f"{subject.name} looted a {looted_item.name} from the {name}. It has been stored in {subject.name}'s inventory."
            )
            self.entities.set_exp_level("loot_level", subject)

    def mine(self, name):
        entity = self.entities.get_local_entity(name, self.entities.player)
        pickaxe = self.entities.get_inventory_entity("pickaxe")
        if not entity:
            print(f"The {name} cannot be mined or does not exist.")
        elif not pickaxe:
            print(f"You need a pickaxe in your inventory to mine the {name}.")
        else:
            mined = self.entities.get_global_entity(entity.inventory[0])
            entity.inventory.remove(mined.id)
            self.entities.player.inventory.append(mined.id)
            print(
                f"You mine a {mined.name} from the {name}. It has been stored in your inventory."
            )

    def talk(self, npc):
        npc = self.entities.get_local_entity(npc, self.entities.player)
        if not npc:
            print("Cannot be found or does not exist")
        elif not npc.dialogue:
            print("Does not appear to be very talkative. Best left to its own devices.")
        else:
            print(f'{npc.name}: {npc.dialogue}')

    def crouch(self):
        if self.entities.player.crouched is True:
            print("You are already crouching")
        else:
            self.entities.player.crouched = True
            print("You are now crouching")

    def standup(self):
        if self.entities.player.crouched is False:
            print("You are already standing")
        else:
            self.entities.player.crouched = False
            print("You are now standing")

    def drink(self, name):
        entity = self.entities.get_inventory_entity(name)
        test = [x.id for x in self.entities() if x.name == 'status_effect']
        if not entity:
            print(f"{name} is not in your inventory")
            return
        elif not entity.drinkable:
            print(f"Er... I don't think {name} is something you can drink.")
            return
        else:
            print(f"You drink {name}")
            self.entities.player.inventory.remove(entity.id)
            self.entities.player.inventory.append(test[0])

    def craft(self, name):
        outcome = "You don't appear to know any recipes"
        for entity_id in self.entities.player.inventory:
            recipe = self.entities.entity(entity_id)
            product = self.entities.entity(recipe.produces)
            ingredient = self.entities.entity(recipe.ingredient)
            if not product or not ingredient:
                continue
            elif product.name != name:
                outcome = f"You don't appear to know any recipes that produce {name}"
            elif ingredient.id not in self.entities.player.inventory:
                outcome = f"You need {ingredient.name} to produce {product.name}"
            else:
                self.entities.player.inventory.append(product.id)
                self.entities.player.inventory.remove(ingredient.id)
                print(f"{ingredient.name} removed from inventory")
                print(f"{product.name} added to inventory")
                outcome = f"you craft {product.name} by action of {recipe.name} consuming {ingredient.name} in the process"
        print(outcome)

    def use(self, name, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        object = self.entities.get_proximal_entity(name, subject)
        if not object:
            print("Cannot be found or does not exist")
        elif not object.usable:
            print("Cannot be used")
        else:
            object.usable = False
            return f"{object.use}"

    def exit(self):
        exit()

    def loadgame(self):
        self.entities.load_entities("data/save")

    def savegame(self):
        for entity in self.entities():
            with open(f"data/save/{entity.name}.json", "w") as file:
                file.write(entity.to_json())

    def inventory(self):
        status = "status_effect"
        print(
            f"Your inventory currently holds {[entity.name for entity in self.entities.get_inventory(self.entities.player) if entity.name != status]}"
        )

    def pick(self, name):
        self.take(name)

    def take(self, name, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        object = self.entities.get_local_entity(name, subject)
        if not object:
            print("Cannot be found or does not exist")
        elif not object.takeable:
            print("Cannot be taken")
        else:
            print(f"You take {object.name}")
            subject.inventory.append(object.id)
            self.entities.get_global_entity(object.location).inventory.remove(object.id)
            object.location = subject.id
            return f"{object.take}"

    def drop(self, name=None, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        object = self.entities.get_inventory_entity(name, subject)
        drop_location = subject.location
        if not name:
            print("Need something to drop")
        elif not object:
            print("Cannot be found or does not exist.")
        else:
            print(f"{object.name} dropped by {subject.name}.")
            subject.inventory.remove(object.id)
            object.location = subject.location
            self.entities.get_global_entity(drop_location).inventory.append(object.id)

    def look(self, name=None):
        if name:
            for entity in self.entities.get_surroundings(self.entities.player):
                if entity.name == name:
                    print(entity.description_long)
            for entity in self.entities.get_inventory(self.entities.player):
                if entity.name == name:
                    print(entity.description_long)
        else:
            location = self.entities.entity(self.entities.player.location)
            print(location.description_long)
            self.contains(location.id)

    def contains(self, object):
        object = self.entities.entity(object)
        if not object:
            print("Cannot be found or does not exist.")
        if object.name == "open_field" or object.name == "credits":
            return
        else:
            print(f"{object.name} contains: ", end="")
            print(
                *[entity.name for entity in self.entities.get_inventory(object)],
                sep=", ",
            )

    def walk(self, name):
        self.go(name)

    def sneak(self, subject=None):
        subject = self.entities.player if subject is None else self.entities.entity(subject)
        stealth = self.entities.entity('stealth')
        if stealth.id in subject.inventory:
            subject.inventory.remove(stealth.id)
            print(f'{subject.name} emerges from the shadows')
        else:
            subject.inventory.append(stealth.id)
            print(f'{subject.name} slips into the shadows')

    def _move(self, object, subject):
        self.entities.entity(subject.location).inventory.remove(subject.id)
        subject.location = object.id
        object.inventory.append(subject.id)

    def go(self, name, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        door = self.entities.get_local_entity(name, self.entities.player)
        if not door:
            print("Cannot be found or does not exist")
        elif not door.destination:
            print("This does not appear to be traversable")
        elif (
                door.unlocked_by and door.unlocked_by not in self.entities.player.inventory
        ):
            if door.go_interrupt:
                return door.go_interrupt
            else:
                print(
                    "You are missing something in your inventory required to traverse through this"
                )
        else:
            destination = self.entities.entity(door.destination)
            self._move(destination, subject)
            if destination.name != "barricaded_door" and destination.name != "credits":
                print(
                    f"You traverse {door.name} and arrive at {destination.name}"
                )
            if destination.discovered:
                print(f"{destination.description_short}")
            else:
                print(f"{destination.description_long}")
            destination.discovered = True
            self.contains(destination.id)

    def _cardinal(self, direction, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        location = self.entities.entity(subject.location)
        direction = getattr(location, direction)
        if direction:
            self.go(direction)
        else:
            print("impassable")

    def north(self):
        self._cardinal("north")

    def south(self):
        self._cardinal("south")

    def east(self):
        self._cardinal("east")

    def west(self):
        self._cardinal("west")

    def help(self):
        print(f"possible actions include: {self.actions}")
