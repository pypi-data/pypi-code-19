#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time
import datetime
import copy
from re import search
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import sql
import sql.operators
import sqlite3
import pymysql

from scet.globales import *

log = logging.getLogger(__name__)


class Tabla():
    """Clase de ayuda para importar y exportar informacion entre python, Base de Datos SQL y XML"""


    class fila(dict):
        def __init__(self, padre, pos):
            #"padre" es el objeto 'Tabla' al que pertenece la fila y "pos" su posicion de fila
            self.padre = padre
            self.pos = pos

        def __getitem__(self, llave):
            return dict.__getitem__(self, llave)

        def __setitem__(self, llave, valor):
            #sinplificar el espacio de nombre
            columnas = self.padre.columnas
            filas = self.padre.filas
            pos = self.pos

            #Verificar que no se modifico una columna que no existente
            if llave in columnas:
                #cambiar valor local
                dict.__setitem__(self, llave, valor)

                #Borrar fila modificada
                filas.remove(filas[pos])

                #Insertar nueva fila con el valor actualisado
                filas.insert(pos, tuple([self[col] for col in columnas]))

            else:
                msg = '''Solo se pueden modificar columnas existentes, use "agregar_columna"
 para agregar una columna nueva'''
                err = TypeError(msg)
                log.error(err)
                raise err

        def __delitem__(self, llave):
            #sinplificar el espacio de nombre
            columnas = self.padre.columnas
            filas = self.padre.filas
            defecto = self.padre._col[columnas.index(llave)]['defecto']
            pos = self.pos

            #Verificar que no se modifico una columna que no existente
            if llave in columnas:
                #cambiar valor local
                dict.__setitem__(self, llave, defecto)

                #Borrar fila modificada
                filas.remove(filas[pos])

                #Insertar nueva fila con el valor actualisado
                filas.insert(pos, tuple([self[col] for col in columnas]))

        def borrar(self):
            '''Borra la fila de la que proviene'''
            del self.padre[self.pos]


    xml_declaration= '<?xml version="1.0" encoding="UTF-8"? standalone="yes"?>'

    def __init__(self, nombre='', coneccion=None):
        self._coneccion = None
        self._nombre = None
        self._col = []
        self._fil = []
        self.coneccion = coneccion
        self.nombre = nombre

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if isinstance(valor, bytes): self._nombre = str(valor, 'utf-8')
        elif isinstance(valor, str): self._nombre = valor
        else:
            msg = '''el nombre debe ser un str o bytes'''
            err = TypeError(msg)
            log.error(err)
            raise err

    @property
    def coneccion(self):
        return self._coneccion

    @coneccion.setter
    def coneccion(self, valor):
        '''Selecciona un objeto connecion que cumpla con el estandar DB API 2.0'''
        if isinstance(valor, sqlite3.Connection):
            # Set SQL style to use ? instead of %s
            sql.Flavor.set(sql.Flavor(paramstyle='qmark'))
            log.debug('Base de Datos es sqlite3, cambiando paramstyle a qmark')
        elif isinstance(valor, pymysql.connections.Connection):
            sql.Flavor.set(sql.Flavor(paramstyle='format'))
            log.debug('Base de Datos es pymysql, cambiando paramstyle a python')
        elif valor is None:
            log.debug('Usando Tabla sin Base de Datos')
        else:
            log.debug('Base de Datos es desconocida ({})'.format(valor))
            sql.Flavor.set(sql.Flavor(paramstyle='format'))
        self._coneccion = valor

    @coneccion.deleter
    def coneccion(self):
        self._coneccion = None

    @property
    def filas(self):
        return self._fil

    @filas.setter
    def filas(self, valor):
        '''Las filas debe ser un contenedor con contenedores con igual cantidad de elementos que cantidad de columnas'''
        try:
            self._fil = [tuple(val[:len(self._col)]) for val in valor]
        except TypeError:
            self._fil = [tuple(valor[:len(self._col)])]

    @property
    def columnas(self):
        return [col['campo'] for col in self._col]

    @property
    def valores(self):
        l = []
        n = len(self.filas)

        for nfila in range(n):
            a = self.fila(self, nfila)
            p = 0
            for col in self._col:
                dict.__setitem__(a, col['campo'], self.filas[nfila][p])
                p += 1
            l.append(a)

        return tuple(l)

    @property
    def llaves_primarias(self):
        return [col['campo'] for col in self._col if col['llave'] == 'PRI']

    @property
    def llaves_extranjeras(self):
        return [col['campo'] for col in self._col if col['llave'] == 'MUL']

    def __getitem__(self, llave):
        if type(llave) is int:
            if llave >= len(self.valores):
                fila = self.fila(self, llave)
                for col in self._col:
                    dict.__setitem__(fila, col['campo'], col['defecto'])
                return fila
            else:
                return self.valores[llave]
        elif type(llave) is slice:
            return self.valores[llave]
        else:
            msg = '''La llave debe ser int o slice'''
            err = TypeError(msg)
            log.error(err)
            raise err

    def __delitem__(self, llave):
        if type(llave) in (int, slice):
            del self.filas[llave]
        elif type(llave) is self.fila:
            del self.filas[llave.pos]
        else:
            msg = '''La llave debe ser int o slice o una fila de la tabla'''
            log.err(msg)
            raise TypeError(msg)

    def __setitem__(self, llave, valor):
        del self.filas[llave]
        self.__iadd__(valor, llave)

    def __add__(self, valor):
        tabla = self.copy()
        type(self).__iadd__(tabla, valor)
        return tabla

    def __radd__(self, valor):
        return self.__add__(valor)

    def __iadd__(self, valor, pos='final'):
        if pos == 'final': pos = len(self.filas)
        def obtener_fila(valor):
            fila = []
            for col in self._col:
                try:
                    fila.append(valor[col['campo']])
                except KeyError:
                    fila.append(col['defecto'])
                except TypeError:
                    try:
                        fila.append(valor[self._col.index(col)])
                    except IndexError:
                        fila.append(col['defecto'])
            return fila
        if type(valor) is type(self):
            filas = [obtener_fila(val) for val in valor]
            self.filas += filas
        else:
            filas = obtener_fila(valor)
            self.filas.insert(pos, filas)
        return self

    def __mul__(self, valor):
        tabla = self.copy()
        tabla.filas *= valor
        return tabla

    def __rmul__(self, valor):
        return self.__mul__(valor)

    def __imul__(self, valor):
        self.filas *= valor
        return self

    def __next__(self):
        if self.pos >= len(self.filas):
            raise StopIteration
        else:
            n = self.pos
            self.pos += 1
            return self.valores[n]

    def __iter__(self):
        self.pos = 0
        return self

    def __repr__(self):
        return '\n'.join((repr(self.nombre), repr(self._col), repr(self._fil)))

    def __str__(self):
        extra = 4

        n = 0
        t = 0
        max = 0
        for i in self._col:
            if len(i['campo']) > n: n = len(i['campo'])
            max += len(i['campo'])
            t += 1

        formato = ('{:'+str(n)+'}'+(' '*extra))*len(self._col)

        nombre = self.nombre.upper().center(max+(extra*t))

        valores = [col['campo'].upper().center(n) for col in self._col]

        cols = formato.format(*valores)

        sep = ((('-' * n)  + '-'*extra) * t)

        formato = ('{:'+str(n)+'}'+(' '*extra))*len(self._col)
        valores = []
        for fila in self._fil:
            v = []
            for valor in fila:
                if isinstance(valor,str): val = valor.ljust(n)
                elif isinstance(valor,bool): val = str(valor).center(n)
                elif isinstance(valor,int): val = str(valor).zfill(n)
                else: val = str(valor).center(n)
                v.append(val)
            valores.append(formato.format(*v))

        filas = '\n'.join(valores)

        return '\n'.join((sep, nombre, sep, cols, sep, filas, sep))

    def __len__(self):
        return len(self.filas)

    def index(self, valor):
        'Regresa un tuple con la pos de fila y columna la primera ocurrencia de valor'
        try:
            for fil in self.filas:
                if val in fil:
                    return (self.filas.index(fil), fil.index(valor))

        except IndexError:
            msg = '''El tuple de fila no se encontro,
Si estas intetando indexar una fila obtenida atraves de fila = tabla[x],
Prueba fila.pos'''
            err = IndexError(msg)
            log.error(err)
            raise err

    def copy(self, *slices):
        tabla = copy.copy(self)
        if not slices: slices = (None,None,None)
        tabla.filas = tabla.filas.__getitem__(slice(*slices))
        tabla.coneccion = self.coneccion
        return tabla

    def truncar(self):
        self._fil = []

    def agregar_columna(self, **arg):
        '''Agrega una columa a la tabla con la informacion dada o la de por defecto'''
        campo = arg.get('campo', str())
        tipo = arg.get('tipo', 'varchar')
        nulo = arg.get('nulo', 'YES')
        llave = arg.get('llave', str())
        defecto = arg.get('defecto', None)
        extra = arg.get('extra', str())
        self._col.append({'campo':campo,'tipo':tipo,'nulo':nulo,'llave':llave,'defecto':defecto,'extra':extra})
        return True

    def eliminar_columna(self, campo):
        '''Elimina una columna por nombre'''

        for col in self._col:
            if col['campo'] == campo:
                self._col.remove(col)

                return True
        return False

    def ver_columna(self, nombre_columna, *info):
        '''Regresa la informacion de una columna (tipo, nulo, llave, defecto, extra),
        Si se pide una caracteristica se regresa un valor, si se piden mas regresa un tuple,
        regresa None si no hay un acolumna'''
        for col in self._col:
            if col['campo'] == nombre_columna:
                if len(info) > 1:
                    i = [col[carac] for carac in info]

                else: i = col[info[0]]

                return i
        return None

    def ejecutar_proc(self, proc='', *args):
        '''Ejecua un procedimiento almasenado en la base de datos'''

        cur = self.cnx.cursor()

        return cur.callproc(proc, args)

    @property
    def reporte(self):
        '''Exporta los datos de la tabla a texto xml para reportes'''

        reporte = []
        for fil in self._fil:
            fila = ET.Element(self.nombre)
            for col in self._col:
                val = fil[self._col.index(col)]
                if isinstance(val, time.struct_time):
                    fila.append(_cambiar_time_a_xml(val, col['campo']))
                else:
                    columna = ET.SubElement(fila, col['campo'])
                    columna.text = str(val)
            reporte.append(fila)

        return reporte

    @property
    def xml(self):
        '''Exporta los datos de la tabla a texto xml'''
        arbol = ET.Element('tabla', nombre=self.nombre)

        #Agrega la estructura de los Encabesados y la Metadata
        columnas = ET.SubElement(arbol,'columnas')
        for col in self._col:
            tipo = col['tipo']
            nulo = col['nulo']
            llave = col['llave']
            defecto = col['defecto']
            extra = col['extra']

            if tipo is None: tipo = str(None)
            if nulo  is None: nulo = str(None)
            if llave is None: llave = str(None)
            if defecto is None: defecto = str(None)
            if extra is None: extra = str(None)

            columna = ET.SubElement(columnas, col['campo'],
            tipo = tipo,
            nulo = nulo,
            llave = llave,
            defecto = defecto,
            extra = extra,
            )

        #Agrega los Datos
        for fil in self._fil:
            fila = ET.SubElement(arbol, "fila")
            for col in self._col:
                val = fil[self._col.index(col)]
                if isinstance(val, time.struct_time):
                    fila.append(_cambiar_time_a_xml(val, col['campo']))
                else:
                    columna = ET.SubElement(fila, col['campo'])
                    columna.text = str(val)

        return ET.tostring(arbol, encoding='unicode')


    @xml.setter
    def xml(self, xml):
        """importar_xml(xml, tipo=('texto'/'archivo')
        Crear los datos de la tabla a base de un archivo xml"""

        arbol = ET.XML(xml)

        self.nombre = arbol.get('nombre', arbol.tag)

        #Llena la informacion de las columnas
        self._col = []
        for col in arbol.find('columnas'):
            campo = col.tag
            tipo = col.get('tipo')
            nulo = col.get('nulo')
            llave = col.get('llave')
            defecto = col.get('defecto')
            extra = col.get('extra')

            self._col.append({
            'campo':campo,
            'tipo':tipo,
            'nulo':nulo,
            'llave':llave,
            'defecto':defecto,
            'extra':extra,
            })

        #LLena la informacion de la filas
        fil = []

        for fila in arbol.findall('fila'):

            valores = []
            for n in range(len(self._col)):
                if self._col[n]['tipo'] in ('timestamp', 'datetime'):
                    valores.append(_cambiar_xml_a_time(fila[n]))
                else:
                    valores.append(self._cambiar_tipo_dato(fila[n].text, self._col[n]['tipo']))

            fil.append(valores)
        self.filas = fil


    def seleccionar_bd(self, columnas=('*',), condicion=True, cantidad=1000000):
        '''Importa los datos de la tabla desde la base de datos'''
        cur = self.coneccion.cursor()
        # Importar imformacion de las columnas
        self._col_bd(cur, columnas)
        # Importar filas, convertilas y guardarlas
        self._fila_bd(cur, condicion, cantidad)
        log.debug('Datos de {}: {}'.format(self.nombre, self))
        numero_fil = cur.rowcount
        cur.close()
        return numero_fil


    def insertar_bd(self, columnas=None):
        '''Exporta los datos de la tabla a la base de datos, regresa lasrowid por conveniencia'''

        cur = self.coneccion.cursor()

        tabla = sql.Table(self.nombre)
        cols = [col['campo'] for col in self._col]
        columnas = [sql.Column(tabla, c) for c in (cols if columnas is None else columnas)]
        datos = {'':None,}
        valores = [[fil[col.name] if not fil[col.name] in datos else datos[fil[col.name]] for col in columnas] for fil in self.valores]

        statement = tabla.insert(columnas, valores)

        query, datos = tuple(statement)
        query = query.replace('"', '`')
        log.debug('Ejecutando SQL: {}'.format((query, datos)))

        cur.execute(query, datos)

        return cur.lastrowid


    def actualisar_bd(self, columnas=None, llaves=[]):
        '''Realisa un UPDATE de todas la columnas usando automaticamente las llaves PRI para la clausula WHERE,
        las llaves no tienen que estar dentro de la columnas a actualisar,
        se pueden usar columnas propias como llaves a responsabilidad del usuario,
        regresa ROW_COUNT() por conveniencia'''

        #Busca las llaves PRI
        llaves = [i['campo'] for i in self._col if (i['llave'] == 'PRI')] + list(llaves)
        assert llaves, "La tabla no tiene ninguna columna PRI o columna que usar como llave"

        cur = self.coneccion.cursor()

        tabla = sql.Table(self.nombre)
        llaves = [sql.Column(tabla, l) for l in llaves]
        cols = [col['campo'] for col in self._col if col['tipo'] != "timestamp"]
        columnas = [sql.Column(tabla, c) for c in (cols if columnas is None else columnas)]

        for fil in self.valores:
            datos = {'':None,}
            valores = [fil[col.name] if not fil[col.name] in datos else datos[fil[col.name]] for col in columnas]
            condicion = sql.operators.And([sql.operators.Equal(l, fil[l.name]) for l in llaves])

            statement = tabla.update(columns = columnas, values=valores, where=condicion)

            query, datos = tuple(statement)
            query = query.replace('"', '`')
            log.debug('Ejecutando SQL: {}'.format((query, datos)))
            cur.execute(query, datos)

        return cur.rowcount


    def borrar_bd(self, llaves=[]):
        '''Realisa un DELETE usando automaticamente las llaves PRI para la clausula WHERE,
        se pueden usar columnas propias como llaves a responsabilidad del usuario,
        regresa ROW_COUNT() por conveniencia'''

        #Busca las llaves PRI
        llaves = [i['campo'] for i in self._col if (i['llave'] == 'PRI')] + list(llaves)
        assert llaves, "La tabla no tiene ninguna columna PRI o columna que usar como llave"

        cur = self.coneccion.cursor()

        tabla = sql.Table(self.nombre)
        llaves = [sql.Column(tabla, l) for l in llaves]

        for fil in self.valores:
            condicion = sql.operators.And([sql.operators.Equal(l, fil[l.name]) for l in llaves])
            statement = tabla.delete(where=condicion)
            query, datos = tuple(statement)
            query = query.replace('"', '`')
            log.debug('Ejecutando SQL: {}'.format((query, datos)))
            cur.execute(query, datos)

        return cur.rowcount


    def _col_bd(self, cur, cols=None):
        '''Busca y guarda los Metadatos de la tabla:
        primero intenta SHOW COLUMNS (MySql), si no intenta PRAGMA table_info (SQLite)'''
        # Para MySql
        try:
            meta = ('campo','tipo','nulo','llave','defecto','extra')
            cur.execute('SHOW COLUMNS FROM {}'.format(self.nombre))
            con = cur.fetchall()
            self._col = []
            for i in con:
                if (cols is None) or ('*' in cols and not i[0] in cols) or (i[0] in cols and not '*' in cols):
                    col = {}
                    for n in range(6):
                        atrib = i[n]
                        col[meta[n]] = atrib
                    self._col.append(col)
        # Para SQLite3
        except sqlite3.OperationalError:
            meta = ('id', 'campo', 'tipo', 'nulo', 'defecto', 'llave')
            log.warn('PRAGMA table_info({})'.format(self.nombre))
            cur.execute('PRAGMA table_info({})'.format(self.nombre))
            con1 = cur.fetchall()
            cur.execute('PRAGMA foreign_key_list({})'.format(self.nombre))
            con2 = cur.fetchall()
            self._col = []
            for columna in con1:
                # Verifica si se selecionaron columnas para imoportar
                if (cols is None) or ('*' in cols and not columna[1] in cols) or (columna[1] in cols and not '*' in cols):
                    col = {}
                    # Ir por cada par de tipo valor de metadata
                    for nombre, atrib in zip(meta, columna):
                        # Verificar si la columna es PRI, MUL o normal
                        if nombre == "llave":
                            col[nombre] = 'PRI' if bool(atrib) else None
                            for key in con2:
                                if key[4] == columna[1]:
                                    col[nombre] = 'MUL'
                        # Si la columna es nula
                        elif nombre == "nulo":
                            col[nombre] = not bool(atrib)
                        # Si la columna es el valor defecto, transformalo a un tipo de Python
                        elif nombre == "defecto":
                            log.debug('Columna defecto {}({})'.format(atrib, type(atrib)))
                            if type(atrib) is str:
                                if atrib == 'NULL':
                                    v = None
                                elif atrib.isdigit():
                                    v = int(atrib) if '.' in atrib else float(atrib)
                                else:
                                    v = atrib
                            if type(atrib) is type(None):
                                v = None
                            col[nombre] = v
                        # Si es otra columna
                        else:
                            col[nombre] = atrib
                    self._col.append(col)
        log.debug('Encontrada estructura de la tabla {}: {}'.format(self.nombre, self._col))

    def _fila_bd(self, cur, condicion=True, cantidad=1000000):
        '''Busca y escribe los datos de la Base de Datos'''

        tabla = sql.Table(self.nombre)
        columnas = [sql.Column(tabla, c['campo']) for c in self._col]

        #Crear la Condicion
        if condicion is False:
            condicion = sql.operators.Equal(1,2)
        elif condicion is True:
            condicion = sql.operators.And([])
        elif bool(condicion) is True:
            c = []
            for col in columnas:
                if condicion.get(col.name, None) is None: continue
                if isinstance(condicion.get(col.name), int):
                    c.append(sql.operators.Equal(col, condicion[col.name]))
                if isinstance(condicion.get(col.name), str):
                    c.append(sql.operators.Like(col, '%{}%'.format(condicion[col.name])))
            condicion = sql.operators.And(c)
        elif bool(condicion) is False:
            condicion = sql.operators.Equal(1,2)

        statement = tabla.select(*columnas)
        statement.where = condicion

        query, datos = tuple(statement)
        query = query.replace('"', '`')
        log.debug('Ejecutando SQL: {}'.format((query, datos)))
        cur.execute(query, datos)

        con = cur.fetchmany(cantidad)
        self._fil = con
        log.debug('Datos Importados directamente {}: {}'.format(self.nombre, repr(self._fil)))
        #~ self._convertir_datos()

    def _convertir_datos(self):
        tipo = [i['tipo'] for i in self._col]
        t = []
        for fil in self._fil:
            n = 0
            f = []
            for val in fil:
                if val is None:
                    f.append(None)
                else:
                    f.append(self._cambiar_tipo_dato(val,tipo[n]))
                n += 1
            t.append(tuple(f))
        self._fil = t

    def _cambiar_tipo_dato(self, valor, tipo):
        if isinstance(valor, bytes):
            valor = str(valor, 'utf-8')
        else:
            try:
                valor = str(valor)
            except Exception:
                msg = '''Valor debe ser bytes o str'''
                err = AttributeError(msg)
                log.error(err)
                raise err

        if valor == 'None':
            return None

        for p in tipos_variables:
            if search(tipos_variables[p], tipo):
                t = convercion_variables[p]
            else:
                try:
                    t = convercion_variables[tipo]
                except KeyError:
                    continue

            if t is str:
                return valor

            elif t is int:
                return int(valor,10)

            elif t is float:
                return float(valor)

            elif t is bool:
                return bool(int(valor))

            elif t is time:
                s = search('(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)', valor)
                return time.struct_time([int(s.group(n)) for n in range(1,7)] + [0]*3)

            elif t is datetime.timedelta:
                s = search('(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)', valor)
                A = int(s.group(1)) * 365
                M = int(s.group(2)) * 30
                D = int(s.group(3)) + M + A
                h = int(s.group(4)) * 3600
                m = int(s.group(5)) * 60
                s = int(s.group(6)) + h + m
                return datetime.timedelta(days=D, seconds=s)

            elif t is datetime.datetime:
                return datetime.datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')

            elif t is datetime.time:
                s = search('(\d\d):(\d\d):(\d\d)', valor)
                return datetime.time(hour=int(s.group(1)), minute=int(s.group(2)), second=int(s.group(3)))

            elif t is datetime.date:
                s = search('(\d\d\d\d)-(\d\d)-(\d\d)', valor)
                return datetime.date(year=int(s.group(1)), month=int(s.group(2)), day=int(s.group(3)))

            #Mas converciones a otros formatos

        return None

