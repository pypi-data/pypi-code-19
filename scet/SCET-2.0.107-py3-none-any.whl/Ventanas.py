#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from tkinter import ttk, messagebox, Tk, Toplevel

from scet.libsa import Ventana, Base_Entrada, Formulario, Bucle, Tabla
from scet.libsa import transaccion, ejecutar, seguro
from scet import Contenedores
from scet import Formularios
from scet import Mostradores
from scet import Objetos
from scet import Plantillas
from scet import Reportes
from scet import Selectores
from scet import Tablas
from scet.Contenedores import Tabla_Busqueda
from scet.globales import *


log = logging.getLogger(__name__)


class Control_Recursos(Ventana):
    archivo_gui = 'C_Control_Recursos'
    _lista_tablas = ()
    _lista_formularios = ()

    _formulario = None

    def __init__(self, master):
        self.master = master
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.libreta = self.gui.get_object('__libreta__')
        self.marco = self.gui.get_object('__marco__')
        self._tablas()
        self._actualisar_tablas()

    def _tablas(self):
        m_talleres = self.gui.get_object('__marco_talleres__')
        m_almasenes = self.gui.get_object('__marco_almasenes__')
        m_tecnicos = self.gui.get_object('__marco_tecnicos__')
        m_herramientas = self.gui.get_object('__marco_herramientas__')
        m_empresas = self.gui.get_object('__marco_empresas__')

        t_talleres = Tabla_Busqueda(m_talleres, Tablas.Talleres)
        t_almasenes = Tabla_Busqueda(m_almasenes, Tablas.Almasenes)
        t_tecnicos = Tabla_Busqueda(m_tecnicos, Tablas.Tecnicos)
        t_herramientas = Tabla_Busqueda(m_herramientas, Tablas.Herramientas)
        t_empresas = Tabla_Busqueda(m_empresas, Tablas.Empresas)

        self._lista_tablas = {
            str(m_talleres):t_talleres,
            str(m_almasenes):t_almasenes,
            str(m_tecnicos):t_tecnicos,
            str(m_herramientas):t_herramientas,
            str(m_empresas):t_empresas,
            }

        self._lista_formularios = {
            t_talleres:Objetos.Talleres,
            t_almasenes:Objetos.Almasenes,
            t_tecnicos:Objetos.Tecnicos,
            t_herramientas:Objetos.Herramientas,
            t_empresas:Objetos.Empresas,
            }

    def _actualisar_tablas(self):
        for tabla in self._lista_formularios:
            tabla.buscar()

    def _preparar_formulario(funcion):
        def proceso(self, evento=None):
            if not self._formulario is None:
                self._formulario.vp.destroy()
            tabla = self._lista_tablas[str(self.libreta.select())]
            funcion(self, tabla)
        return proceso

    @seguro
    @_preparar_formulario
    def modificar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        llave = self._lista_formularios[tabla](None).llave_base

        id = int(fila[llave]) if fila and fila[llave] else None
        self._formulario = self._lista_formularios[tabla](self.marco, id)

    @seguro
    @_preparar_formulario
    def borrar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

    def guardar(self):
        if self._formulario.guardar():
            self._actualisar_tablas()

    @_preparar_formulario
    def cancelar(self, tabla):
        self._actualisar_tablas()


class Control_Clientes(Ventana):
    archivo_gui = 'C_Control_Clientes'
    _formulario = None

    def __init__(self, master):
        self.master = master
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.marco_clientes = self.gui.get_object('__marco_clientes__')
        self.marco = self.gui.get_object('__marco__')
        self._tablas()
        self._actualisar_tablas()

    def _tablas(self):
        self._tabla_clientes = Tabla_Busqueda(self.marco_clientes, Tablas.Clientes)

    def _actualisar_tablas(self):
        self._tabla_clientes.buscar()

    def _preparar_formulario(funcion):

        def proceso(self, evento=None):
            if not self._formulario is None:
                self._formulario.vp.destroy()

            tabla = self._tabla_clientes

            funcion(self, tabla)

        return proceso

    @seguro
    @_preparar_formulario
    def modificar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        llave = Objetos.Clientes(None).llave_base
        id = int(fila[llave]) if fila else fila
        self._formulario = Objetos.Clientes(self.marco, id)

    @seguro
    @transaccion
    @_preparar_formulario
    def borrar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        if not fila: return
        llave = Objetos.Entidades(None).llave_primaria
        id = int(fila[llave])
        self._formulario = Objetos.Entidades(None, id)
        self._formulario.borrar()
        self._actualisar_tablas()


    def guardar(self):
        if self._formulario:
            self._formulario.guardar()
            self._actualisar_tablas()

    @_preparar_formulario
    def cancelar(self, tabla):
        self._actualisar_tablas()


