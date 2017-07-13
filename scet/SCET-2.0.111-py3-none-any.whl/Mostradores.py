#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.bd_xml import Tabla
from scet import libsa
from scet.globales import *


log = logging.getLogger(__name__)


class Mostrador_Estandar(libsa.Ventana):
    """Un Mostrador es una interfaz simple que muestra información,
    sin la posibilidad de entrar o cambiar informacion"""

    archivo_gui = None
    nombre_tabla = ''

    def __init__(self, master):
        self.master = master
        self.bd = Tabla(self.nombre_tabla)
        libsa.Ventana.__init__(self, self.master, self.archivo_gui)