tipos_variables = {
    'int':'^(small|medium|big)?int(eger)?(\((\d+)\))?( unsigned)?( zerofill)?$',
    'bool':'^tinyint\(1\)$',
    'double':'^(double|real|float|decimal|numeric)(\((\d+)(,\d+)?\))?( unsigned)?( zerofill)?$',
    'date':'^date$',
    'time':'^time$',
    'datetime':'^datetime$',
    'timestamp':'^timestamp$',
    'varchar':'^(var)?char(\(\d+\))?$',
    'text':'^(tiny|medium|long)?(text|blob)( binary)?$',
    'set':'^(enum|set)\(.*\)$',
    }

convercion_variables = {
    'datetime':datetime.datetime,
    'date':datetime.date,
    'time':datetime.time,
    'timestamp':time,
    'varchar':str,
    'str':str,
    'char':str,
    'text':str,
    'blob':str,
    'enum':str,
    'set':str,
    'int':int,
    'double':float,
    'float':float,
    'real':float,
    'bool':bool,
    }

estructura_time = {
    0:'ano',
    1:'mes',
    2:'dia',
    3:'hora',
    4:'minuto',
    5:'segundo',
    6:'dia_semana',
    7:'dia_ano',
    8:'hora_de_verano',
    }

def _cambiar_time_a_xml(objeto_struct_time, tag):
    nodo = ET.Element(tag)

    for n in range(9):
        subnodo = ET.SubElement(nodo, estructura_time[n])
        subnodo.text = str(objeto_struct_time[n])

    return nodo


