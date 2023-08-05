from dataclasses import dataclass, field
from action import Action
from parsley import Parsley
from entities import Entities


@dataclass
class Game:
    action: Action = field(default_factory=lambda: Action())
    parsley: Parsley = field(default_factory=lambda: Parsley())
    logger = None

    def loop(self):
        while True:
            response = self.parsley.parse_input(iter(input("> ").split()), None)
            while response:
                response = self.parsley.parse_input(iter(response.split()), None)


entities = Entities()
parsley = Parsley()
action = Action(entities)
game = Game(action, parsley)
game.action.look()
game.loop()