class Control_Entradas(Ventana):
    archivo_gui = 'C_Control_Entradas'
    _formulario = None

    def __init__(self, master):
        self.master = master
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.marco_equipos = self.gui.get_object('__marco_equipos__')
        self.marco = self.gui.get_object('__marco__')
        self._tablas()
        self._actualisar_tablas()

    def _tablas(self):
        self.tabla = Tabla_Busqueda(self.marco_equipos, Tablas.Entradas, 'C_Tabla_Busqueda_Entradas')
        self.tabla.gui.create_variable('estado').set(0)

    def _actualisar_tablas(self):
        self.tabla.buscar()

    def _preparar_formulario(funcion):
        def proceso(self, evento=None):
            if not self._formulario is None:
                self._formulario.vp.destroy()

            tabla = self.tabla

            funcion(self, tabla)

        return proceso

    @seguro
    @transaccion
    @_preparar_formulario
    def imprimir_entrada(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

        id = int(fila['idEntradas']) if fila else fila

        rep = Reportes.Entradas(condicion={'idEntradas':id})
        Reportes.abrirReporte(rep, 'entradas.xsl')

    @seguro
    @transaccion
    @_preparar_formulario
    def imprimir_listado(self, tabla):
        rep = Reportes.Trabajos(condicion={'estado':0})
        with open('listado.xml', 'w') as listado:
            listado.write(Reportes.reporte_xml_texto(rep))
        Reportes.abrirReporte(rep, 'listado.xsl')

    @seguro
    @transaccion
    @_preparar_formulario
    def modificar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        llave = Objetos.Objetos(None).llave_primaria
        id = int(fila[llave]) if fila else fila
        self._formulario = Objetos.Objetos(self.marco, id)

    @seguro
    @transaccion
    def _terminar(self, fila):
        llave = Formularios.Trabajos(None).llave_primaria
        f = Formularios.Trabajos(None, int(fila[llave]))
        f.bd[0]['estado'] = True
        f.guardar()


    @_preparar_formulario
    def terminar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        if fila:
            self._terminar(fila)
            self._actualisar_tablas()


    @seguro
    @_preparar_formulario
    def borrar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

    @seguro
    @transaccion
    def guardar(self, evento=None):
        self._formulario.guardar()
        self._actualisar_tablas()

    @_preparar_formulario
    def cancelar(self, tabla):
        self._actualisar_tablas()


class Historial_Entradas(Ventana):
    archivo_gui = 'C_Historial_Entradas'
    _formulario = None

    def __init__(self, master):
        self.master = master
        Ventana.__init__(self, self.master, self.archivo_gui)
        self.marco_equipos = self.gui.get_object('__marco_equipos__')
        self.marco = self.gui.get_object('__marco__')
        self._tablas()
        self._actualisar_tablas()

    def _tablas(self):
        self.tabla = Tabla_Busqueda(self.marco_equipos, Tablas.Entradas, 'C_Tabla_Busqueda_Entradas')
        self.tabla.gui.create_variable('estado').set(1)

    def _actualisar_tablas(self):
        self.tabla.buscar()

    def _preparar_formulario(funcion):
        def proceso(self, evento=None):
            if not self._formulario is None:
                self._formulario.vp.destroy()

            tabla = self.tabla

            funcion(self, tabla)

        return proceso

    @seguro
    @transaccion
    @_preparar_formulario
    def imprimir_entrada(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

        id = int(fila['idEntradas']) if fila else fila

        rep = Reportes.Entradas(condicion={'idEntradas':id})
        Reportes.abrirReporte(rep, 'entradas.xsl')

    @seguro
    @transaccion
    @_preparar_formulario
    def modificar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

        llave = Objetos.Objetos(None).llave_primaria

        id = int(fila[llave]) if fila else fila

        self._formulario = Objetos.Objetos(self.marco, id)

    @seguro
    @transaccion
    def _reabrir(self, fila):
        llave = Formularios.Trabajos(None).llave_primaria
        f = Formularios.Trabajos(None, int(fila[llave]))
        f.bd[0]['estado'] = False
        f.guardar()


    @_preparar_formulario
    def reabrir(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None
        if fila:
            self._reabrir(fila)
            self._actualisar_tablas()


    @seguro
    @_preparar_formulario
    def borrar(self, tabla):
        fila = tabla.arbol.seleccion()[0] if len(tabla.arbol.seleccion()) > 0 else None

    @seguro
    @transaccion
    def guardar(self, evento=None):
        self._formulario.guardar()
        self._actualisar_tablas()

    @_preparar_formulario
    def cancelar(self, tabla):
        self._actualisar_tablas()


class Entrada_Taller(Ventana):
    archivo_gui = 'C_Entrada_Taller'

    def __init__(self, master):
        self.master = master
        Ventana.__init__(self, self.master, self.archivo_gui)
        self._crear_campos()

    @transaccion
    def _crear_campos(self, evento=None):
        self.marco_clientes = self.gui.get_object('__marco_clientes__')
        self.marco_equipos = self.gui.get_object('__marco_equipos__')
        self.clientes = Tabla_Busqueda(
            self.marco_clientes,
            Tablas.Clientes,
            archivo_gui='C_Tabla_Busqueda_Clientes',
            clienteNuevo=self.clienteNuevo)
        self.equipos = Tablas.Equipos_Entrada(self.marco_equipos, None)

    def _crear_equipo(self, fila, cliente):
        objeto = Formularios.Objetos(None)
        objeto.bd += {'nombre':fila['Equipo']}
        objeto.guardar()
        log.debug('idObjeto {}'.format(objeto.id_primario))

        especificaciones = Plantillas.Especificaciones(None, objeto.id_primario)
        especificaciones.gui.create_variable('marca').set(fila['Marca'])
        especificaciones.gui.create_variable('modelo').set(fila['Modelo'])
        especificaciones.gui.create_variable('serial').set(fila['Serial'])
        especificaciones.gui.create_variable('descripcion').set(fila['Descripcion'])
        especificaciones.guardar()

        equipo = Formularios.Equipos(None)
        equipo.bd += {'idObjetos':objeto.id_primario, 'idClietnes':cliente}
        equipo.guardar()

        return equipo.id_primario

    def _proceso(funcion):
        log.debug('Creando wraper _proceso para funcion {}'.format(funcion))

        def proceso(self, *arg):
            log.debug('Iniciando un _proceso para la funcion {}'.format(funcion))
            r = funcion(self, *arg)

            if r:
                rep = Reportes.Entradas(condicion={'idEntradas':self.idEntrada})
                Reportes.abrirReporte(rep, 'entradas.xsl')
                messagebox.showinfo(title='Guardado Exitoso', message='La entrada ha sido creada con el id {}'.format(self.idEntrada), parent=self.master)
                log.info('La entrada ha sido creada con el id {}'.format(self.idEntrada))
                self.vp.destroy()

            else:
                messagebox.showerror(title='Error al Guardar', message='La Entrada no pudo ser Creada', parent=self.master)
                log.error('La Entrada no pudo ser Creada, guarde los datos en otra parte(Ej. Imprima la pantalla) y comuniquese con un administrador por ayuda')

            log.debug('Cerrando _proceso para la funcion {}'.format(funcion))

        return proceso

    @_proceso
    @seguro
    @transaccion
    def guardar(self, evento=None):
        # Requisitos
        if not len(self.clientes.arbol.seleccion()) > 0:
            messagebox.showwarning(title='Error al Guardar', message='Debe selecionar un cliente', parent=self.master)
            log.warning('Debe selecionar un cliente')
            return False

        if not len(self.equipos.bd) > 0:
            messagebox.showwarning(title='Error al Guardar', message='Debe ingresar equipos', parent=self.master)
            log.warning('Debe ingresar equipos')
            return False

        # informaciòn
        #~ empresa = self.empresas.seleccion()['idEmpresas']
        empresa = 1
        cliente = self.clientes.arbol.seleccion()[0]['idClientes']
        equipos = [self._crear_equipo(fila, cliente) for fila in self.equipos.bd]

        # crear entradas
        entradas = Formularios.Entradas(None)
        entradas.bd += {'idEmpresas':empresa, 'idClientes':cliente}
        entradas.guardar()
        self.idEntrada = entradas.id_primario

        # crear trabajos
        trabajos = Formularios.Trabajos(None)
        for equipo in equipos:
            trabajos.bd += {'idEntradas':entradas.id_primario, 'idEquipos':equipo}
        trabajos.guardar()

    def clienteNuevo(self):
        ventana = Toplevel(self.master)
        clienteNuevo = Objetos.Cliente_Nuevo(ventana)
