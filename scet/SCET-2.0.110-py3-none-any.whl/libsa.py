#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import traceback
import time
import datetime
import shutil
from xml.etree.ElementTree import XML, Element, ElementTree, tostring, ProcessingInstruction as PI
from tkinter import Tk, ttk, Toplevel, Text, messagebox, filedialog

import pygubu
import pymysql

from scet import bd_xml as bd
from scet.globales import *


log = logging.getLogger(__name__)


class Error(Exception):
    """Error Base para el Modulo

    Atibutos:
        arg - Contenido del error
        obj - Objeto que creo el error

    Metodos:
        mensaje - genera un messagebox.showwarning
        con texto aclaratorio del error

    """

    title = None
    message = None
    detail = None
    parent = None

    def __init__(self, arg, obj=None):
        self.arg = arg
        self.title = """Error"""
        self.message = self.arg
        self.obj = obj
        self.detail = ''

    def mensaje(self):
        try:
            self.parent = self.obj.master
        except AttributeError:
            self.parent = None

        o = {
        'title':self.title,
        'message':self.message,
        'detail':self.detail,
        'parent':self.parent
        }

        log.error('{title}: {message}'.format(**o))
        messagebox.showwarning(**o)

    def __str__(self):
        return self.message


class ErrorEscritura(Error):
    """Error producido cuando un campo ha sido escrito con un tipo de valor equibocado

    Atributos:
        campo - Nombre de la variable que contiene el valor
        esp - Tipo de valor esperado para el campo
        valor - Valor introducido(si es posible obtenerlo)
        tipo - Clase del valor introducido(si es posible obtenerlo)
        nota - Comentario informativo acerca del Error(Opcional)
    """

    def __init__(self, campo, esp, valor=None, nota=None, obj=None):
        self.campo = campo
        self.esp = esp
        self.valor = valor
        self.tipo = tipo = {str:'Texto', int:'Numero', float:'Decimal', bool:'Cierto/Falso', type(None):'Nulo'}[type(valor)]
        self.nota = nota
        self.obj = obj
        self.title = """Error de Escritura en <{campo}>""".format(**locals())
        self.message = """Se esperaba obtener <{esp}> pero se obtubo <{tipo}>""".format(**locals())
        self.detail = self.nota

class ErrorFormato(Error):
    """Error producido cuando un campo ha sido mal escrito, no sigiendo un formato

    Atributos:
        campo - Nombre de la variable que contiene el valor
        formato - Tipo de valor esperado para el campo
        valor - Valor introducido
        nota - Comentario informativo acerca del Error(Opcional)
    """

    def __init__(self, campo, formato, valor, nota=None, obj=None):
        self.campo = campo
        self.formato = formato
        self.valor = valor
        self.nota = nota
        self.obj = obj
        self.title = """Error de Formato en <{campo}>""".format(**locals())
        self.message = """<{valor}> no sigue el formato <{formato}>""".format(**locals())
        self.detail = self.nota

class ErrorValor(Error):
    """Error producido cuando un campo contiene un valor sin sentido en el contexto dado

    Atributos:
        campo - Nombre de la variable que contiene el valor
        con - Contexto en el que se introduce el valor
        valor - Valor introducido
        nota - Comentario informativo acerca del Error(Opcional)
    """

    def __init__(self, campo, contexto, valor, nota=None, obj=None):
        self.campo = campo
        self.contexto = contexto
        self.valor = valor
        self.nota = nota
        self.obj = obj
        self.title = """Error de Valor en <{campo}>""".format(**locals())
        self.message = self.contexto
        self.detail = self.valor

class ErrorSilencioso(Error):
    """Error que no debe ser informado al usuario, para uso interno"""

    def __init__(self):
        pass

    def mensaje(self):
        pass

    def __str__(self):
        return "Error Interno"


