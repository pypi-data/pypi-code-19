from timeit import default_timer

from pandas import DataFrame


class MyTimer:
    """
    A custom timer class
    """

    start_time = 0
    break_n = 0
    break_time = 0
    time_data = DataFrame(columns=['overall_time', 'block_time', 'break_text'])

    def __init__(self):
        pass

    def start(self):
        self.start_time = default_timer()
        self.break_time = default_timer()
        self.time_data.loc[self.break_n, 'overall_time'] = default_timer() - self.start_time
        self.time_data.loc[self.break_n, 'block_time'] = default_timer() - self.break_time
        self.time_data.loc[self.break_n, 'break_text'] = "Timer start"

    def break_point(self, text="None"):
        self.break_n += 1

        self.time_data.loc[self.break_n, 'overall_time'] = default_timer() - self.start_time
        self.time_data.loc[self.break_n, 'block_time'] = default_timer() - self.break_time
        self.time_data.loc[self.break_n, 'break_text'] = text
        self.break_time = default_timer()

        print("")
        print("-------------------------------------------------------------------------------------------")
        print("{}: Block {} took {} seconds.".format(self.break_n, self.time_data.loc[self.break_n, 'break_text'],
                                                     self.time_data.loc[self.break_n, 'block_time']))
        print("")
        print("{} seconds have elapsed overall".format(self.time_data.loc[self.break_n, 'overall_time']))
        print("-------------------------------------------------------------------------------------------")
        print("")