def _cambiar_xml_a_time(nodo):
    datos = [int(nodo[n].text) for n in range(9)]
    return time.struct_time(datos)


def _prueba():
    ###Crear Tabla
    personas = p = Tabla('personas')

    #Asignar Nombre, se usa para identificar la tabla cuando exportando a una BD o XML
    nombre = p.nombre
    p.nombre = nombre

    ##Agregar columnas
    p.agregar_columna(campo='id', tipo='int', llave='pri')
    p.agregar_columna(campo='nombre', tipo='str', defecto="Jhon")
    p.agregar_columna(campo='apellido', tipo='str', defecto="Doe")

    ###Manipulacion de Datos
    #Insertar
    print('Agregar los datos de diferentes formas')
    p += {'nombre':'wolfang','id':1,'apellido':'torres'}
    p = p + {'id':2, 'apellido':'torres', 'nombre':'wendy',}
    p = (3, 'carlos', 'molano') + p
    print(p)

    #Insertar una lina vacia llena los datos faltantes con el "defecto"
    print('insetar linea vacia')
    p += ()
    print(p)

    #Multiplicacion
    print('Tambien se puede multiplicar')
    p *= 3
    print(p)

    #Copiado
    print('las tablas se pueden copiar, use slice en la funcion de copia( tabla[a:b:c] => copy(a,b,c) )')
    c = p.copy(None,2)
    c.nombre = 'clientes'
    print(c)

    d = p.copy()
    d.nombre = 'pacientes'
    d.filas = d.filas[2]
    print(d)

    #Tambien puedes sumar dos copias
    e = c + d
    del c
    del d
    e.nombre = 'copiado'
    print(e)

    #Modificacion de una fila
    print('Modificar las filas de diferentes formas')
    p[1] = {'apellido':'molano', 'nombre':'carlos', 'id':3,}
    p[2] = [2, 'wendy', 'torres']
    print(p)

    #Modificar un registro
    print('Modificar los registros de diferentes formas')
    p[0]['id']=4
    p[1]['nombre']='juan'
    print(p)

    #Borrar
    print('Borrar las filas')
    del p[0]
    print(p)

    #Convertir al Defecto
    print('Borrar un registro lo convierte en el defecto')
    del p[1]['nombre']
    del p[1]['apellido']
    print(p)

    ###La tablas pueden ser operadas de diferentes formas
    ##Este es mas o menos el equivalente a:
    #UPDATE <tabla> SET nombre = CONCAT(nombre,' ',apellido), apellido = NULL WHERE id = 2
    print("UPDATE <tabla> SET nombre = CONCAT(nombre,' ',apellido), apellido = NULL WHERE id = 2")
    for fila in p:
        if fila['id'] == 2:
            fila['nombre'] += ' ' + fila['apellido']
            fila['apellido'] = None
    print(p)

    ##Este es mas o menos el equivalente a:
    #DELETE FROM <tabla> WHERE MOD(id,2) = 0 LIMIT 1
    print("DELETE FROM <tabla> WHERE MOD(id,2) = 0 LIMIT 1")
    n = 0
    nmax = 1
    for fila in p:
        if fila['id'] % 2 == 0:
            del p[fila]
            n += 1
            if n >= nmax: break
    print(p)


    ###Importacion y exportacion xml
    #Crear Tabla
    print()
    print('Importacion y exportacion xml')

    dir = 'tabla_xml.xml'
    compras = Tabla("Compras")
    compras.agregar_columna(campo="nombre_proveedor", tipo="varchar")
    compras.agregar_columna(campo="codigo_proveedor", tipo="varchar")
    compras.agregar_columna(campo="fecha", tipo="timestamp")
    compras.agregar_columna(campo="codigo", tipo="varchar")
    compras.agregar_columna(campo="cantidad", tipo="int")
    compras.agregar_columna(campo="pn1", tipo="float")
    compras.agregar_columna(campo="pvp1", tipo="float")

    compras += {'nombre_proveedor':'wolfang',
    'codigo_proveedor':'v24404292',
    'fecha':time.localtime(),
    'codigo':'abc',
    'cantidad':None,
    'pn1':10.0,
    'pvp1':12.0,
    }
    print(compras)

    ##Exportacion
    with open(dir, 'w') as archivo:
        archivo.write(compras.xml)

    ##Importacion
    f = Tabla()
    with open(dir, 'r') as archivo:
        f.xml = archivo.read()
    print(f)
    os.remove(dir)


if __name__ == '__main__':
    _prueba()
