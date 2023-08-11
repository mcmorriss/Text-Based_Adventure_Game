from collections import deque
import shutil
from dataclasses import dataclass, field
from action import Action
from parsley import Parsley
from entities import Entities
import sys


@dataclass
class Game:
    parsley: Parsley = field(default_factory=lambda: Parsley())
    logger = None
    location = deque(['Square', 'Square'], 2)
    description = "Enter a command... "
    previous_action = "look"

    def loop(self):
        start = False
        build_output(self, self.location)
        while True:
            if not start:
                print("Previous action: ", self.previous_action)
                print(self.parsley.action.look()[1])
                start = True
            else:
                print("Previous action: ", self.previous_action)
            user_input = input("> ")
            reaction, response = self.parsley.parse_input(iter(user_input.split()), None)
            while reaction:
                reaction, followup = self.parsley.parse_input(iter(reaction.split()), None)
                response += f"\n{followup}"
            self.location.append(self.parsley.action.entities.entity(self.parsley.action.entities.player.location).name)
            self.previous_action = user_input
            if self.location[0] != self.location[1]:
                build_output(self, self.location)
            print(response)

def build_output(user, location):
    divider = build_divider()
    print(divider)
    print("Text-Based Adventure Game".center(len(divider)))
    print(divider)
    print(f'Location: {user.location[1].upper()}'.center(len(divider)))
    print(divider)
    build_ascii_art(location)
    print(divider)
    print(divider)


def build_divider():
    terminal_width = shutil.get_terminal_size().columns
    width = 125
    divider = "+"
    for i in range(width):
        divider += "—"
    divider += "+"
    return divider


def build_ascii_art(location='square'):
    try:
        with open(f'art/{location[1]}.txt', 'r') as f:
            for line in f:
                print(line.rstrip())
    except:
        pass


entities = Entities()
parsley = Parsley()
action = Action(entities)
game = Game(parsley)
game.loop()
