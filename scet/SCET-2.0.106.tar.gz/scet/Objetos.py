#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from shutil import copyfile
from tkinter import ttk, messagebox, Tk, Toplevel, filedialog

from scet.libsa import Ventana, Base_Entrada, Formulario, Bucle, Tabla
from scet.libsa import transaccion, ejecutar, seguro
from scet import Formularios
from scet import Mostradores
from scet import Plantillas
from scet import Tablas
from scet.globales import *


log = logging.getLogger(__name__)


class Cliente_Nuevo(Ventana):
    archivo_gui = 'C_Cliente_Nuevo'

    def __init__(self, master):
        self.master = master
        self._gui()
        self._formularios()

    def _gui(self):
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.m_infomacion_fiscal = self.gui.get_object('Informacion_Fiscal')
        self.m_contacto = self.gui.get_object('Contacto')

    @transaccion
    def _formularios(self):
        self.informacion_fiscal = Formularios.Informacion_Fiscal(self.m_infomacion_fiscal)
        self.contacto = Plantillas.Contacto(self.m_contacto)

    def _crear_entidad(self):
        d = self.informacion_fiscal.datos
        nombre = d['razon_social']
        referencia = d['rif']
        self.entidad = Formularios.Entidad(None)
        self.entidad.bd += locals()
        self.entidad.guardar()
        self.informacion_fiscal.id_extranjero = self.entidad.id_primario
        self.contacto.id_extranjero = self.entidad.id_primario
        self.idEntidades = self.entidad.id_primario
        self.referencia = referencia
        self.razon_social = nombre

    #~ def _crear_ubicacion(self):
        #~ ubicaciones = Formularios.Ubicaciones(None)
        #~ log.debug(self.informacion_fiscal.datos)
        #~ log.debug(self.informacion_fiscal.datos['estado'])
        #~ ubicaciones.bd += {
            #~ 'referencia':self.referencia,
            #~ 'nombre':'Ubicacion de {}'.format(self.razon_social),
            #~ 'descripcion':'{estado} – {ciudad} – {direccion}'.format(**self.informacion_fiscal.datos),
            #~ }
#~
        #~ ubicaciones.guardar()
        #~ self.idUbicaciones = ubicaciones.id_primario
#~
        #~ descripcion = Plantillas.Descripciones(None)
        #~ descripcion.id_primario = ubicaciones.id_primario
        #~ for val in ('estado', 'ciudad', 'direccion'):
            #~ var = descripcion.gui.create_variable(val)
            #~ var._name = val
            #~ var.set(self.informacion_fiscal.datos[val])
#~
        #~ descripcion.guardar()
#~
        #~ return True

    def _crear_cliente(self):
        idEntidades = self.idEntidades
        #~ idUbicaciones = self.idUbicaciones
        self.cliente = Formularios.Cliente(None)
        self.cliente.bd += locals()
        self.cliente.guardar()
        return True

    @seguro
    @transaccion
    def guardar(self):
        self._crear_entidad()
        #~ self._crear_ubicacion()
        self._crear_cliente()
        self.informacion_fiscal.guardar()
        self.contacto.guardar()
        messagebox.showinfo(message='Guardado exitosamente',
            icon="info", title="Client guardado de forma exitosa")
        self.cancelar()

    def cancelar(self):
        self.master.destroy()


class Equipo_Nuevo(Ventana):
    archivo_gui = 'C_Formulario'
    metodo = None

    idObjetos = None
    idClientes = None

    def __init__(self, master):
        self.master = master
        self._gui()
        self._formularios()

    def _gui(self):
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.marco = self.gui.get_object('__marco__')

    @transaccion
    def _formularios(self):
        self.plantilla = Plantillas.Especificaciones(self.marco)

    def _crear_objeto(self):
        d = self.plantilla.datos
        nombre = d['equipo']
        referencia = d['serial']

        self._objeto = Formularios.Objetos(None)
        self._objeto.bd += locals()

        if self._objeto.guardar():
            self.idObjetos = self._objeto.id
            self.plantilla.id = self.idObjetos
            return True
        else:
            return False

    def _crear_equipo(self):
        idObjetos = self.idObjetos
        idClientes = self.idClientes
        self._equipo = Formularios.Equipos(None)

        self._equipo.bd += locals()

        if self._equipo.guardar():
            self.idEquipos = self._equipo.id
            return True
        else:
            return False

    @seguro
    @transaccion
    def guardar(self):
        f = (
            self._crear_objeto,
            self._crear_equipo,
            self.plantilla.guardar,
            )
        if not ejecutar(f):
            assert True, 'El Proseso ha sido canselado intencionalmente por el programa'
        else:
            self.cancelar()

    def cancelar(self):
        self.vp.destroy()
        self.arbol.actualisar_tabla()


class Objetos(Ventana):
    nombre = 'Objetos'
    archivo_gui = 'C_Objetos'

    def __init__(self, master, id_primario=None):
        self.master = master
        self.id_primario = id_primario

        Ventana.__init__(self, self.master, self.archivo_gui)
        m1 = self.gui.get_object('__primario__') if self.master else None
        m2 = self.gui.get_object('__secundario__') if self.master else None

        self._primario = Formularios.Objetos(m1, self.id_primario)
        self.llave_primaria = self._primario.llave_primaria

        self._secundarios = [Tablas.Especificaciones(m2, self.id_primario)]

    def guardar(self):
        self._primario.guardar()
        self.id_primario = self._primario.id_primario
        for formulario in self._secundarios:
            formulario.id_extranjero = self.id_primario
            formulario.guardar()


