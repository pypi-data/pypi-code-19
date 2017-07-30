import re
from itertools import product
from typing import (
    Dict,
    Tuple,
)

from .. import Workaround


class BaseHandler:
    adjectives = set()
    value_patterns = []  # Iterable[Union[Pattern, str]]

    example_values = []  # Iterable[str]

    @classmethod
    def examples(cls):
        return list(product(cls.example_values, cls.adjectives))

    @classmethod
    def is_result_equal(cls, result, adjective):
        return result == adjective

    def can_handle(self, value, adjective):
        return self.can_handle_adjective(adjective) and self.can_handle_value(value)

    def can_handle_adjective(self, adjective):
        return adjective in self.adjectives

    def can_handle_value(self, value):
        return any(re.match(pattern, value) for pattern in self.value_patterns)

    def handle(self, workaround: Workaround) -> Tuple[bool, str]:
        parsed_value = self.extract_info_from_value(workaround.value)
        result = self.get_result(workaround, parsed_value)
        return self.is_result_equal(result, workaround.adjective), result

    def extract_info_from_value(self, value) -> Dict[str, str]:
        for pattern in self.value_patterns:
            match = re.match(pattern, value)

            if match:
                return match.groupdict()

    def get_result(self, workaround: Workaround, parsed_value: Dict[str, str]) -> str:
        raise NotImplementedError('Handlers need to implement the get_result method.')
