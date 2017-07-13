#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCET
Sistema de Control de Entradas de Taller,
por Wolfang Torres
"""

from scet.globales import *

import os
import logging
import time
import sys
import traceback
import time
import subprocess
import pip
import sqlite3
from tkinter import Tk, ttk, Toplevel, messagebox, filedialog
from os.path import join, abspath, dirname, basename, isfile

import pymysql

from scet.libsa import Ventana, Base_Entrada, Formulario, Bucle, Tabla,\
    Reporte, seguro, ControladorEstado, VentanaError
from scet.bd_xml import Tabla
from scet import Ventanas


log = logging.getLogger(__name__)


class inicio_seccion(Ventana, Base_Entrada):
    """Ventana de incio de seccion"""

    archivo_gui = "Inicio_seccion"
    dir = join(CARPETA_TRABAJO, 'BD_login.xml')

    def __init__(self, master):
        self.master = master
        self.master.wm_title(NOMBRE)
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.Activo = True
        self.gui.get_object('contraseña').focus()
        self.bd = Tabla()
        log.info('Pantalla de incio de sesion creada')
        try:
            log.info('Buscar archivo informacion comun')
            with open(self.dir, 'r') as preferencias:
                self.bd.xml = preferencias.read()
        except IOError as err:
            log.info('Archivo no encontrada, creando uno generico')
            self._crear_archivo_preferencias()
            with open(self.dir, 'w') as preferencias:
                preferencias.write(self.bd.xml)
        self._sincronisar('formulario', 0, self.bd, 'none_a_str')
        log.info('Preferencias escritas en el formulario')

    @seguro
    def aceptarServidor(self, event=None):
        """Aceptar entrar usando una coneccion a la base de datos MYSQL"""
        self.bd[0] = self.datos
        self.config = self.bd[0]
        #Configuraciones para MYSQL
        config  = self.config.copy()
        del config['file']
        config['port'] = int(config['port'])
        try:
            DEFINIR_BD(pymysql.connect(**config))
        except pymysql.err.MySQLError:
            pass
            print("Coneccion negada")
        else:
            log.info('Itento de coneccion al servidor de BD exitoso')
            # guardar preferencias
            self._guardar()
            # cerrar la ventana de login para continuar
            self.Activo = False
            self.master.destroy()

    @seguro
    def aceptarLocal(self, event=None):
        """Aceptar entrar usando una coneccion a la base de datos SQLite local"""
        if not isfile(ARCHIVO_SQLITE):
            crearBaseDatosSQLite()
        DEFINIR_BD(sqlite3.connect(ARCHIVO_SQLITE))
        log.info('Abrir archivo de BD exitoso')
        # guardar preferencias
        self._guardar()
        # cerrar la ventana de login para continuar
        self.Activo = False
        self.master.destroy()

    @seguro
    def selecionarArchivo(self):
        global ARCHIVO_SQLITE, NOMBRE_SQLITE
        ARCHIVO_SQLITE = filedialog.asksaveasfilename(
            confirmoverwrite = False,
            defaultextension = 'sqlite',
            filetypes = [('Base de Datos SQLite',('.sqlite')), ('Todos los archivos','*')],
            initialdir = CARPETA_TRABAJO,
            initialfile = NOMBRE_SQLITE,
            title = "Seleccionar Archivo de Base de Datos",
            )
        self.gui.create_variable('file').set(ARCHIVO_SQLITE)
        NOMBRE_SQLITE = basename(ARCHIVO_SQLITE)

    @seguro
    def resetearBD(self):
        r = messagebox.askyesno(
            message = '''Esta operación borrara TODOS los datos en la Base de Datos,
¿Esta seguro que desea continuar?''',
            icon = 'warning',
            default = 'no',
            title = 'Resetear',
        )
        if r:
            crearBaseDatosSQLite()

    @seguro
    def salir(self):
        self.master.destroy()

    @seguro
    def guardar(self):
        self._guardar()
        messagebox.showinfo(
            message='Guardado exitosamente',
            icon="info",
            title="guardado exitoso"
            )

    def _guardar(self):
        """guarda los datos de incio de seccion a un archivo de preferencias"""
        self._crear_archivo_preferencias()
        self.bd[0] = self.datos
        with open(self.dir, 'w') as preferencias:
            preferencias.write(self.bd.xml)

    def _crear_archivo_preferencias(self):
        """Crea un arhivo de preferencias"""
        self.bd = Tabla('Preferencias')
        self.bd.agregar_columna(campo='host', tipo='str', defecto='127.0.0.1')
        self.bd.agregar_columna(campo='port', tipo='str', defecto='3306')
        self.bd.agregar_columna(campo='user', tipo='str', defecto='')
        self.bd.agregar_columna(campo='password', tipo='str', defecto='')
        self.bd.agregar_columna(campo='db', tipo='str', defecto='scet')
        self.bd.agregar_columna(campo='file', tipo='str', defecto=ARCHIVO_SQLITE)
        self.bd += ()


class programa(Ventana):
    """Clase que representa al programa"""

    formulario = None
    _estilos = {
        'linux':'clam',
        'win32':'clam',
        }
    _fuente = ('Helvetica', 11)
    _fuente_titulo = _fuente + ('bold',)

    def __init__(self, master):
        self.master = master
        self.master.report_callback_exception = self.report_callback_exception
        master.wm_title(NOMBRE)
        Ventana.__init__(self, master, 'Main')
        self.marco = self.gui.get_object('__marco__')
        self._estilo()
        self._login()
        self._menu()

    def report_callback_exception(self, *args):
        VentanaError(args)

    @seguro
    def _login(self):
        """Crea la pantalla de incio de seccion"""
        self.master.withdraw()
        ventana = Toplevel(self.master)
        self.login = inicio_seccion(ventana)
        self.master.wait_window(ventana)
        if OBTENER_BD() is None:
            log.info('Pantalla de inicio de secion cerrada, cerrando programa')
            sys.exit(0)
        else:
            self.master.deiconify()

    @seguro
    def _estilo(self):
        """Modifica el estilo estandar de tkinter"""
        log.info('Creando estilo grafico')
        self.estilo = ttk.Style()
        log.info('Sistema operativo es {}'.format(sys.platform))
        for os, estilo in self._estilos.items():
            if os in sys.platform:
                log.info('Seleccionando estilo {}'.format(estilo))
                s = estilo
                break
        else:
            s = 'default'
            log.info('No se encontro un estilo para el OS, usando default')
        self.estilo.theme_use(s)
        #conf
        self.estilo.configure('.', font=self._fuente, background='white')
        self.estilo.configure('Subtitulo.TLabel', font=self._fuente_titulo)
        self.estilo.configure('TNotebook.Tab', font=self._fuente_titulo)
        self.estilo.configure('TButton', font=self._fuente_titulo)

    def _menu(self):
        """Crea las entradas del menu"""
        menu = self.gui.get_object('__menu_usuario__')
        # Menu
        entradaTaller = menu.insert('', 'end', text='Entrada a Taller', tags=('fila', 'a'))
        controlClientes = menu.insert('', 'end', text='Control de Clientes', tags=('fila', 'b'))
        controlRecursos = menu.insert('', 'end', text='Control de Recursos', tags=('fila', 'a'))
        controlEntradas = menu.insert('', 'end', text='Equipos en Taller', tags=('fila', 'b'))
        historialEntradas = menu.insert('', 'end', text='Historial de Trabajos', tags=('fila', 'a'))
        # Binds
        menu.tag_bind('fila', '<Double-Button-1>', self._selecionar_menu)
        menu.tag_bind('fila', '<Return>', self._selecionar_menu)
        menu.tag_configure('fila', font=self._fuente_titulo)
        menu.tag_configure('a', background='white')
        menu.tag_configure('b', background='gray')
        # Mapeo de menu y ventana
        self._mapeo_menu_formulario = {
            entradaTaller:Ventanas.Entrada_Taller,
            controlClientes:Ventanas.Control_Clientes,
            controlRecursos:Ventanas.Control_Recursos,
            controlEntradas:Ventanas.Control_Entradas,
            historialEntradas:Ventanas.Historial_Entradas,
        }

    def _selecionar_menu(self, evento):
        """Controla la seleccion del menu"""
        menu = evento.widget
        if not menu.selection():
            return None
        objeto = menu.selection()[0]
        if objeto in self._mapeo_menu_formulario:
            formulario = self._mapeo_menu_formulario[objeto]
        log.debug('Selecionando menu: {menu}, objeto: {objeto}, formulario: {formulario}'.format(**locals()))
        if self.formulario:
            self.formulario.destruir()
        self.formulario = formulario(self.marco)

    @seguro
    def acerca(self):
        """Crea la ventana de acerca"""
        acerca()


class acerca(Ventana):
    """Ventana de Acerca"""

    def __init__(self):
        Ventana.__init__(self, OBTENER_ROOT(), 'Acerca')
        self.valores()

    def valores(self):
        self.gui.get_variable('vercion').set('{} - Ver. {}'.format(NOMBRE,VERSION))
        self.gui.get_variable('titulo').set(TITULO)
        self.gui.get_variable('fecha').set(FECHA.strftime(FORMATO_FECHA))
        self.gui.get_variable('autor').set(AUTOR)
        self.gui.get_variable('contacto').set(CONTACTO)

    def licencia(self):
        archivo = abspath(join(dirname(__file__),'Licencia.html'))
        subprocess.Popen([archivo])

    def manual(self):
        proc = join(CARPETA_MADRE, 'manual.pdf')
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', proc])
        if sys.platform.startswith('win'):
            os.startfile(proc)

    def actualisar(self):
        actualisar()

def actualisar():
    """Utilisa pip, que viene instalado con python, para actualisar el paquete
    scet a la ultima version en pypi, https://pypi.python.org/pypi/SCET"""
    log.info('Ejecutando Actualisador')
    if sys.platform.startswith('linux'):
        r = [ 'install', 'scet', '--user', '--upgrade']
    elif sys.platform.startswith('win'):
        r = ['install', 'scet', '--upgrade']
    else:
        r = ['install', 'scet', '--upgrade']
    pip.main(r)
    messagebox.showinfo(
        title='Actualisacion Completa',
        message='El programa se cerrara ahora para aplicar los cambios, {}'.format(r),
        )
    sys.exit(0)

def crearBaseDatosSQLite():
    """Borra y crea un nuevo archivo de SQLite con la base de datos"""
    log.info('Creando nueva Base de Datos local')
    # Borrar y crear archivo
    if isfile(ARCHIVO_SQLITE):
        os.remove(ARCHIVO_SQLITE)
        log.info('Borrando Base de Datos vieja')
    bd = sqlite3.connect(ARCHIVO_SQLITE)
    # Leer archivo SQL y ejecutarlo
    sql = open(ARCHIVO_SQL_SQLITE).read()
    cursor = bd.cursor()
    for qry in sql.split(";"):
        log.debug('='*72 + '\nEjecutando SQL: \n' + qry)
        cursor.execute(qry)
    bd.commit()
    log.info('Nueva Base de Datos creada')

def main():
    root = OBTENER_ROOT()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    scet = programa(root)
    root.mainloop()

if __name__ == '__main__':
    main()