def seguro(funcion):
    log.debug('Creando wraper seguro para funcion {}'.format(funcion))
    detalles = "Verifique el archivo de registro (registro.log) para mas detalles"

    def ejecucion(self, *arg):
        log.debug('Iniciando una ejecucion segura {}'.format(funcion))
        try:
            return funcion(self, *arg)

        except SystemExit as err:
            log.warning('Saliendo del sistema de forma normal')
            messagebox.showinfo(title='Adios', message='Nos vemos Pronto!', parent=self.master)
            sys.exit(0)

        except Error as err:
            log.warning('Se atrapo al error de libsa {err}'.format(**locals()))
            err.mensaje()
            return False

        except IOError as err:
            log.warning('Se atrapo al error de IO {err}'.format(**locals()))
            error = traceback.format_exc()
            log.error(error)
            msj = '''Ocurrio un error al intentar leer o escribir un archivo.'''
            det = '''Verifique que todos los archivos del sistema esten en su lugar
y que tiene permisos nesesarios para usarlos.
''' + detalles
            messagebox.showerror(title='Error Archivo', icon="error", message=msj, detail=det)
            return False

        except pymysql.err.IntegrityError as err:
            log.warning('Se atrapo al error de Integrada {err}'.format(**locals()))
            msj = '''La Base de Datos rechazo la información.'''
            det = '''Probablemente sea que el RIF/C.I. ya existe, intente buscarlo enves de crearlo.
''' + detalles
            messagebox.showerror(title='Error Datos', icon="error", message=msj, detail=det)
            return False

        except pymysql.err.ProgrammingError as err:
            log.warning('''Intento de coneccion no exitoso, {}
{}'''.format(err, self.config))
            messagebox.showinfo(message='Error de Coneccion',
                                icon="error", title="Error",
                                detail="""Los datos suministrados no son validos""")

        except pymysql.err.InterfaceError as err:
            log.warning('''Intento de coneccion no exitoso, {}
{}'''.format(err, self.config))
            messagebox.showinfo(message='Error de Coneccion',
                                icon="error", title="Error",
                                detail=err)

        except Exception as err:
            log.warning('Se atrapo al error {err}'.format(**locals()))
            error = traceback.format_exc()
            log.error(error)
            VentanaError()
            return False

        finally:
            log.debug('Cerrando la ejecucion segura {}'.format(funcion))

    return ejecucion

def ejecutar(funciones):
    log.debug('''Iniciando la ejecucion de las funciones:
    {}'''.format(funciones))
    for fun in funciones:
        if fun() is False:
            log.debug('La funcion {} detubo la ejecucion'.format(fun))
            return False
    else:
        log.debug('Terminando la ejecucion correctamente')
        return True

def transaccion(funcion):
    """Wrapper para ejecutar un proceso que accese a la Base de Datos en una Transación.
    Si la funcione regresa falso, o alza un error, realiza un rollback,
    si no relealiza un commit, no cierra la coneccion al final"""
    log.debug('Creando wraper transaccion para funcion {}'.format(funcion))

    def transaccion(self, *arg):
        BD = OBTENER_BD()
        log.debug('Iniciando un transaccion para la funcion {}'.format(funcion))
        # Borrar cambios echos fuera de una transacción
        BD.rollback()
        # Ejecutar funcion y le
        try:
            r = funcion(self, *arg)
            if r is False:
                BD.rollback()
                return False
        # Atrapar execpciones y llevarlas al sistema de errores
        except Exception:
            BD.rollback()
            log.warning('Debido a un error se cancelaron todos los cambios echos a la base de datos por la funcion {}'.format(funcion))
            raise
        # Guardar cambios
        else:
            BD.commit()
            return True

    return transaccion


