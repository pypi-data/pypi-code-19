# vamos a crear una excepion que sera empaquetada
#vamos a manejar errores de tipo entero
class TinyIntError(Exception):#para usar la clase como una excepcion 
    def __init__(self):
        self.menssage = 'No es un numero tinyint'

    def __str__(self):
        return self.menssage
