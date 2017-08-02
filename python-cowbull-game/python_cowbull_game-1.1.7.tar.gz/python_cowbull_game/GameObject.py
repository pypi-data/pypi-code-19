import json
from python_digits import DigitWord
from jsonschema import validate


class GameObject(object):
    _key = None
    _status = None
    _ttl = None
    _answer = None
    _mode = None
    _guesses_remaining = None
    _guesses_made = None
    _last_guess = None

    game_modes = ["easy", "normal", "hard", "hex"]
    game_states = ["won", "lost", "playing"]

    schema = {
        "type": "object",
        "properties":
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
    }

    digits_used = {
        'easy': 3,
        'normal': 4,
        'hard': 6,
        'hex': 4
    }

    guesses_allowed = {
        'easy': 15,
        'normal': 10,
        'hard': 6,
        'hex': 10
    }

    def __init__(self):
        self._key = None
        self._status = None
        self._ttl = None
        self._answer = None
        self._mode = None
        self._guesses_remaining = None
        self._guesses_made = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if value is None:
            raise ValueError("Key CANNOT be None")
        self._key = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value.lower() not in self.game_states:
            raise ValueError("Status can only be one of: {}".format(self.game_states))
        self._status = value

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        error_text = "TTL must be a positive integer (>0) representing the number of " \
                     "seconds from the epoch (time.time()) when the game " \
                     "object expires!"

        if not isinstance(value, int):
            raise TypeError(error_text)
        if value < 1:
            raise ValueError(error_text)

        self._ttl = value

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value):
        if not isinstance(value, DigitWord):
            raise TypeError("Answer must be a DigitWord")
        self._answer = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in self.game_modes:
            raise ValueError("Mode must be one of : {}".format(self.game_modes))
        self._mode = value

    @property
    def guesses_remaining(self):
        return self._guesses_remaining

    @guesses_remaining.setter
    def guesses_remaining(self, value):
        error_text = "Guesses remaining must be a positive integer (>=0) representing the number of " \
                     "guesses left."
        if not isinstance(value, int):
            raise TypeError(error_text)
        if value < 0:
            raise ValueError(error_text)
        self._guesses_remaining = value

    @property
    def guesses_made(self):
        return self._guesses_made

    @guesses_made.setter
    def guesses_made(self, value):
        error_text = "Guesses made must be a positive integer (>=0) representing the number of " \
                     "guesses made."
        if not isinstance(value, int):
            raise TypeError(error_text)
        if value < 0:
            raise ValueError(error_text)
        self._guesses_made = value

    def to_json(self):
        if self._key is None:
            return_object = {}
        else:
            return_object = \
                {
                    "key": self._key,
                    "status": self._status,
                    "ttl": self._ttl,
                    "answer": self._answer.word,
                    "mode": self._mode,
                    "guesses_remaining": self._guesses_remaining,
                    "guesses_made": self._guesses_made
                }

        return json.dumps(return_object)

    def from_json(self, jsonstr):
        if not isinstance(jsonstr, str):
            raise TypeError("Load requires a valid JSON string")
        _temp_dict = json.loads(jsonstr)

        if _temp_dict == {}:
            self._key = None
            return

        # Validate the dictionary object against the schema
        validate(_temp_dict, self.schema)

        self.key = _temp_dict["key"]
        self.status = _temp_dict["status"]
        self.ttl = _temp_dict["ttl"]

        self.mode = _temp_dict["mode"]

        # Create a DigitWord based on the array of integers passed in the JSON
        if self.mode.lower() == 'hex':
            _wordtype = DigitWord.HEXDIGIT
        else:
            _wordtype = DigitWord.DIGIT
        self.answer = DigitWord(*_temp_dict["answer"], wordtype=_wordtype)

        self.guesses_remaining = _temp_dict["guesses_remaining"]
        self.guesses_made = _temp_dict["guesses_made"]
