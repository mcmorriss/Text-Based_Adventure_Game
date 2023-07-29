from action import Action
from dataclasses import dataclass, field

@dataclass
class Parsley():
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
                action()
            except Exception as e:
                print(e)
                print("I'm sorry; I'm not sure what you mean.")
        # if the next word is an action
        # pass that word as an argument to our current action
        elif next_word in self.action.actions:
            self.parse_input(
                input,
                getattr(self.action, next_word)
                if action is None
                else lambda: action(next_word),
            )
        # if the next word is a name of an entity in the player's inventory
        # pass that entity as an argument to our action
        elif next_word in self.action.entities.names():
            self.parse_input(input, lambda: action(next_word))
        else:
            self.parse_input(input, action)
