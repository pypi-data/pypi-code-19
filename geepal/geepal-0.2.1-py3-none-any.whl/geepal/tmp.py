#from enum import enum


def main():
    """ """

    members = ['day', 'week', 'month', 'year']
    for member in members:
        stuff = RelativeTimePeriod.parse(member)
        print(stuff)

class RelativeTimePeriod():#enum):
    """ """

    Day = 'day'
    Week = 'week'
    Month = 'month'
    Year = 'year'

    @staticmethod
    def parse(text: str):
        if not text:
            return None

        text = text.strip().lower()
        relrange_dict = {
                    'day': RelativeTimePeriod.Day,
                    'week': RelativeTimePeriod.Week,
                    'month': RelativeTimePeriod.Month,
                    'year': RelativeTimePeriod.Year,
                    }
        return relrange_dict.get(text)

    def __iter__(self): # Add iteration method for class
        for i in sorted(self.items, key=lambda i: i)

if __name__ == '__main__':
    main()