class Ubicaciones(Ventana):
    nombre = 'Ubicaciones'
    archivo_gui = 'C_Objetos'

    def __init__(self, master, id_primario=None):
        self.master = master
        self.id_primario = id_primario

        Ventana.__init__(self, self.master, self.archivo_gui)
        m1 = self.gui.get_object('__primario__') if self.master else None
        m2 = self.gui.get_object('__secundario__') if self.master else None

        self._primario = Formularios.Ubicaciones(m1, self.id_primario)
        self.llave_primaria = self._primario.llave_primaria

        self._secundarios = [Tablas.Descripciones(m2, self.id_primario)]

    def guardar(self):
        self._primario.guardar()
        self.id_primario = self._primario.id_primario
        for formulario in self._secundarios:
            formulario.id_extranjero = self.id_primario
            formulario.guardar()


class Entidades(Ventana):
    nombre = 'Entidades'
    archivo_gui = 'C_Entidades'

    def __init__(self, master, id_primario=None):
        self.master = master
        self.id_primario = id_primario

        Ventana.__init__(self, self.master, self.archivo_gui)
        m1 = self.gui.get_object('__primario__') if self.master else None
        m2 = self.gui.get_object('__secundario__') if self.master else None
        m3 = self.gui.get_object('__formulario__') if self.master else None
        m4 = self.gui.get_object('__extra__') if self.master else None

        self._primario = Formularios.Entidad(m1, self.id_primario)
        self.llave_primaria = self._primario.llave_primaria

        self._secundarios = [
            Tablas.Caracteristicas(m2, self.id_primario),
            Formularios.Informacion_Fiscal(m3, self.id_primario),
            Tablas.Contacto(m4, self.id_primario),
            ]

        #~ self._secundarios[1].gui.tkvariables['razon_social'] = self._primario.gui.get_variable('nombre') if self.master else None
        #~ self._secundarios[1].gui.tkvariables['rif'] = self._primario.gui.get_variable('referencia') if self.master else None

    def guardar(self):
        self._primario.guardar()
        self.id_primario = self._primario.id_primario
        for formulario in self._secundarios:
            formulario.id_extranjero = self.id_primario
            formulario.guardar()

    def borrar(self):
        self._primario.borrar()




class Control_Registros(Ventana):

    _formulario_base = None
    llave_base = None
    id_base = None

    _formularios_primarios = ()

    archivo_gui = None

    def __init__(self, master, id_base=None):
        self.master = master
        self.id_base = id_base
        Ventana.__init__(self, self.master, self.archivo_gui)
        self._buscar_datos()

    @seguro
    @transaccion
    def _buscar_datos(self, event=None):
        # buscar datos del Formulario Base
        self._base = self._formulario_base(None, self.id_base)
        self.llave_base = self._base.bd.llaves_primarias[0]
        self.llaves_primarias = self._base.bd.llaves_extranjeras
        self.id_primarios = [self._base.bd[0][llave] for llave in self.llaves_primarias]
        # buscar datos del objeto principal y sus carateristicas
        self._primarios = []
        for f, id in zip(self._formularios_primarios, self.id_primarios):
            m = self.gui.get_object(f.nombre) if self.master else None
            self._primarios.append(f(m, id))

    @seguro
    @transaccion
    def guardar(self, evento=None):
        self._base.bd.truncar()
        self._base.bd += ()
        for formulario in self._primarios:
            formulario.guardar()
            self._base.bd[0][formulario.llave_primaria] = formulario.id_primario
        self._base.guardar()
        messagebox.showinfo(
            icon="info",
            message='Guardado exitosamente',
            title="Guardado exitosamente"
            )
        self.cancelar()

    def cancelar(self, evento=None):
        self.vp.destroy()

class Herramientas(Control_Registros):
    archivo_gui = 'C_Herramientas'
    _formulario_base = Formularios.Herramientas
    _formularios_primarios = (Objetos,)

class Almasenes(Control_Registros):
    archivo_gui = 'C_Almasenes'
    _formulario_base = Formularios.Almasenes
    _formularios_primarios = (Ubicaciones,)

class Talleres(Control_Registros):
    archivo_gui = 'C_Talleres'
    _formulario_base = Formularios.Talleres
    _formularios_primarios = (Ubicaciones,)

class Tecnicos(Control_Registros):
    archivo_gui = 'C_Tecnicos'
    _formulario_base = Formularios.Tecnicos
    _formularios_primarios = (Entidades,)

class Empresas(Control_Registros):
    archivo_gui = 'C_Empresas'
    _formulario_base = Formularios.Empresas
    _formularios_primarios = (Entidades,)

    @seguro
    def selecionarLogo(self):
        imagen = filedialog.askopenfilename(
            filetypes = [
                ('PNG',('.png')),
                ('JPEG',('.jpeg', '.jpg', '.jpe')),
                ('Todos los archivos','*')
            ],
            initialdir = CARPETA_TRABAJO,
            initialfile = NOMBRE_SQLITE,
            title = "Seleccionar logo de la Empresa",
            )
        if imagen:
            copyfile(imagen, IMAGEN_LOGO)

class Clientes(Control_Registros):
    archivo_gui = 'C_Clientes'
    _formulario_base = Formularios.Cliente
    _formularios_primarios = (Entidades,)
