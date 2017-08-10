from enum import Enum
import json, re

class Measurement(Enum):
  CUP = 'cup',
  TEASPOON = 'teaspoon',
  TABLESPOON = 'tablespoon',
  FLUID_OUNCE = 'fluid_ounce',
  OUNCE = 'ounce',
  CLOVE = 'clove',
  PINCH = 'pinch',
  LITER = 'liter',
  MILLILITER = 'milliliter',
  GALLON = 'gallon',
  QUART = 'quart',
  KILOGRAM = 'kilogram',
  GRAM = 'gram',
  POUND = 'pound',
  DASH = 'dash',
  PINT = 'pint'

with open('./conversions.json') as f:
  conversions = json.load(f)

def convert(amount, fromMeasurement, toMeasurement):
  normalized_from = __normalizeMeasurement(fromMeasurement)
  normalized_to = __normalizeMeasurement(toMeasurement)

  if __isValidConversion(normalized_from, normalized_to):
    return __convert(amount, normalized_from.value[0], normalized_to.value[0])
  else:
    return 0.0

def __normalizeMeasurement(measurement):
  singular = re.sub(r's$', '', measurement).upper()
  if singular in Measurement.__members__:
    return Measurement[singular]
  else:
    raise Exception('{} isn\'t a measurement'.format(measurement))

def __convert(amount, fromMeasurement, toMeasurement):
  measurement_conversion = conversions[toMeasurement]

  return amount * measurement_conversion[fromMeasurement]

def __isValidConversion (fromMeasurement, toMeasurement):
  if fromMeasurement in [ Measurement.TEASPOON, Measurement.TABLESPOON, Measurement.CUP, Measurement.FLUID_OUNCE, Measurement.PINCH, Measurement.DASH, Measurement.CLOVE ]:
      return [ Measurement.TEASPOON, Measurement.TABLESPOON, Measurement.CUP, Measurement.FLUID_OUNCE, Measurement.PINCH, Measurement.DASH, Measurement.CLOVE ].index(toMeasurement) > -1

  if fromMeasurement in [ Measurement.GRAM, Measurement.KILOGRAM, Measurement.OUNCE, Measurement.POUND ]:
      return [ Measurement.GRAM, Measurement.KILOGRAM, Measurement.OUNCE, Measurement.POUND ].index(toMeasurement) > -1

  if fromMeasurement in [ Measurement.GALLON, Measurement.MILLILITER, Measurement.LITER, Measurement.PINT, Measurement.QUART ]:
    return [ Measurement.TEASPOON, Measurement.TABLESPOON, Measurement.CUP, Measurement.FLUID_OUNCE, Measurement.GALLON, Measurement.MILLILITER, Measurement.LITER, Measurement.PINT, Measurement.QUART ].index(fromMeasurement) > -1

  return False
