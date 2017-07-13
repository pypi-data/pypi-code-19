#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from os import path
import sys
import subprocess
import os
from tempfile import NamedTemporaryFile

from scet.libsa import Reporte
from scet.libsa import transaccion, ejecutar, seguro
from scet.bd_xml import Tabla
from scet.globales import *


log = logging.getLogger(__name__)

PDF = True
try:
    import lxml.etree as ET
    from lxml.etree import XSLT, parse
except ImportError:
    import xml.etree.ElementTree as ET
    PDF = False
try:
    from weasyprint import HTML, CSS, default_url_fetcher
except ImportError as err:
    PDF = False
    log.warning('Debido a {}, no se puede exportar a pdf, \
    usando exportanción a html por defecto'.format(err))


class Reporte:
    """Objeto que representa un reporte de la BD,
    exportado a una extructura xml, en la que cada objeto reporte representa
    un registro de una tabla y contiene "hijos", reportes de tablas que dependen de esta,
    y "padres", o reportes de tablas de la que esta depende."""

    _nombreTabla = ''

    _hijos = ()
    hijos = []

    _padres = ()
    padres = []

    condicion = {}
    columnas = ('*')
    limite = 100

    def __init__(self, condicion=False, columnas=('*'), limite=100):
        self.condicion = condicion
        self.columnas = columnas
        self.limite = limite
        self.bd = Tabla(self._nombreTabla, OBTENER_BD())
        self._infomacionBasica()
        self._actualisarTablas()

    @property
    def xml(self):
        resultado= []
        objetos = self.bd.reporte
        for objeto, padres, hijos in zip(objetos, self.padres, self.hijos):
            for padre in padres:
                for miembro in padre.xml:
                    objeto.append(miembro)
                    #~ for elemento in miembro:
                        #~ objeto.append(elemento)
            for hijo in hijos:
                for miembro in hijo.xml:
                    objeto.append(miembro)
            resultado.append(objeto)
        return resultado

    @transaccion
    def _infomacionBasica(self, evento=None):
        self.bd.seleccionar_bd(condicion=False)
        self.llavesPrimaria = self.bd.llaves_primarias[0]
        self.llavesExtranjeras = self.bd.llaves_extranjeras

    @transaccion
    def _actualisarTablas(self, evento=None):
        self.bd.seleccionar_bd(self.columnas, self.condicion, self.limite)
        log.debug('Iniciando: {}'.format(self._nombreTabla))
        self._iniciarHijos()
        self._iniciarPadres()
        log.debug('Terminando: {}'.format(self._nombreTabla))

    def _iniciarHijos(self):
        self.hijos = []
        for fila in self.bd:
            objeto = []
            for hijo in self._hijos:
                objeto.append(hijo(condicion={self.llavesPrimaria:fila[self.llavesPrimaria]}))
            self.hijos.append(objeto)
        #~ log.debug('Hijos: {}'.format(self.hijos))

    def _iniciarPadres(self):
        self.padres = []
        for fila in self.bd:
            objeto = []
            for padre, llave in zip(self._padres, self.llavesExtranjeras):
                objeto.append(padre(condicion=({llave:fila[llave]} if fila[llave] else {})))
            self.padres.append(objeto)
        #~ log.debug('Padres: {}'.format(self.padres))


# entidades
class Caracteristicas(Reporte):
    _nombreTabla = 'Caracteristicas'

class Contacto(Reporte):
    _nombreTabla = 'Contacto'

class Informacion_Fiscal(Reporte):
    _nombreTabla = 'Informacion_Fiscal'

class Entidades(Reporte):
    _nombreTabla = 'Entidades'
    _hijos = (Caracteristicas, Contacto, Informacion_Fiscal)


# objetos
class Especificaciones(Reporte):
    _nombreTabla = 'Especificaciones'

class Objetos(Reporte):
    _nombreTabla = 'Objetos'
    _hijos = (Especificaciones,)


# ubicaciones
class Descripciones(Reporte):
    _nombreTabla = 'Descripciones'
    _hijos = ()

