import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiBadRequestError

def decide_from_row(tree, columns, row):
  time = Time(
    t=row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
    timezone=row.name.tz
  )
  context = {
    col: row[col] for col in columns if pd.notnull(row[col])
  }
  decision = VanillaInterpreter.decide(tree, [context, time])

  keys, values = zip(*[
    (output + '_' + key, value)
    for output, output_decision in decision["output"].items()
    for key, value in output_decision.items()
  ])

  return pd.Series(data=values, index=keys)

class Interpreter(VanillaInterpreter):
  @staticmethod
  def decide(tree, args):
    if len(args) == 1 and isinstance(args[0], pd.DataFrame):
      df = args[0]
      if not isinstance(df.index, pd.DatetimeIndex):
        raise CraftAiBadRequestError("Invalid dataframe given, it is not time indexed")

      return df.apply(lambda row: decide_from_row(tree, df.columns, row), axis=1)

    else:
      return VanillaInterpreter.decide(tree, args)