class Ventana:

    nombre_objeto_ventana = '__ventana__'
    objeto_menu = '__menu__'

    def __init__(self, master, archivo_gui, menu=False):
        self.master = master
        self.archivo_gui = archivo_gui
        self._crear_gui(archivo_gui)
        if menu:
            self._crear_menu()
        self.gui.connect_callbacks(self)
        # Crear una variable para cada text
        self.mapeo_text_variable

    def destruir(self):
        self.vp.destroy()

    def _crear_gui(self, GUI):
        self.gui = pygubu.Builder()
        # Agregar las caprteas con los archivos
        self.gui.add_resource_path(CARPETA_RECURSOS)
        if not (GUI is None or self.master is None):
            self.gui.add_from_file(os.path.join(CARPETA_GUIS, GUI+'.ui'))
            # Hacer a la ventana reajustable
            self.master.rowconfigure(0, weight=1)
            self.master.columnconfigure(0, weight=1)
            self.vp = self.gui.get_object(self.nombre_objeto_ventana, self.master)
            log.debug('Creando interfaz {} en ubicacion {}'.format(self.archivo_gui, self.master))

    def _crear_menu(self):
        self.menu = self.gui.get_object(self.objeto_menu)
        self.master.configure(menu=self.menu)

    @property
    def mapeo_text_variable(self):
        '''Regresa un Dicionario con los tk.Text y sus variables.'''
        mapa = {}
        for nombre, widget in self.gui.objects.items():
            if widget.class_ == Text:
                variable = self.gui.create_variable(nombre)
                mapa[widget.widget] = variable
                widget.widget.bind("<FocusOut>", self.obtener_text_variable)
        return mapa


    @property
    def datos(self):
        '''Regresa un mapa de los nombre de variable y su respectivo valor'''
        datos = {}
        #Actualisar los Text
        for w in self.mapeo_text_variable:
            self.obtener_text_variable(None, w)
        for var, tkvar in self.gui.tkvariables.items():
            try:
                datos[var] = tkvar.get() if not tkvar.get() is '' else None
            except Exception:
                msj = """Tipo de dato erroneo guadado en la variable {}
es la variable {} de tipo {}""".format(var, tkvar, type(tkvar))
                raise Error(msj, self)
        return datos

    def _obtener_nombre(self, objeto):
        objeto = self.vp.nametowidget(objeto)
        for nombre, widget in self.gui.objects.items():
            if str(widget.widget) == str(objeto):
                return nombre
        else:
            return None

    def _cambiar_estado(self, widgets=('Entry','Combobox','Radiobutton','Checkbutton', 'Text', 'Spinbox'), estado='disabled'):
        for w in self.gui.objects:
            for t in widgets:
                if t in str(self.gui.objects[w]): self.gui.get_object(w)['state'] = estado

    def _cambiar_texto(self, widgets, texto):
        for (w, t) in zip(widgets, texto):
            self.gui.get_object(w)['text']=t

    def colocar_text_variable(self):
        '''Escribe a un widget tk.text el contenido de una StringVar
         segun el mapeo de crear_mapa_text()'''
        m = self.mapeo_text_variable
        for widget in m:
            t = m[widget].get()
            s = False
            if widget['state'] == 'disabled':
                widget['state'] = 'normal'
                s = True
            widget.delete(1.0, 'end')
            widget.insert(1.0, t)
            if s:
                widget['state'] = 'disabled'

    #Bindings
    def obtener_text_variable(self, evento, widget=None):
        '''Asigna el contenido de un tk.text a una StringVar
        segun el mapeo de crear_mapa_text()'''
        w = evento.widget if not evento is None else widget
        self.mapeo_text_variable[w].set(limpiar_texto(w.get(0.0, 'end')))


class VentanaError(Ventana):

    def __init__(self, args=None):
        Ventana.__init__(self, OBTENER_ROOT(), 'Error')
        # verificar que error debe ser levantado
        if args:
            error = ''.join(traceback.format_exception(*args))
        else:
            error = REGISTRO.getvalue()
        # escribir el registro en el Text
        self.gui.get_object('registro').insert(1.0, error)
        self.vp.focus_set()
        #~ self.vp.grab_set()
        self.vp.transient(self.master)
        self.master.wait_window(self.vp)

    def guardar(self):
        carpeta = filedialog.askdirectory(
            initialdir=os.path.expanduser('~'),
            parent=self.vp,
            )

        with open(join(carpeta, 'SCET.log'), 'w') as archivo:
            archivo.write(REGISTRO.getvalue())
        self.destruir()


