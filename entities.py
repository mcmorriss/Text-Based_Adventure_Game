from dataclasses import dataclass, field
import inspect
import os
from entity import Entity


@dataclass
class Entities:
    player: Entity = field(default_factory=lambda: Entity())
    parser: Entity = field(default_factory=lambda: Entity())
    entities: dict[str, Entity] = field(default_factory=lambda: {})
    words: dict[str, Entity] = field(default_factory=lambda: {})

    def __call__(self):
        return self.entities.values()
    
    def names(self):
        return [entity.name for entity in self.entities.values()]
    
    def entity(self, identifier):
        """Attempts to get the entity associated with the identifier
        the identifier can be the id or a name"""
        try:
            return self.entities[identifier]
        except:
            for entity in self.entities:
                if entity.name == identifier:
                    return entity
                
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
    
    def get_surroundings(self, entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.location].inventory]
    
    def get_level(self, level_type):
        level = 0
        if level_type == "combat" or level_type == "combat_level":
            level = self.player.combat_level
            print(
                f"Your combat level is {level}"
            )
        if level_type == "looting" or level_type == "looting_level":
            level = self.player.loot_level
            print(
                f"Your combat level is {level}"
            )
        else:
            print(
                f"'{level_type}' is not a valid entry. Please enter 'combat' or 'looting'"
            )

    def set_exp_level(self, exp_type):
        """ Leveling system called by functions that allow players to do actions associated with the 3 skills"""
        exp = self.player.combat_experience
        level = 0
        if exp_type == "combat_level":
            exp = self.player.combat_experience
            level = self.player.combat_level
        if exp_type == "loot_level":
            exp = self.player.loot_experience
            level = self.player.loot_level
        # Can add the other leveling feature when base action is implemented

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

    def load_entities(self, directory):
        for root, _, files in os.walk(directory):
            root = os.path.join(root).replace("\\", "/")
            base = os.path.basename(root)
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as data:
                        match base:
                            case "words":
                                entity = Entity.from_json(data.read())
                                self.words[entity.name] = entity
                            case _:
                                entity = Entity.from_json(data.read())
                                self.entities[entity.id] = entity
                        if entity.name == "you":
                            self.player = entity
                        if entity.name == "parser":
                            self.parser = entity