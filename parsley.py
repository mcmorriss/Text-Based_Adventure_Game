from action import Action
from dataclasses import dataclass, field
from functools import partialmethod
import inspect


@dataclass
class Parsley:
    action: Action = field(default_factory=lambda: Action())

    def parse_input(self, input, action):
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
                return action.__get__(self.action, Action)()
            except Exception as e:
                print(e)
                print("I'm sorry; I'm not sure what you mean.")
        # if the next word is the name of an action
        # pass that action as an argument to our current action
        elif next_word in self.action.actions:
            return self.parse_input(
                input,
                partialmethod(getattr(Action, next_word))
                if action is None
                else action(next_word),
            )
        # if the next word is the name of an entity
        # pass that entity as an argument to our action
        elif next_word in self.action.entities.names():
            return self.parse_input(input, partialmethod(action, next_word))
        else:
            return self.parse_input(input, action)