class Base_Entrada:

    def __init__(self, tabla, **funciones):
        self.bd = tabla
        self.funciones_guardar = list(funciones.pop('guardar', []))
        self.funciones_cancelar = list(funciones.pop('cancelar', []))
        self.funciones_reiniciar = list(funciones.pop('reiniciar', []))
        self.funciones_limpiar = list(funciones.pop('limpiar', []))
        self.funciones_selecionar = list(funciones.pop('selecionar', []))
        self.funciones_buscar = list(funciones.pop('buscar', []))
        self.funciones_borrar = list(funciones.pop('borrar', []))
        self.funciones_cambio_registro = list(funciones.pop('cambio_registro', []))
        self.funciones_activar = list(funciones.pop('activar', []))
        self.funciones_desactivar = list(funciones.pop('descartivar', []))

    def _sincronisar(self, dir='tabla', reg=0, tabla=None, *opciones):
        ''' sincronisar (dir = ( tabla / formulario ), reg=0, tabla=<objeto Tabla>)
        Sincronisa la tabla/formulario con los contenidos del otro.

        Opciones:
            -no_pri: ignora la columna si es primaria
            -none_a_str: comvierte los NoneType a str()
            -fecha: comvierte los time.struc_time a formato
        '''

        if tabla is None: tabla = self.bd

        no_pri = 'no_pri' in opciones
        none_a_str = 'none_a_str' in opciones
        fecha = 'fecha' in opciones

        if dir == 'tabla':
            while True:
                try:
                    for col in tabla[reg]:
                        if no_pri and tabla.ver_columna(col, 'llave') == 'PRI': continue

                        try:
                            tabla[reg][col] = self.gui.get_variable(col).get()
                        except ValueError:
                            msj = """Seguramente Escribio mal un numero,
verifique que uso '.' enves de ','
para identificar decimales"""
                            raise ErrorEscritura(var, tabla.ver_columna(var, 'tipo'), None, msj)

                except IndexError:
                    tabla += {}
                else:
                    break

        elif dir == 'formulario':
            filas = (tabla[reg],) if not reg is None else tabla[:]
            for fila in filas:
                for col in fila:
                    d = filas[filas.index(fila)][col]

                    if no_pri and tabla.ver_columna(col, 'llave') == 'PRI': continue
                    if none_a_str and d is None: d = ''
                    if isinstance(d, time.struct_time) and fecha: d = time.strftime(FORMATO_FECHA_HORA, d)

                    self.gui.create_variable(col).set(d)

            self.colocar_text_variable()


    def _validar_todo(self):
        '''Va por todos los objetos, verifica si estan en la lista de validables y los valida'''
        log.info('iniciando validacion total')
        for nombre, widget in self.gui.objects.items():
            if widget.class_ in (ttk.Entry, ttk.Combobox):
                r = widget.widget.validate()
                if not (r is True):
                    raise ErrorSilencioso()
        else:
            return True

    #Validaciones Basicas
    def _validar_fecha(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando fecha de <{}>'.format(nombre))

        if P == "":
            return True

        try:
            datetime.datetime.strptime(P, FORMATO_FECHA)

        except ValueError:
            msj = ("""Verifique que no escribio mes 13 o febrero 30
Intente escribir '-' enves de '/'""")
            err = ErrorFormato(nombre, FORMATO_FECHA, P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_obligatorio(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando obligatorio <{}>'.format(nombre))

        if P == "":
            r = '{} es obligatorio'.format(nombre)
            err = ErrorValor(nombre, r, P, obj=self)
            err.mensaje()
            return False

        return True


    def _validar_hora(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando hora de <{}>'.format(nombre))

        if P == "":
            return True

        try:
            datetime.datetime.strptime(P, FORMATO_HORA)

        except ValueError:
            msj = ("""Verifique que no escribio mes 13 o febrero 30
Intente escribir '-' enves de '/'""")
            err = ErrorFormato(nombre, FORMATO_HORA, P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_decimal(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando decimal de <{}>'.format(nombre))

        dato = P.split('.')
        msj = ("""verifique que uso '.' enves de ',' para identificar decimales""")

        if not len(dato) in range(1,3):
            err = ErrorEscritura(nombre, 'Decimal', P, msj, obj=self)
            err.mensaje()
            return False

        if not sum([1 if (v.isdecimal() or v == '') else 0 for v in dato]) == len(dato):
            err = ErrorEscritura(nombre, 'Decimal', P, msj, obj=self)
            err.mensaje()
            return False

        if (not len(dato) == 1) and (sum([1 if v == '' else 0 for v in dato]) == len(dato)):
            err = ErrorEscritura(nombre, 'Decimal', P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_numero(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando numero de <{}>'.format(nombre))

        if P == "":
            return True

        if not P.isdecimal():
            msj = ("""Seguramente Escribio mal un numero,
verifique que escribio '0' en ves de dejarlo vacio""")
            err = ErrorEscritura(nombre, 'Numero', P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_texto(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando texto en <{}>'.format(nombre))

        if P == "":
            return True

        if not len(P) in range(1,51):
            con = ("""El texto no puede ser mayor a 50 caracteres""")
            val = ("""{}... ({} caracteres)""".format(P[:10], len(P)))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_rif(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando RIF de <{}>'.format(nombre))

        if not P[0].upper() in ('J', 'G', 'E', 'V'):
            con = ("""El R.I.F: / C.I. debe empesar con V, E, J o G""")
            val = ("""{} no es un caracter valido""".format(P[0].upper()))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        if P[0].upper() in ('J','G') and len(P) != 10:
            con = ("""El R.I.F: debe tener 10 caracteres""")
            val = ("""{}... ({} caracteres)""".format(P[:10], len(P)))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        if P[0].upper() in ('V','E') and len(P) not in (9,10):
            con = ("""La C.I. debe tener de 9 caracteres o 10 si es un RIF personal""")
            val = ("""{}... ({} caracteres)""".format(P[:10], len(P)))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        if not P[1:].isdecimal():
            msj = ("""El R.I.F: / C.I. be escribirse en numeros sin puntos ni guiones
Ej. J123456789 no J-12345678-9 o V-12.345.678""")
            err = ErrorEscritura(nombre, 'Numero', P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_telefono(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando telefono de <{}>'.format(nombre))

        if P == '':
            return True

        if not len(P) in range(1,8):
            con = ("""El texto no puede ser mayor a 7 caracteres""")
            val = ("""{}... ({} caracteres)""".format(P[:7], len(P)))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        if not P.isdecimal():
            msj = ("""Seguramente Escribio mal un numero,
verifique que escribio '0' en ves de dejarlo vacio""")
            err = ErrorEscritura(nombre, 'Numero', P, msj, obj=self)
            err.mensaje()
            return False

        return True

    def _validar_telefono_codigo(self, d, i, P, s, S, v, V, W):
        nombre = self._obtener_nombre(W)
        log.debug('Validando telefono codigo de <{}>'.format(nombre))

        if P == '':
            return True

        if not len(P)in range(0,5):
            con = ("""El texto no puede ser mayor a 4 caracteres""")
            val = ("""{}... ({} caracteres)""".format(P[:4], len(P)))
            err = ErrorValor(nombre, con, val, obj=self)
            err.mensaje()
            return False

        if not P.isdecimal():
            msj = ("""Seguramente Escribio mal un numero,
verifique que escribio '0' en ves de dejarlo vacio""")
            er = ErrorEscritura(nombre, 'Numero', P, msj, obj=self)
            err.mensaje()
            return False

        return True


class Formulario(Base_Entrada):
    nombre_objeto_formulario = '__formulario__'

    msj_guardado = 'El Formulario {nombre} fue guardado'

    def __init__(self, tabla, id_primario=None, id_extranjero=None, **funciones):
        Base_Entrada.__init__(self, tabla, **funciones)
        self.id_primario = id_primario
        self.id_extranjero = id_extranjero

        # obtener la informacion de la tabla del servidor
        self.bd.seleccionar_bd(condicion=False)

        pri = self.bd.llaves_primarias
        self.llave_primaria = pri[0] if len(pri) > 0 else None

        sec = self.bd.llaves_extranjeras
        self.llave_extranjera = sec[0] if len(sec) > 0 else None

        # buscar datos a modificar si existen
        condicion = {}
        if self.id_primario:
            condicion[self.llave_primaria] = self.id_primario
        if self.id_extranjero:
            condicion[self.llave_extranjera] = self.id_extranjero
        self.bd.seleccionar_bd(condicion=condicion)
        # guardar los datos
        self.id_primario = [fila[self.llave_primaria] for fila in self.bd]


    #Funciones
    def _guardar(funcion):
        log.debug('Creando wraper _guardar para funcion {}'.format(funcion))

        def guardar(self):
            log.debug('iniciando guardado para funcion {}'.format(funcion))
            self._validar_todo()
            funcion(self)
            id = None
            for fila in self.bd:
                if self.id_primario:
                    fila[self.llave_primaria] = self.id_primario[fila.pos]
                else:
                    fila[self.llave_primaria] = None
                if self.id_extranjero:
                    fila[self.llave_extranjera] = self.id_extranjero
                tabla = self.bd.copy(fila.pos, fila.pos+1)
                if fila[self.llave_primaria]:
                    id = fila[self.llave_primaria]
                    tabla.actualisar_bd()
                else:
                    id = tabla.insertar_bd()
            nombre = self.bd.nombre
            self.id_primario = id
            log.info(self.msj_guardado.format(**locals()))
            return True

        return guardar

    @_guardar
    def guardar(self):
        pass

    def borrar(self):
        log.debug('iniciando borrado para {}'.format(self.bd.nombre))
        self.bd.borrar_bd()


class Tabla(Base_Entrada):
    nombre_objeto_tabla = '__tabla__'
    condicion = False
    columnas = None
    campo = None

    def __init__(self, tabla, id_extranjero=None):
        Base_Entrada.__init__(self, tabla)
        self.id_extranjero = id_extranjero
        self.lista_filas = []
        if self.bd.coneccion and self.bd.nombre:
            self.bd.seleccionar_bd(condicion=False)
            sec = self.bd.llaves_extranjeras
            self.llave_extranjera = sec[0] if len(sec) > 0 else None
            condicion = {}
            if id_extranjero:
                condicion[self.llave_extranjera] = self.id_extranjero
            self.bd.seleccionar_bd(condicion=condicion)

        if self.master:
            self.arbol = self.gui.get_object(self.nombre_objeto_tabla)
            self.arbol.bind("<Double-1>", self._crear_campo)
            self.arbol.bind("<Return>", self._crear_campo)
            self.arbol.bind("<Delete>", self.eliminar_valores)
            self.actualisar_arbol()

    @seguro
    def agregar_valores(self, event=None):
        self.bd += self.datos

        self.actualisar_arbol()
        self.arbol.selection_set(self.lista_filas[-1])

    @seguro
    def eliminar_valores(self, event=None):
        for id in self.arbol.selection():
            reg = self.lista_filas.index(id)
            del self.bd[reg]

        self.actualisar_arbol()

    def actualisar_tabla(self):
        self.bd.seleccionar_bd(condicion=self.condicion)
        self.actualisar_arbol()

    def actualisar_arbol(self):
        self._limpiar_campos()
        for i in self.lista_filas:
            self.arbol.delete(i)
        self.lista_filas = []

        n=0
        for reg in self.bd:
            n+=1
            valores = [(reg[col] if not reg[col] is None else '') for col in self.bd.columnas]
            log.debug('Valores arbol {}: {}'.format(self.nombre_tabla, valores))

            id = self.arbol.insert('', 'end', values=valores, tags={0:'fila_A', 1:'fila_B'}[n%2])
            self.lista_filas.append(id)

        self.arbol.tag_configure('fila_A', background=('white' if len(self.bd)%2 == 1 else 'gray'))
        self.arbol.tag_configure('fila_B', background=('white' if len(self.bd)%2 == 0 else 'gray'))

    def seleccion(self):
        reg = self.arbol.selection()
        filas = []
        for fil in reg:
            n = self.lista_filas.index(fil)
            filas.append(self.bd[n])
        return tuple(filas)

    def guardar(self):
        id = None
        for fila in self.bd:

            if self.id_extranjero:
                fila[self.llave_extranjera] = self.id_extranjero

            tabla = self.bd.copy(fila.pos, fila.pos+1)

            if fila[tabla.llaves_primarias[0]]:
                tabla.actualisar_bd()
            else:
                id = tabla.insertar_bd()

        nombre = self.bd.nombre
        self.id_primario = id
        log.info(self.msj_guardado.format(**locals()))

        return True

    def _limpiar_campos(self):
        if not self.campo is None:
            self.campo.cancelar()

    def _crear_campo(self, event):
        ''' Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text '''

        # close previous popups
        self._limpiar_campos()

        # what row and column was clicked on
        rowid = self.arbol.identify_row(event.y)
        column = self.arbol.identify_column(event.x)

        # do nothing if item is there is no row
        if rowid == '':
            self.agregar_valores()
            return

        # obtener informacioen de bd
        fila = self.lista_filas.index(rowid)
        nro_col = int(column[1:])-1
        columna = self.arbol['displaycolumns'][nro_col]
        columna = self.arbol['columns'].index(columna)
        columna = self.bd.columnas[columna]

        # clicked row parent id
        parent = self.arbol.parent(rowid)

        # get column position info
        x,y,width,height = self.arbol.bbox(rowid, column)

        # y-axis offset
        pady = height // 2
        texto = self.arbol.item(rowid, 'values')[nro_col]

        # place Entry popup properly
        self.campo = self.Campo(self, self.arbol , self.bd, fila, columna)
        self.campo.place(x=x, y=y+pady, width=width, height=height, anchor='w')

    class Campo(ttk.Entry):
        f = None

        def __init__(self, padre, arbol, tabla, fila, columna, **kw):
            ''' If relwidth is set, then width is ignored '''
            super().__init__(arbol, **kw)
            self.padre = padre
            self.tabla = tabla
            self.columna = columna
            self.fila = fila

            texto = tabla[fila][columna] if not tabla[fila][columna] is None else ''
            self.insert(0, texto)
            #~ self.selection_range(0, 'end')
            self['exportselection'] = False
            self['font'] = ('Helvetica', 11)

            self.focus_force()
            self.bind("<Control-a>", self.selectAll)
            self.bind("<Escape>", self.cancelar)
            self.bind("<Return>", self.guardar)
            #~ self.bind("<Delete>", self.padre.eliminar_valores)


        def selectAll(self, *ignore):
            ''' Set selection on the whole text '''
            self.selection_range(0, 'end')

            # returns 'break' to interrupt default key-bindings
            return 'break'

        def cancelar(self, evento=None):
            self.padre.campo = None
            self.padre.arbol.selection_set(self.padre.lista_filas[-1])
            self.destroy()

        @seguro
        def guardar(self, evento=None):
            self.tabla[self.fila][self.columna] = self.get()
            self.cancelar()
            self.padre.actualisar_arbol()


class Reporte:

    clausula_xml = '''version="{version}" encoding="{encoding}"'''
    clausula_estilo = '''type="{type}" href="{href}"'''
    id_estilo = '''stylesheet'''
    tag = '''reporte'''
    encoding = 'UTF-8' if platform.startswith('linux') else 'ISO-8859-1'
    version = '1.0'

    hoja_estilo = None
    tipo_hoja_estilo = None

    def __init__(self, *tablas, **configuracion):
        self.tablas = tablas

        self.hoja_estilo = configuracion.get('hoja_estilo')

        tipo = 'xsl'
        if '.' in self.hoja_estilo:
            hoja, tipo = self.hoja_estilo.split('.')
            self.tipo_hoja_estilo = tipo

        self.tipo_hoja_estilo = configuracion.get('tipo_hoja_estilo', tipo)

    def reporte_xml_estilo(self):
        nodo_root = datos_xml(*self.tablas)
        nodo_root.tag = self.tag

        nodo_xml = PI('xml', self.clausula_xml.format(version=self.version, encoding=self.encoding))

        assert  self.hoja_estilo, 'Falsa hoja de estilo'

        href = self.hoja_estilo
        type = '''text/{}'''.format(self.tipo_hoja_estilo)

        nodo_estilo = PI('xml-stylesheet', self.clausula_estilo.format(**locals()))

        return '\n'.join( [tostring(nodo, 'unicode') for nodo in (nodo_xml, nodo_estilo, nodo_root)] )


class Selector(Base_Entrada):
    nombre_objeto_selector = '__selector__'

    def __init__(self, tabla, id_extranjero=None, **funciones):
        Base_Entrada.__init__(self, tabla, **funciones)
        self.id_extranjero = id_extranjero

        # obtener la informacion de la tabla del servidor
        self.bd.seleccionar_bd(condicion=False)

        sec = self.bd.llaves_extranjeras
        self.llave_extranjera = sec[0] if len(sec) > 0 else None

        # buscar datos a modificar si existen
        condicion = {self.llave_extranjera : self.id_extranjero} if self.id_extranjero else True
        self.bd.seleccionar_bd(condicion=condicion)

    def seleccion(self):
        reg = self.lista.current()
        return self.bd[reg]


class Bucle(Base_Entrada):
    nombre_objeto_bucle = '__bucle__'

    def __init__(self, tabla, **funciones):
        Base_Entrada.__init__(self, tabla, **funciones)

        self.__pos__ = self.gui.create_variable('int:__pos__')
        self.__tot__ = self.gui.create_variable('int:__tot__')
        self.__pos__.set(0)
        self.__tot__.set(0)

    #Metodos
    def _activar(self):
        ejecutar(self.funciones_activar)
        self.__pos__.set(1 if len(self.bd) >= 1 else 0)
        self.__tot__.set(len(self.bd))
        self._sincronisar('formulario', self.__pos__.get()-1, self.bd,'fecha', 'none_a_str')
        ejecutar(self.funciones_cambio_registro)

    def _desactivar(self):
        ejecutar(self.funciones_desactivar)
        self.__pos__.set(0)
        self.__tot__.set(0)
        ejecutar(self.funciones_cambio_registro)
        self._cambiar_estado()

    def cambiar_registro(self, numero_registro):
        self.__pos__.set(numero_registro + 1)
        self._sincronisar('formulario', numero_registro, None, 'fecha', 'none_a_str')
        ejecutar(self.funciones_cambio_registro)

    #Funciones
    def registro_ant(self, evento=None):
        p = self.__pos__.get() -1
        t = self.__tot__.get() -1
        if p > 0:
            p -= 1
        else:
            p = t
        self._sincronisar('formulario', p, None, 'fecha', 'none_a_str')
        self.__pos__.set(p+1)
        ejecutar(self.funciones_cambio_registro)

    def registro_sig(self, evento=None):
        p = self.__pos__.get() -1
        t = self.__tot__.get() -1
        if p < t:
            p += 1
        else:
            p = 0
        self._sincronisar('formulario', p, None, 'fecha', 'none_a_str')
        self.__pos__.set(p+1)
        ejecutar(self.funciones_cambio_registro)

    def selecionar(self, evento=None):
        ejecutar(self.funciones_selecionar)
        self._desactivar()

    def guardar(self, evento=None):
        numero_registro = (self.__pos__.get() - 1)
        self.bd[numero_registro] = self.datos
        ejecutar(self.funciones_guardar)

    def borrar(self, evento=None):
        numero_registro = (self.__pos__.get() - 1)
        del self.bd[numero_registro]
        self.__tot__.set(len(self.bd))
        ejecutar(self.funciones_borrar)
        self.registro_ant()

    def buscar(self, evento=None):
        ejecutar(self.funciones_buscar)

        if self.bd:
            self._activar()
        ejecutar(self.funciones_cambio_registro)


def limpiar_texto(texto):
    texto.replace('\t','')
    while texto[-1:] == '\n':
        texto = texto[:-1]
    return texto

def calc_meses(dias):
    meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    mes = 0

    while dias >= meses[mes]:
        dias -= meses[mes]
        mes += 1

    return mes, dias

def calc_dias(mes):
    meses = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return sum(meses[:mes])


def timedelta_a_iso(timedelta):
    '''convierte un timedate.timedelta a formato iso: YYYY-MM-DD HH:mm:ss, sin extra ceros'''

    formato = "{YYYY}-{MM}-{DD} {HH}:{mm}:{ss}"

    mm, ss = divmod(timedelta.seconds, 60)
    HH, mm = divmod(mm, 60)
    YYYY, DD = divmod(timedelta.days, 365)
    MM, DD = calc_meses(DD)

    return formato.format(**locals())


def timedelta_a_fecha(timedelta):
    '''convierte un timedate.timedelta a formato iso: YYYY-MM-DD, sin extra ceros'''

    formato = "{YYYY}-{MM}-{DD}"
    YYYY, DD = divmod(timedelta.days, 365)
    MM, DD = calc_meses(DD)
    return formato.format(**locals())


def timedelta_a_duracion(timedelta):
    '''convierte un timedate.timedelta a formato legible: YYYY anos, DD dias, hh horas'''

    formato = '''{YYYY}-{MM}-{DD} {HH}:{mm}:{ss}'''


    mm, ss = divmod(timedelta.seconds, 60)
    hh, mm = divmod(mm, 60)
    YYYY, DD = divmod(timedelta.days, 365)
    MM, DD = calc_meses(DD)

    formato = (('anos', YYYY), ('meses', MM), ('dias', DD), ('horas', hh), ('minutos', mm), ('segundos', ss))

    return ' '.join(["{} {}".format(valor, texto) for texto, valor in formato if valor > 0])


def convertir_fecha(tabla, campo, formato, obj=None):
    for fil in tabla:
        try:
            fil[campo] = time.strptime(fil[campo], formato)
        except ValueError:
            msj = """Intente escribir '-' enves de '/'"""
            raise ErrorFormato("{}, fila {}".format(campo, fil.pos), formato, fil[campo], msj, self, obj)
    return


def datos_xml(*tablas, metadatos=False):
    """Devuelve un objeto Element con los datos de las tablas"""
    xml = Element('xml')
    for tarbol in [XML(tabla.xml) for tabla in tablas]:
        xml.append(arbol)
    return xml


class ControladorEstado:
    '''Objeto disenado para ser un wrapper entre una clase que escriba a un stream y una Tk.StringVar'''

    nombreVariable = '__estado__'

    def __init__(self, variable):
        self.variable = variable
        self.buffer = []

    def write(self, valor):
        if valor == '':
            return
        self.buffer.append(valor)
        self.flush()

    def flush(self):
        for valor in self.buffer:
            self.buffer.remove(valor)
            self.variable.set(valor)
