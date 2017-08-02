import uuid
import json
import logging
from time import time
from python_digits import DigitWord
from .GameObject import GameObject


class Game(object):
    """Game is a class cowbull game where the objective is to guess a sequence of numbers. The
    numbers are randomly generated and the user is given a number of turns to guess the numbers.

    The game is started by instantiating a game object, g = Game(), and then calling the new
    game method, g.new_game(). If you run this in the console, you will notice that it returns
    the complete game object (including the answer) - that's because the Game object is
    intended to be connected (or interfaced) to a user interface.

    A game object is a JSON structure as follows:

    {
        "key": {"type": "string"},
        "status": {"type": "string"},
        "ttl": {"type": "integer"},
        "answer": {
            "type": "array",
            "items":
                {
                    "digit":
                        {
                            "type": "integer",
                            "minimum": 0
                        }
                }
        },
        "mode": {"type": "string"},
        "guesses_remaining": {"type": "integer"},
        "guesses_made": {"type": "integer"}
    }

    """
    _g = None   # _g The global game variable
    go = GameObject # The GameObject to be used.

    def __init__(self, game_object=None):
        if game_object is not None:
            logging.debug("Game: GameObject passed so inheritance being used")
            self.go = game_object

    @property
    def digits_required(self):
        return self._g.digits_used[self._g.mode]

    @property
    def guesses_allowed(self):
        return self._g.guesses_allowed[self._g.mode]

    @property
    def key(self):
        return self._g.key

    def new_game(self, mode=None):
        """
        new_game() creates a new game. At version 0.3, the game is set to normal and this
        will be updated later. The new_game instantiates the object and then allows a number
        of tries to be made to guess the digits (see guess()).

        :return: JSON String containing the game object.

        """
        if not mode:
            _mode = "normal"
        else:
            _mode = mode

        # Validate game mode
        if _mode not in self.go.game_modes:
            raise ValueError('The mode passed ({}) is not supported.'.format(_mode))

        logging.debug("new_game called.")
        dw = DigitWord()

        dw.random(self.go.digits_used[_mode])
        logging.debug("Randomized DigitWord. Value is {}.".format(dw.word))

        self._g = self.go()
        _game = {
            "key": str(uuid.uuid4()),
            "status": "playing",
            "ttl": int(time()) + 3600,
            "answer": dw.word,
            "mode": _mode,
            "guesses_remaining": self.go.guesses_allowed[_mode],
            "guesses_made": 0
        }
        logging.debug("Game being created: {}".format(_game))

        self._g.from_json(jsonstr=json.dumps(_game))
        return self._g.to_json()

    def load_game(self, jsonstr):
        """
        load_game() takes a JSON string representing a game object and calls the underlying
        game object (_g) to load the JSON. The underlying object will handle schema validation
        and transformation.

        :param jsonstr: A valid JSON string representing a GameObject (see above)

        :return: None

        """
        logging.debug("load_game called.")
        logging.debug("Creating empty GameObject.")
        self._g = self.go()

        logging.debug("Calling from_json with {}.".format(jsonstr))
        self._g.from_json(jsonstr=jsonstr)

    def save_game(self):
        """
        save_game() asks the underlying game object (_g) to dump the contents of
        itself as JSON and then returns the JSON to

        :return: A JSON representation of the game object

        """
        logging.debug("save_game called.")
        logging.debug("Validating game object")
        self._validate_game_object(op="save_game")

        logging.debug("Dumping JSON from GameObject")
        return self._g.to_json()

    def guess(self, *args):
        """
        guess() allows a guess to be made. Before the guess is made, the method
        checks to see if the game has been won, lost, or there are no tries
        remaining. It then creates a return object stating the number of bulls
        (direct matches), cows (indirect matches), an analysis of the guess (a
        list of analysis objects), and a status.

        :param args: any number of integers (or string representations of integers)
        to the number of Digits in the answer; i.e. in normal mode, there would be
        a DigitWord to guess of 4 digits, so guess would expect guess(1, 2, 3, 4)
        and a shorter (guess(1, 2)) or longer (guess(1, 2, 3, 4, 5)) sequence will
        raise an exception.

        :return: a JSON object containing the analysis of the guess:

        {
            "cows": {"type": "integer"},
            "bulls": {"type": "integer"},
            "analysis": {"type": "array of DigitWordAnalysis"},
            "status": {"type": "string"}
        }

        """
        logging.debug("guess called.")
        logging.debug("Validating game object")
        self._validate_game_object(op="guess")

        logging.debug("Building return object")
        _return_results = {
            "cows": None,
            "bulls": None,
            "analysis": [],
            "status": ""
        }

        logging.debug("Check if game already won, lost, or too many tries.")
        if self._g.status.lower() == "won":
            _return_results["message"] = self._start_again("You already won!")
        elif self._g.status.lower() == "lost":
            _return_results["message"] = self._start_again("You have made too many guesses, you lost!")
        elif self._g.guesses_remaining < 1:
            _return_results["message"] = self._start_again("You have run out of tries, sorry!")
        elif self._g.ttl < time():
            _return_results["message"] = self._start_again("Sorry, you ran out of time to complete the puzzle!")
        else:
            logging.debug("Creating a DigitWord for the guess.")
            guess = DigitWord(*args)

            logging.debug("Validating guess.")
            self._g.guesses_remaining -= 1
            self._g.guesses_made += 1

            logging.debug("Initializing return object.")
            _return_results["analysis"] = []
            _return_results["cows"] = 0
            _return_results["bulls"] = 0

            logging.debug("Asking the underlying GameObject to compare itself to the guess.")
            for i in self._g.answer.compare(guess):
                logging.debug("Iteration of guesses. Processing guess {}".format(i.index))

                if i.match is True:
                    logging.debug("Bull found. +1")
                    _return_results["bulls"] += 1
                elif i.in_word is True:
                    logging.debug("Cow found. +1")
                    _return_results["cows"] += 1

                logging.debug("Add analysis to return object")
                _return_results["analysis"].append(i.get_object())

            logging.debug("Checking if game won or lost.")
            if _return_results["bulls"] == len(self._g.answer.word):
                logging.debug("Game was won.")
                self._g.status = "won"
                self._g.guesses_remaining = 0
                _return_results["message"] = "Well done! You won the game with your " \
                                             "answers {}".format(self._get_text_answer())
            elif self._g.guesses_remaining < 1:
                logging.debug("Game was lost.")
                self._g.status = "lost"
                _return_results["message"] = "Sorry, you lost! The correct answer was " \
                                             "{}".format(self._get_text_answer())
            _return_results["status"] = self._g.status

        logging.debug("Returning results.")
        return _return_results

    def _start_again(self, message=None):
        """Simple method to form a start again message and give the answer in readable form."""
        logging.debug("Start again message delivered: {}".format(message))
        the_answer = self._get_text_answer()

        return "{0} The correct answer was {1}. Please start a new game.".format(
            message,
            the_answer
        )

    def _get_text_answer(self):
        return ', '.join([str(i) for i in self._g.answer.word])

    def _validate_game_object(self, op="unknown"):
        """
        A helper method to provide validation of the game object (_g) in one place. If the
        game object does not exist or if (for any reason) the object is not a GameObject,
        then an exception will be raised.

        :param op: A string describing the operation (e.g. guess, save, etc.) taking place
        :return: Nothing
        """
        if self._g is None:
            raise ValueError(
                "Game must be instantiated properly before using - call new_game() "
                "or load_game(jsonstr='{...}')"
            )
        if not isinstance(self._g, GameObject):
            raise TypeError(
                "Unexpected error during {0}! GameObject (_g) is not a GameObject!".format(op)
            )
