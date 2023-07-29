from dataclasses import dataclass, field
from action import Action
from parsley import Parsley
from entities import Entities


@dataclass
class Game:
    action: Action = field(default_factory=lambda: Action())
    parsley: Parsley = field(default_factory=lambda: Parsley())

    def loop(self):
        while True:
            self.parsley.parse_input(
                iter(input(": ").split()), None
            )

entities = Entities()
action = Action(entities)
parsley = Parsley(action)
game = Game(action, parsley)
game.action.look()
game.loop()
