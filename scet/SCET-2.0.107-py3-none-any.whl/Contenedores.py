#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.libsa import Ventana, Base_Entrada, Formulario, Bucle, Tabla
from scet.libsa import transaccion, ejecutar, seguro
from scet import Formularios
from scet import Plantillas
from scet import Tablas
from scet import Mostradores
from scet.globales import *


log = logging.getLogger(__name__)


class Tabla_Busqueda(Ventana):
    archivo_gui = 'C_Tabla_Busqueda'

    def __init__(self, master, objeto_tabla, archivo_gui=None, **funciones):
        self.master = master
        self.objeto_tabla = objeto_tabla
        self.archivo_gui = archivo_gui if archivo_gui else self.archivo_gui
        Ventana.__init__(self, self.master, self.archivo_gui)
        funciones.update({'buscar':self.buscar})
        self.gui.connect_callbacks(funciones)
        # Crear campos busquedas
        self.marco = self.gui.get_object('__marco__') if self.master else None
        self.arbol = self.objeto_tabla(self.marco, OBTENER_BD())
        self.gui.create_variable('_tipo_nombre').set(self.arbol.arbol['displaycolumns'][0])
        self.gui.create_variable('_tipo_referencia').set(self.arbol.arbol['displaycolumns'][1])
        self.gui.create_variable('nombre').trace('w', self.buscar)
        self.gui.create_variable('referencia').trace('w', self.buscar)
        self.gui.create_variable('cliente').trace('w', self.buscar)
        self.gui.create_variable('codigo').trace('w', self.buscar)
        self.gui.create_variable('equipo').trace('w', self.buscar)
        self.gui.create_variable('serial').trace('w', self.buscar)

    def buscar(self, event=None, *arg):
        self._buscar()
        self.arbol.actualisar_arbol()

    @seguro
    @transaccion
    def _buscar(self, evento=None):
        self.arbol.condicion = self.datos
        log.debug('Tabla busqueda {}: {}'.format(
            self.objeto_tabla,
            self.arbol.condicion))
        self.arbol.actualisar_tabla()

    #callbacks
    def clienteNuevo(self):
        None
