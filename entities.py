from dataclasses import dataclass, field
import os
from entity import Entity, EntityId, EntityName
import inspect


@dataclass
class Entities:
    player: Entity = field(default_factory=lambda: Entity())
    entities: dict[str, Entity] = field(default_factory=lambda: {})

    def __post_init__(self):
        self.load_entities("data/new")

    def __call__(self):
        return self.entities.values()

    def names(self):
        return [entity.name for entity in self.entities.values()]

    def entity(self, identifier: EntityId | EntityName | Entity):
        """Attempts to get the entity associated with the identifier
        the identifier can be the id or a name"""
        try:
            return self.entities[identifier]
        except:
            for entity in self.entities.values():
                if entity.name == identifier:
                    return entity
        return None

    def get_global_entity(self, identifier):
        """Attempts to get the entity associated with the identifier
        the identifier can be the id or a name"""
        try:
            return self.entities[identifier]
        except:
            for entity in self.entities:
                if entity.name == identifier:
                    return entity

    def get_local_entity(
        self, identifier: EntityName | EntityId, subject: Entity = None
    ) -> Entity | None:
        """Gets an entity by name or id from the subject's immediate surroundings"""
        subject = self.player if subject is None else subject
        by_name = next(
            (
                entity
                for entity in self.get_surroundings(subject)
                if entity.name == identifier
            ),
            None,
        )
        by_id = next(
            (
                entity
                for entity in self.get_surroundings(subject)
                if entity.id == identifier
            ),
            None,
        )
        return by_id if by_name is None else by_name

    def get_inventory_entity(
        self, identifier: EntityId | EntityName, subject: Entity = None
    ) -> Entity | None:
        """Gets an entity by name from the subject's inventory"""
        subject = self.player if subject is None else subject
        by_name = next(
            (
                entity
                for entity in self.get_inventory(subject)
                if entity.name == identifier
            ),
            None,
        )
        by_id = next(
            (
                entity
                for entity in self.get_inventory(subject)
                if entity.id == identifier
            ),
            None,
        )
        return by_id if by_name is None else by_name

    def get_proximal_entity(self, name, subject: Entity = None) -> Entity | None:
        """Gets an entity from the subject's inventory.
        If the entity is not in the subject's inventory gets
        the entity from the subject's location"""
        subject = self.player if subject is None else subject
        return (
            self.get_local_entity(name, subject)
            if self.get_inventory_entity(name, subject) is None
            else self.get_inventory_entity(name, subject)
        )

    def get_inventory(self, entity: Entity) -> list[Entity]:
        """returns a list of the player's inventory"""
        return [self.entities[id] for id in self.entities[entity.id].inventory]

    def get_surroundings(self, entity: Entity) -> list[Entity]:
        return [self.entities[id] for id in self.entities[entity.location].inventory]

    def get_level(self, level_type):
        level = 0
        if level_type == "combat" or level_type == "combat_level":
            level = self.player.combat_level
            print(f"Your combat level is {level}")
        if level_type == "looting" or level_type == "looting_level":
            level = self.player.loot_level
            print(f"Your looting level is {level}")
        else:
            print(
                f"'{level_type}' is not a valid entry. Please enter 'combat' or 'looting'"
            )

    def set_exp_level(self, exp_type, subject=None):
        """Leveling system called by functions that allow players to do actions associated with the 3 skills"""
        subject = self.player if subject is None else subject
        exp = 0
        level = 0
        # Combat
        if exp_type == "combat_level":
            subject.combat_experience += 1
            exp = subject.combat_experience
            if exp >= 1:
                subject.combat_level = 1
            if exp >= 4:
                subject.combat_level = 2
            if exp >= 7:
                subject.combat_level = 3
            level = subject.combat_level

        # Looting
        if exp_type == "loot_level":
            subject.loot_experience += 1
            exp = subject.loot_experience
            if exp >= 1:
                subject.loot_level = 1
            if exp >= 4:
                subject.loot_level = 2
            if exp >= 7:
                subject.loot_level = 3
            level = subject.loot_level

        # Can add the other leveling feature when base action is implemented
        # Check for level up.
        if exp == 1 or exp == 4 or exp == 7:
            print(f"{subject.name} {exp_type} is now level {level}!")
            if exp_type == "combat_level":
                print(f"{subject.name} now does {level}x damage!")

    def load_entities(self, directory):
        for root, _, files in os.walk(directory):
            root = os.path.join(root).replace("\\", "/")
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as data:
                        entity = Entity.from_json(data.read())
                        if (
                            inspect.currentframe().f_back.f_code.co_name != "loadgame"
                            and entity.id in self.entities.keys()
                        ):
                            print(
                                f"WARNING: entity id collision. {entity.name} shares an id with {self.entities[entity.id].name}"
                            )
                        self.entities[entity.id] = entity
                        if entity.name == "player":
                            self.player = entity
        self.dereference_entities()

    def dereference_entities(self):
        for entity in self.entities.values():
            entity.description_long = '\n'.join(entity.description_long)
            if not entity.location:
                continue
            else:
                self.entities[entity.location].inventory.append(entity.id)
