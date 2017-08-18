def validate_tiny_int(val):
    return val >= 0 and val <= 255

def validate_val(val):
    try:
      return isinstance(int(val),int)#aca valida si es una instancia de la clase int
                             #en python todo es un objeto
                             #se intenta convertir un string a entero con int(val)
    except ValueError as error:
      return False 