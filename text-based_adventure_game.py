import shutil
from dataclasses import dataclass, field
from action import Action
from parsley import Parsley
from entities import Entities
import os


@dataclass
class Game:
    action: Action = field(default_factory=lambda: Action())
    parsley: Parsley = field(default_factory=lambda: Parsley())
    logger = None
    location = ""
    description = "Enter a command... "
    previous_action = "look"

    def __post_init__(self):
        self.location = self.action.entities.entity(self.action.entities.player.location).name

    def loop(self):
        start = False
        while True:
            os.system('cls')
            build_output(self, self.location)
            if not start:
                print("Previous action: ", self.previous_action)
                print(self.action.look())
                start = True
            else:
                print("Previous action: ", self.previous_action)
            user_input = input(": ")
            response = self.parsley.parse_input(iter(user_input.split()), None)
            if response:
                self.description = response[0]
            previous_action = user_input
            self.previous_action = user_input
            next_input = input("Press 'enter' to continue...")
            if next_input == '':
                continue
            else:
                continue

            #response = self.parsley.parse_input(iter(input("> ").split()), None)
            while response:
                response = self.parsley.parse_input(iter(response.split()), None)


def build_output(user, location):
    divider = build_divider()
    print(divider)
    print("Text-Based Adventure Game".center(len(divider)))
    print(divider)
    print(f'Location: {user.location.upper()}'.center(len(divider)))
    print(divider)
    #print(shutil.get_terminal_size().columns)
    build_ascii_art(location)
    print(divider)
    print(user.description)
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
    with open(f'art/{location}.txt', 'r') as f:
        for line in f:
            print(line.rstrip())


entities = Entities()
parsley = Parsley()
action = Action(entities)
game = Game(action, parsley)
game.action.look()
game.loop()
