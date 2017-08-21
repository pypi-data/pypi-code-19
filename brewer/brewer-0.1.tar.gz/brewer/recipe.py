from controller import Controller
from settings import db_file
import sqlite3

conn = sqlite3.connect(db_file)

class Recipe():
    def __init__(self, vars):
        self.controller = Controller()
        self.vars = self._all_to_float(vars)

    def load_selected_recipe(self):
        sqlite.execute("SELECT * FROM recipe where selected = 1")

    def store(self):
        pass

    def _all_to_float(self, vars_dict):
        for key, value in vars_dict.iteritems():
            if not key == "name":
                vars_dict[key] = float(value)
        return vars_dict