class Ubicaciones(Reporte):
    _nombreTabla = 'Ubicaciones'
    _hijos = (Descripciones,)


# clientes
class Equipos(Reporte):
    _nombreTabla = 'Equipos'
    _padres = (Objetos,)

class Clientes(Reporte):
    _nombreTabla = 'Clientes'
    _padres = (Entidades,)


# recursos
class Tecnicos(Reporte):
    _nombreTabla = 'Tecnicos'
    _padres = (Entidades,)

class Herramientas(Reporte):
    _nombreTabla = 'Herramientas'
    _padres = (Objetos,)

class Talleres(Reporte):
    _nombreTabla = 'Talleres'
    _padres = (Ubicaciones,)

class Almasenes(Reporte):
    _nombreTabla = 'Almasenes'
    _padres = (Ubicaciones,)

class Empresas(Reporte):
    _nombreTabla = 'Empresas'
    _padres = (Entidades,)


# Entradas
class Acciones(Reporte):
    _nombreTabla = 'Acciones'
    _padres = (Tecnicos, Herramientas)

class Trabajos(Reporte):
    _nombreTabla = 'Trabajos'
    _padres = (Equipos, Talleres, Almasenes)
    _hijos = (Acciones,)

class Entradas(Reporte):
    _nombreTabla = 'Entradas'
    _padres = (Clientes, Empresas)
    _hijos = (Trabajos,)


# funciones
def reporte_xml_texto(reporte):
    def itinerador(reporte, p=0, texto=''):
        e = ' '*4
        s = '\n'
        for objeto in reporte:
            if type(objeto) in (list, ET._Element if PDF else ET.Element) and len(objeto) > 0:
                texto += '{}{}{}'.format(e*p, '<{}>'.format(objeto.tag if type(objeto) is type(ET.Element('t')) else 'LISTA'), s)
                texto = itinerador(objeto, p+1, texto)
                texto += '{}{}{}'.format(e*p, '</{}>'.format(objeto.tag if type(objeto) is type(ET.Element('t')) else 'LISTA'), s)
            else:
                texto += '{}<{}>{}</{}>{}'.format(e*p, objeto.tag, objeto.text, objeto.tag, s)
        return texto
    texto = '<Reporte>\n'
    texto = itinerador(reporte.xml, 1, texto)
    texto += '</Reporte>'
    return texto

def reporte_xml(reporte, archivo, xslt):
    arbol = ET.Element('Reporte')
    for objeto in reporte.xml:
        arbol.append(objeto)

    declaracion = ET.tostring(ET.PI('xml', 'version="1.0" encoding="{}"'.format('UTF-8' if sys.platform.startswith('linux') else 'ISO-8859-1')), encoding='unicode')
    estilo = ET.tostring(ET.PI('xml-stylesheet', 'type="text/xsl" href="{}"'.format(xslt)), encoding='unicode')
    rais = ET.tostring(arbol, encoding='unicode')

    archivo.write(declaracion)
    archivo.write(estilo)
    archivo.write(rais)

    return archivo

def reporte_pdf(reporte, archivo, xslt):
    xslt = XSLT(parse(xslt))

    arbol = ET.Element('Reporte')
    for objeto in reporte.xml:
        arbol.append(objeto)

    base = '"File://{}/"'.format(CARPETA_TRABAJO)

    html = HTML(tree=xslt(arbol, base=base))
    html.write_pdf(target=archivo)

    return archivo

def abrirReporte(reporte, xslt):
    if PDF:
        xslt = os.path.join(CARPETA_TRABAJO, xslt)
        archivo = NamedTemporaryFile(suffix='.pdf', delete=False)
        archivo = reporte_pdf(reporte, archivo, xslt)
    else:
        archivo = open(os.path.join(CARPETA_TRABAJO, 'reporte.xml'), 'w')
        archivo = reporte_xml(reporte, archivo, xslt)
    nombre = archivo.name
    log.debug('creando archivo temporal {}, existe {}'.format(nombre, os.path.isfile(nombre)))
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', nombre])
    if sys.platform.startswith('win'):
        os.startfile(nombre)
    archivo.close()
