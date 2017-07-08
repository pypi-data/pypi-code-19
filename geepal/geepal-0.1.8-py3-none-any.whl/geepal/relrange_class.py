from enum import Enum


def main():
    d_text = 'day'
    m = SelectPeriod.parse(d_text)

    print("You chose: {}".format(m))

    Today = AddTense("Last")
    Today.conjugate(m)


class SelectPeriod(Enum):
    Day = 1
    Week = 2
    Month = 3
    Year = 4

    @staticmethod
    def parse(text: str):
        if not text:
            return None

        text = text.strip().lower()
        parse_dict = {
            'day': SelectPeriod.Day,
            'week': SelectPeriod.Week,
            'month': SelectPeriod.Month,
            'year': SelectPeriod.Year,
        }
        return parse_dict.get(text)


class AddTense:
    def __init__(self, name):
        self.name = name

    def conjugate(self, direction: SelectPeriod):
        action_dict = {
            SelectPeriod.Day: lambda: print("RelativePeriod is: {}".format(self.name)),
        }

        action = action_dict.get(
            direction,
            lambda: print("{} moves quickly to {}".format(self.name, direction)))
        action()


if __name__ == '__main__':
    main()
