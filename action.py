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
            return (None, f"{name} does not appear to be a valid destination")
        else:
            self._move(destination, self.entities.player)
            return self.look()

    def equip(self, name):
        """equips an entity from the player's inventory to be used in an attack"""
        entity = self.entities.get_inventory_entity(name)
        if not entity:
            return (None, f"{name} cannot be found or does not exit")
        elif not entity.equipable:
            return (None, f"{name} cannot be equiped")
        elif self.entities.player.equiped != None:
            currently_equiped = self.entities.entity(self.entities.player.equiped)
            self.entities.player.equiped = entity.id
            return (None, f"You unequip {currently_equiped.name}\n{currently_equiped.name} sent to your inventory\nYou equip {entity.name}")
        else:
            self.entities.player.equiped = entity.id
            return (None, f"You equip {entity.name}")

    def attack(self, name):
        entity = self.entities.get_local_entity(name, self.entities.player)
        if not entity:
            return (None, f"{name} Cannot be found or does not exist")
        if not self.entities.player.equiped:
            return (None, f"Nothing equiped. Equip a weapon before attacking")
        held_item = self.entities.player.equiped
        weapon = self.entities.get_global_entity(held_item)
        damage = random.randint(weapon.damage[0], weapon.damage[1])
        total_damage = int(damage * self.entities.player.combat_level) + 1
        entity.hit_points -= total_damage
        self.entities.set_exp_level("combat_level")
        if entity.hit_points <= 0:
            entity.hit_points = 0
            entity.lootable = True
            self.entities.set_exp_level("combat_level")
            return (None,
                f"The {weapon.name} did {total_damage} points of damage to {entity.name}. {entity.hit_points} remain\nThe {entity.name} has been destroyed by your {weapon.name}!"
            )
        else:
            return (None, f"The {weapon.name} did {total_damage} points of damage to {entity.name}. {entity.hit_points} remain")

    def open(self, name):
        return self.loot(name)
    
    def loot(self, name=None, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        entity = self.entities.get_local_entity(name, subject)
        if not entity:
            return (None, f"{name} cannot be found or does not exist.")
        elif hasattr(entity, "spawnable") and entity.spawnable:
            spawn_entity = self.entities.get_global_entity(entity.spawns)
            spawn_location = self.entities.get_global_entity(self.entities.player.location)
            spawn_entity.location = entity.location
            entity.inventory.remove(spawn_entity.id)
            spawn_location.inventory.append(spawn_entity.id)
            return (None, f"A {spawn_entity.name} appears after you attempt to loot the {entity.name}! \n Be prepared to engage in combat!")
        elif not hasattr(entity, "lootable"):
            return (None, f"{name} cannot be looted or has no items")
        elif entity.lootable is not True:
            return (None, f"{name} cannot be looted right now.")
        elif len(entity.inventory) == 0:
            return (None, f"{name} contains no loot")
        else:
            looted_item = self.entities.get_inventory_entity(
                entity.inventory[-1], entity
            )
            entity.inventory.remove(looted_item.id)
            subject.inventory.append(looted_item.id)
            self.entities.set_exp_level("loot_level", subject)
            return (None,
                f"{subject.name} looted a {looted_item.name} from the {name}. It has been stored in {subject.name}'s inventory."
            )

    def mine(self, name):
        entity = self.entities.get_local_entity(name, self.entities.player)
        pickaxe = self.entities.get_inventory_entity("pickaxe")
        if not entity:
            return (None, f"The {name} cannot be mined or does not exist.")
        elif not pickaxe:
            return (None, f"You need a pickaxe in your inventory to mine the {name}.")
        else:
            mined = self.entities.get_global_entity(entity.inventory[0])
            entity.inventory.remove(mined.id)
            self.entities.player.inventory.append(mined.id)
            return (None,
                f"You mine a {mined.name} from the {name}. It has been stored in your inventory."
            )

    def talk(self, npc):
        npc = self.entities.get_local_entity(npc, self.entities.player)
        if not npc:
            return (None, "Cannot be found or does not exist")
        elif not npc.dialogue:
            return (None, "Does not appear to be very talkative. Best left to its own devices.")
        else:
            return (None, f'{npc.name}: {npc.dialogue}')

    def crouch(self):
        if self.entities.player.crouched is True:
            return (None, "You are already crouching")
        else:
            self.entities.player.crouched = True
            return (None, "You are now crouching")

    def standup(self):
        if self.entities.player.crouched is False:
            return (None, "You are already standing")
        else:
            self.entities.player.crouched = False
            return (None, "You are now standing")

    def drink(self, name):
        entity = self.entities.get_inventory_entity(name)
        test = [x.id for x in self.entities() if x.name == 'status_effect']
        if not entity:
            return (None, f"{name} is not in your inventory")
        elif not entity.drinkable:
            return (None, f"Er... I don't think {name} is something you can drink.")
        else:
            self.entities.player.inventory.remove(entity.id)
            self.entities.player.inventory.append(test[0])
            return (None, f"You drink {name}")

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
                outcome = f"{ingredient.name} removed from inventory\n"
                outcome += f"{product.name} added to inventory\n"
                outcome += f"you craft {product.name} by action of {recipe.name} consuming {ingredient.name} in the process"
        return (None, outcome)

    def use(self, name, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        object = self.entities.get_proximal_entity(name, subject)
        if not object:
            return (None, "Cannot be found or does not exist")
        elif not object.usable:
            return (None, "Cannot be used")
        else:
            object.usable = False
            return (f"{object.use}", "")

    def exit(self):
        exit()

    def loadgame(self):
        self.entities.load_entities("data/save")
        return(None, '')

    def savegame(self):
        for entity in self.entities():
            entity.description_long = entity.description_long.split('\n')
            entity.dialogue = entity.dialogue.split('\n')
            with open(f"data/save/{entity.name}.json", "w") as file:
                file.write(entity.to_json())
        return(None, '')

    def inventory(self):
        status = "status_effect"
        return (None,
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
            return (None, "Cannot be found or does not exist")
        elif not object.takeable:
            return (None, "Cannot be taken")
        else:
            subject.inventory.append(object.id)
            self.entities.get_global_entity(object.location).inventory.remove(object.id)
            object.location = subject.id
            return (f"{object.take}", f"You take {object.name}")

    def drop(self, name=None, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        object = self.entities.get_inventory_entity(name, subject)
        drop_location = subject.location
        if not name:
            return (None, "Need something to drop")
        elif not object:
            return (None, "Cannot be found or does not exist.")
        else:
            subject.inventory.remove(object.id)
            object.location = subject.location
            self.entities.get_global_entity(drop_location).inventory.append(object.id)
            return (None, f"{object.name} dropped by {subject.name}.")

    def look(self, name=None):
        response = ""
        if name:
            for entity in self.entities.get_surroundings(self.entities.player):
                if entity.name == name:
                    response += f'{entity.description_long}'
            for entity in self.entities.get_inventory(self.entities.player):
                if entity.name == name:
                    response += f'{entity.description_long}'
        else:
            location = self.entities.entity(self.entities.player.location)
            response += f'{location.description_long}\n'
            response += f'{self.contains(location.id)}'
        return (None, response)

    def contains(self, object):
        response = ""
        object = self.entities.entity(object)
        if not object:
            response += "Cannot be found or does not exist.\n"
        if object.name == "open_field" or object.name == "credits":
            return response
        else:
            response += f"\n{object.name} contains: "
            response += ", ".join([entity.name for entity in self.entities.get_inventory(object)])
        return response

    def walk(self, name):
        self.go(name)

    def sneak(self, subject=None):
        subject = self.entities.player if subject is None else self.entities.entity(subject)
        stealth = self.entities.entity('stealth')
        if stealth.id in subject.inventory:
            subject.inventory.remove(stealth.id)
            return (None, f'{subject.name} emerges from the shadows')
        else:
            subject.inventory.append(stealth.id)
            return (None, f'{subject.name} slips into the shadows')

    def _move(self, object, subject):
        self.entities.entity(subject.location).inventory.remove(subject.id)
        subject.location = object.id
        object.inventory.append(subject.id)

    def go(self, name, subject=None):
        lines = ""
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        door = self.entities.get_local_entity(name, self.entities.player)
        if not door:
            return (None, "Cannot be found or does not exist")
        elif not door.destination:
            return (None, "This does not appear to be traversable")
        elif (
                door.unlocked_by and door.unlocked_by not in self.entities.player.inventory and door.go_interrupt
        ):
            return (door.go_interrupt, "")
        elif (
                door.unlocked_by and door.unlocked_by not in self.entities.player.inventory
        ):
            return (None,
                "You are missing something in your inventory required to traverse through this"
            )
        destination = self.entities.entity(door.destination)
        self._move(destination, subject)
        if destination.name != "barricaded_door" and destination.name != "credits":
            lines += f"You traverse {door.name} and arrive at {destination.name}\n"
        if destination.discovered:
            lines += f"{destination.description_short}\n"
        else:
            lines += f"{destination.description_long}\n"
        destination.discovered = True
        lines += self.contains(destination.id)
        return (None, lines)

    def _cardinal(self, direction, subject=None):
        subject = (
            self.entities.player if subject is None else self.entities.entity(subject)
        )
        location = self.entities.entity(subject.location)
        direction = getattr(location, direction)
        if direction:
            return self.go(direction)
        else:
            return (None, "impassable")

    def north(self):
        return self._cardinal("north")

    def south(self):
        return self._cardinal("south")

    def east(self):
        return self._cardinal("east")

    def west(self):
        return self._cardinal("west")

    def help(self):
        return (None, f"possible actions include: {self.actions}")
