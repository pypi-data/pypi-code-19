def fct_other(f, keep, drop, other_level = 'Other'):
	f = f.apply(lambda row: row if row in drop else other_level)
	return f

def fct_collapse(f, groups):
    for key in groups:
        print(key)
        f = f.apply(lambda row: key if row in groups[key] else row)
    return f
import pandas as pd
