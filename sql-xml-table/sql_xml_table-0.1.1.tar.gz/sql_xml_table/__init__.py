#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os
import time
import datetime
import copy
from re import search
import sqlite3
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import sql
import sql.operators
import pymysql


log = logging.getLogger(__name__)


class table(object):
    """Clase de ayuda para importar y exportar informacion entre python, Base de data SQL y XML"""

    class row(dict):

        def __init__(self, padre, pos):
            #"padre" es el objeto 'table' al que pertenece la row y "pos" su posicion de row
            self.padre = padre
            self.pos = pos

        def __getitem__(self, key):
            return dict.__getitem__(self, key)

        def __setitem__(self, key, valor):
            #sinplificar el espacio de name
            columns = self.padre.columns
            rows = self.padre.rows
            pos = self.pos
            #Verificar que no se modifico una column que no existente
            if key in columns:
                #convert valor local
                dict.__setitem__(self, key, valor)
                #remove row modificada
                rows.remove(rows[pos])
                #insert nueva row con el valor actualisado
                rows.insert(pos, tuple([self[col] for col in columns]))
            else:
                msg = '''Solo se pueden modificar columns existentes, use "add_column"'''
                err = TypeError(msg)
                log.error(err)
                raise err

        def __delitem__(self, key):
            #sinplificar el espacio de name
            columns = self.padre.columns
            rows = self.padre.rows
            default = self.padre._col[columns.index(key)]['default']
            pos = self.pos
            #Verificar que no se modifico una column que no existente
            if key in columns:
                #convert valor local
                dict.__setitem__(self, key, default)
                #remove row modificada
                rows.remove(rows[pos])
                #insert nueva row con el valor actualisado
                rows.insert(pos, tuple([self[col] for col in columns]))

        def remove(self):
            '''Borra la row de la que proviene'''
            del self.padre[self.pos]

    xml_declaration= '<?xml version="1.0" encoding="UTF-8"? standalone="yes"?>'

    def __init__(self, name='', conection=None):
        self._conection = None
        self._name = None
        self._col = []
        self._rows = []
        self.conection = conection
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, valor):
        if isinstance(valor, bytes): self._name = str(valor)
        elif isinstance(valor, str): self._name = valor
        else:
            msg = '''el name debe ser un str o bytes'''
            err = TypeError(msg)
            log.error(err)
            raise err

    @property
    def conection(self):
        return self._conection

    @conection.setter
    def conection(self, valor):
        '''Selecciona un objeto connecion que cumpla con el estandar DB API 2.0'''
        if isinstance(valor, sqlite3.Connection):
            # Set SQL style to use ? instead of %s
            sql.Flavor.set(sql.Flavor(paramstyle='qmark'))
            log.debug('Base de data es sqlite3, cambiando paramstyle a qmark')
        elif isinstance(valor, pymysql.connections.Connection):
            sql.Flavor.set(sql.Flavor(paramstyle='format'))
            log.debug('Base de data es pymysql, cambiando paramstyle a python')
        elif valor is None:
            log.debug('Usando table sin Base de data')
        else:
            log.debug('Base de data es desconocida ({})'.format(valor))
            sql.Flavor.set(sql.Flavor(paramstyle='format'))
        self._conection = valor

    @conection.deleter
    def conection(self):
        self._conection = None

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, valor):
        '''Las rows debe ser un contenedor con contenedores con igual cantidad de elementos que cantidad de columns'''
        try:
            self._rows = [tuple(val[:len(self._col)]) for val in valor]
        except TypeError:
            self._rows = [tuple(valor[:len(self._col)])]

    @property
    def columns(self):
        return [col['field'] for col in self._col]

    @property
    def values(self):
        l = []
        n = len(self.rows)
        for nrow in range(n):
            a = self.row(self, nrow)
            p = 0
            for col in self._col:
                dict.__setitem__(a, col['field'], self.rows[nrow][p])
                p += 1
            l.append(a)

        return tuple(l)

    @property
    def primary_key(self):
        return [col['field'] for col in self._col if col['key'] == 'PRI']

    @property
    def foreign_key(self):
        return [col['field'] for col in self._col if col['key'] == 'MUL']

    def __getitem__(self, key):
        if type(key) is int:
            if key >= len(self.values):
                row = self.row(self, key)
                for col in self._col:
                    dict.__setitem__(row, col['field'], col['default'])
                return row
            else:
                return self.values[key]
        elif type(key) is slice:
            return self.values[key]
        else:
            msg = '''La key debe ser int o slice'''
            err = TypeError(msg)
            log.error(err)
            raise err

    def __delitem__(self, key):
        if type(key) in (int, slice):
            del self.rows[key]
        elif type(key) is self.row:
            del self.rows[key.pos]
        else:
            msg = '''La key debe ser int o slice o una row de la table'''
            log.err(msg)
            raise TypeError(msg)

    def __setitem__(self, key, valor):
        del self.rows[key]
        self.__iadd__(valor, key)

    def __add__(self, valor):
        table = self.copy()
        type(self).__iadd__(table, valor)
        return table

    def __radd__(self, valor):
        return self.__add__(valor)

    def __iadd__(self, valor, pos='final'):
        if pos == 'final': pos = len(self.rows)
        def obtener_row(valor):
            row = []
            for col in self._col:
                try:
                    row.append(valor[col['field']])
                except KeyError:
                    row.append(col['default'])
                except TypeError:
                    try:
                        row.append(valor[self._col.index(col)])
                    except IndexError:
                        row.append(col['default'])
            return row
        if type(valor) is type(self):
            rows = [obtener_row(val) for val in valor]
            self.rows += rows
        else:
            rows = obtener_row(valor)
            self.rows.insert(pos, rows)
        return self

    def __mul__(self, valor):
        table = self.copy()
        table.rows *= valor
        return table

    def __rmul__(self, valor):
        return self.__mul__(valor)

    def __imul__(self, valor):
        self.rows *= valor
        return self

    def __next__(self):
        if self.pos >= len(self.rows):
            raise StopIteration
        else:
            n = self.pos
            self.pos += 1
            return self.values[n]

    def next(self):
        return type(self).__next__(self)

    def __iter__(self):
        self.pos = 0
        return self

    def __repr__(self):
        return '\n'.join((repr(self.name), repr(self._col), repr(self._rows)))

    def __str__(self):
        extra = 4
        n = 0
        t = 0
        max = 0
        for i in self._col:
            if len(i['field']) > n: n = len(i['field'])
            max += len(i['field'])
            t += 1
        format = ('{:'+str(n)+'}'+(' '*extra))*len(self._col)
        name = self.name.upper().center(max+(extra*t))
        values = [col['field'].upper().center(n) for col in self._col]
        cols = format.format(*values)
        sep = ((('-' * n)  + '-'*extra) * t)
        format = ('{:'+str(n)+'}'+(' '*extra))*len(self._col)
        values = []
        for row in self._rows:
            v = []
            for valor in row:
                if isinstance(valor,str): val = valor.ljust(n)
                elif isinstance(valor,bool): val = str(valor).center(n)
                elif isinstance(valor,int): val = str(valor).zfill(n)
                else: val = str(valor).center(n)
                v.append(val)
            values.append(format.format(*v))
        rows = '\n'.join(values)
        return '\n'.join((sep, name, sep, cols, sep, rows, sep))

    def __len__(self):
        return len(self.rows)

    def index(self, valor):
        'Regresa un tuple con la pos de row y column la primera ocurrencia de valor'
        try:
            for fil in self.rows:
                if val in fil:
                    return (self.rows.index(fil), fil.index(valor))

        except IndexError:
            msg = '''El tuple de row no se encontro,
Si estas intetando indexar una row obtenida atraves de row = table[x],
Prueba row.pos'''
            err = IndexError(msg)
            log.error(err)
            raise err

    def copy(self, *slices):
        table = copy.copy(self)
        if not slices: slices = (None,None,None)
        table.rows = table.rows.__getitem__(slice(*slices))
        table.conection = self.conection
        return table

    def truncar(self):
        self._rows = []

    def add_column(self, **arg):
        '''Agrega una columa a la table con la informacion dada o la de por default'''
        field = arg.get('field', str())
        type = arg.get('type', 'varchar')
        null = arg.get('null', 'YES')
        key = arg.get('key', str())
        default = arg.get('default', None)
        extra = arg.get('extra', str())
        self._col.append({'field':field,'type':type,'null':null,'key':key,'default':default,'extra':extra})
        return True

    def remove_column(self, field):
        '''Elimina una column por name'''
        for col in self._col:
            if col['field'] == field:
                self._col.remove(col)
                return True
        return False

    def ver_column(self, name_column, *info):
        '''Regresa la informacion de una column (type, null, key, default, extra),
        Si se pide una caracteristica se regresa un valor, si se piden mas regresa un tuple,
        regresa None si no hay un acolumn'''
        for col in self._col:
            if col['field'] == name_column:
                if len(info) > 1:
                    i = [col[carac] for carac in info]
                else: i = col[info[0]]
                return i
        return None

    def execute_procedure(self, proc='', *args):
        '''Ejecua un procedimiento almasenado en la base de data'''
        cur = self.cnx.cursor()
        return cur.callproc(proc, args)

    @property
    def report(self):
        '''Exporta los data de la table a texto xml para reports'''
        report = []
        for fil in self._rows:
            row = ET.Element(self.name)
            for col in self._col:
                val = fil[self._col.index(col)]
                if isinstance(val, time.struct_time):
                    row.append(_convert_time_a_xml(val, col['field']))
                else:
                    column = ET.SubElement(row, col['field'])
                    column.text = str(val)
            report.append(row)
        return report

    @property
    def xml(self):
        '''Exporta los data de la table a texto xml'''
        arbol = ET.Element('table', name=self.name)
        #Agrega la estructura de los Encabesados y la Metadata
        columns = ET.SubElement(arbol,'columns')
        for col in self._col:
            type = col['type']
            null = col['null']
            key = col['key']
            default = col['default']
            extra = col['extra']
            #Write Null column data as "None"
            if type is None: type = str(None)
            if null  is None: null = str(None)
            if key is None: key = str(None)
            if default is None: default = str(None)
            if extra is None: extra = str(None)
            column = ET.SubElement(
                columns,
                col['field'],
                type = type,
                null = null,
                key = key,
                default = default,
                extra = extra,
                )
        #Agrega los data
        for fil in self._rows:
            row = ET.SubElement(arbol, "row")
            for col in self._col:
                val = fil[self._col.index(col)]
                if isinstance(val, time.struct_time):
                    row.append(_convert_time_a_xml(val, col['field']))
                else:
                    column = ET.SubElement(row, col['field'])
                    column.text = str(val)
        return ET.tostring(arbol, encoding='unicode')

    @xml.setter
    def xml(self, xml):
        """Pass a xml string in order to import all its data"""
        arbol = ET.XML(xml)
        self.name = arbol.get('name', arbol.tag)
        #Llena la informacion de las columns
        self._col = []
        for col in arbol.find('columns'):
            field = col.tag
            type = col.get('type')
            null = col.get('null')
            key = col.get('key')
            default = col.get('default')
            extra = col.get('extra')
            self._col.append({
                'field':field,
                'type':type,
                'null':null,
                'key':key,
                'default':default,
                'extra':extra,
                })
        #LLena la informacion de la rows
        fil = []
        for row in arbol.findall('row'):
            values = []
            for n in range(len(self._col)):
                if self._col[n]['type'] in ('timestamp', 'datetime'):
                    values.append(_convert_xml_a_time(row[n]))
                else:
                    values.append(self._convert_type_dato(row[n].text, self._col[n]['type']))
            fil.append(values)
        self.rows = fil

    def select_db(self, columns=('*',), condicion=True, cantidad=1000000):
        '''Importa los data de la table desde la base de data'''
        cur = self.conection.cursor()
        # Importar imformacion de las columns
        self._col_db(cur, columns)
        # Importar rows, convertilas y guardarlas
        self._row_db(cur, condicion, cantidad)
        log.debug('data de {}: {}'.format(self.name, self))
        numero_rows = cur.rowcount
        cur.close()
        return numero_rows

    def insert_db(self, columns=None):
        '''Exporta los data de la table a la base de data, regresa lasrowid por conveniencia'''
        cur = self.conection.cursor()
        table = sql.Table(self.name)
        cols = [col['field'] for col in self._col]
        columns = [sql.Column(table, c) for c in (cols if columns is None else columns)]
        data = {'':None,}
        values = [[fil[col.name] if not fil[col.name] in data else data[fil[col.name]] for col in columns] for fil in self.values]
        statement = table.insert(columns, values)
        query, data = tuple(statement)
        query = query.replace('"', '`')
        log.debug('Ejecutando SQL: {}'.format((query, data)))
        cur.execute(query, data)
        return cur.lastrowid

    def update_db(self, columns=None, keys=[]):
        '''Realisa un UPDATE de todas la columns usando automaticamente las keys PRI para la clausula WHERE,
        las keys no tienen que estar dentro de la columns a update,
        se pueden usar columns propias como keys a responsabilidad del usuario,
        regresa ROW_COUNT() por conveniencia'''
        #Busca las keys PRI
        keys = [i['field'] for i in self._col if (i['key'] == 'PRI')] + list(keys)
        assert keys, "La table no tiene ninguna column PRI o column que usar como key"
        cur = self.conection.cursor()
        table = sql.Table(self.name)
        keys = [sql.Column(table, l) for l in keys]
        cols = [col['field'] for col in self._col if col['type'] != "timestamp"]
        columns = [sql.Column(table, c) for c in (cols if columns is None else columns)]
        for fil in self.values:
            data = {'':None,}
            values = [fil[col.name] if not fil[col.name] in data else data[fil[col.name]] for col in columns]
            condicion = sql.operators.And([sql.operators.Equal(l, fil[l.name]) for l in keys])
            statement = table.update(columns = columns, values=values, where=condicion)
            query, data = tuple(statement)
            query = query.replace('"', '`')
            log.debug('Ejecutando SQL: {}'.format((query, data)))
            cur.execute(query, data)
        return cur.rowcount

    def remove_db(self, keys=[]):
        '''Realisa un DELETE usando automaticamente las keys PRI para la clausula WHERE,
        se pueden usar columns propias como keys a responsabilidad del usuario,
        regresa ROW_COUNT() por conveniencia'''
        #Busca las keys PRI
        keys = [i['field'] for i in self._col if (i['key'] == 'PRI')] + list(keys)
        assert keys, "La table no tiene ninguna column PRI o column que usar como key"
        cur = self.conection.cursor()
        table = sql.Table(self.name)
        keys = [sql.Column(table, l) for l in keys]
        for fil in self.values:
            condicion = sql.operators.And([sql.operators.Equal(l, fil[l.name]) for l in keys])
            statement = table.delete(where=condicion)
            query, data = tuple(statement)
            query = query.replace('"', '`')
            log.debug('Ejecutando SQL: {}'.format((query, data)))
            cur.execute(query, data)
        return cur.rowcount

    def _col_db(self, cur, cols=None):
        '''Busca y guarda los Metadata de la table:
        primero intenta SHOW COLUMNS (MySql), si no intenta PRAGMA table_info (SQLite)'''
        # Para MySql
        try:
            meta = ('field','type','null','key','default','extra')
            cur.execute('SHOW COLUMNS FROM {}'.format(self.name))
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
            meta = ('id', 'field', 'type', 'null', 'default', 'key')
            log.warn('PRAGMA table_info({})'.format(self.name))
            cur.execute('PRAGMA table_info({})'.format(self.name))
            con1 = cur.fetchall()
            cur.execute('PRAGMA foreign_key_list({})'.format(self.name))
            con2 = cur.fetchall()
            self._col = []
            for column in con1:
                # Verifica si se selecionaron columns para imoportar
                if (cols is None) or ('*' in cols and not column[1] in cols) or (column[1] in cols and not '*' in cols):
                    col = {}
                    # Ir por cada par de type valor de metadata
                    for name, atrib in zip(meta, column):
                        # Verificar si la column es PRI, MUL o normal
                        if name == "key":
                            col[name] = 'PRI' if bool(atrib) else None
                            for key in con2:
                                if key[4] == column[1]:
                                    col[name] = 'MUL'
                        # Si la column es nula
                        elif name == "null":
                            col[name] = not bool(atrib)
                        # Si la column es el valor default, transformalo a un type de Python
                        elif name == "default":
                            log.debug('column default {}({})'.format(atrib, type(atrib)))
                            if type(atrib) is str:
                                if atrib == 'NULL':
                                    v = None
                                elif atrib.isdigit():
                                    v = int(atrib) if '.' in atrib else float(atrib)
                                else:
                                    v = atrib
                            if type(atrib) is type(None):
                                v = None
                            col[name] = v
                        # Si es otra column
                        else:
                            col[name] = atrib
                    self._col.append(col)
        log.debug('Encontrada estructura de la table {}: {}'.format(self.name, self._col))

    def _row_db(self, cur, condicion=True, cantidad=1000000):
        '''Busca y escribe los data de la Base de data'''
        table = sql.Table(self.name)
        columns = [sql.Column(table, c['field']) for c in self._col]
        #Crear la Condicion
        if condicion is False:
            condicion = sql.operators.Equal(1,2)
        elif condicion is True:
            condicion = sql.operators.And([])
        elif bool(condicion) is True:
            c = []
            for col in columns:
                if condicion.get(col.name, None) is None: continue
                if isinstance(condicion.get(col.name), int):
                    c.append(sql.operators.Equal(col, condicion[col.name]))
                if isinstance(condicion.get(col.name), str):
                    c.append(sql.operators.Like(col, '%{}%'.format(condicion[col.name])))
            condicion = sql.operators.And(c)
        elif bool(condicion) is False:
            condicion = sql.operators.Equal(1,2)
        statement = table.select(*columns)
        statement.where = condicion
        query, data = tuple(statement)
        query = query.replace('"', '`')
        log.debug('Ejecutando SQL: {}'.format((query, data)))
        cur.execute(query, data)
        con = cur.fetchmany(cantidad)
        self._rows = con
        log.debug('data Importados directamente {}: {}'.format(self.name, repr(self._rows)))
        #~ self._convert_data()

    def _convert_data(self):
        type = [i['type'] for i in self._col]
        t = []
        for fil in self._rows:
            n = 0
            f = []
            for val in fil:
                if val is None:
                    f.append(None)
                else:
                    f.append(self._convert_type_dato(val,type[n]))
                n += 1
            t.append(tuple(f))
        self._rows = t

    def _convert_type_dato(self, valor, type):
        if isinstance(valor, bytes):
            valor = str(valor)
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

        for p in types_variables:
            if search(types_variables[p], type):
                t = convercion_variables[p]
            else:
                try:
                    t = convercion_variables[type]
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

            #Mas converciones a otros formats

        return None


types_variables = {
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

def _convert_time_a_xml(objeto_struct_time, tag):
    nodo = ET.Element(tag)

    for n in range(9):
        subnodo = ET.SubElement(nodo, estructura_time[n])
        subnodo.text = str(objeto_struct_time[n])

    return nodo


def _convert_xml_a_time(nodo):
    data = [int(nodo[n].text) for n in range(9)]
    return time.struct_time(data)



def _prueba():
    ###Crear table
    personas = p = table('personas')

    #Asignar name, se usa para identificar la table cuando exportando a una db o XML
    name = p.name
    p.name = name

    ##add columns
    p.add_column(field='id', type='int', key='pri')
    p.add_column(field='name', type='str', default="Jhon")
    p.add_column(field='apellido', type='str', default="Doe")

    ###Manipulacion de data
    #insert
    print('add los data de diferentes formas')
    p += {'name':'wolfang','id':1,'apellido':'torres'}
    p = p + {'id':2, 'apellido':'torres', 'name':'wendy',}
    p = (3, 'carlos', 'molano') + p
    print(p)

    #insert una lina vacia llena los data faltantes con el "default"
    print('insetar linea vacia')
    p += ()
    print(p)

    #Multiplicacion
    print('Tambien se puede multiplicar')
    p *= 3
    print(p)

    #Copiado
    print('las tables se pueden copiar, use slice en la funcion de copia( table[a:b:c] => copy(a,b,c) )')
    c = p.copy(None,2)
    c.name = 'clientes'
    print(c)

    d = p.copy()
    d.name = 'pacientes'
    d.rows = d.rows[2]
    print(d)

    #Tambien puedes sumar dos copias
    e = c + d
    del c
    del d
    e.name = 'copiado'
    print(e)

    #Modificacion de una row
    print('Modificar las rows de diferentes formas')
    p[1] = {'apellido':'molano', 'name':'carlos', 'id':3,}
    p[2] = [2, 'wendy', 'torres']
    print(p)

    #Modificar un registro
    print('Modificar los registros de diferentes formas')
    p[0]['id']=4
    p[1]['name']='juan'
    print(p)

    #remove
    print('remove las rows')
    del p[0]
    print(p)

    #convert al default
    print('remove un registro lo convierte en el default')
    del p[1]['name']
    del p[1]['apellido']
    print(p)

    ###La tables pueden ser operadas de diferentes formas
    ##Este es mas o menos el equivalente a:
    #UPDATE <table> SET name = CONCAT(name,' ',apellido), apellido = NULL WHERE id = 2
    print("UPDATE <table> SET name = CONCAT(name,' ',apellido), apellido = NULL WHERE id = 2")
    for row in p:
        if row['id'] == 2:
            row['name'] += ' ' + row['apellido']
            row['apellido'] = None
    print(p)

    ##Este es mas o menos el equivalente a:
    #DELETE FROM <table> WHERE MOD(id,2) = 0 LIMIT 1
    print("DELETE FROM <table> WHERE MOD(id,2) = 0 LIMIT 1")
    n = 0
    nmax = 1
    for row in p:
        if row['id'] % 2 == 0:
            del p[row]
            n += 1
            if n >= nmax: break
    print(p)


    ###Importacion y exportacion xml
    #Crear table
    print()
    print('Importacion y exportacion xml')

    dir = 'table_xml.xml'
    compras = table("Compras")
    compras.add_column(field="name_proveedor", type="varchar")
    compras.add_column(field="codigo_proveedor", type="varchar")
    compras.add_column(field="fecha", type="timestamp")
    compras.add_column(field="codigo", type="varchar")
    compras.add_column(field="cantidad", type="int")
    compras.add_column(field="pn1", type="float")
    compras.add_column(field="pvp1", type="float")

    compras += {
        'name_proveedor':'wolfang',
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
    f = table()
    with open(dir, 'r') as archivo:
        f.xml = archivo.read()
    print(f)
    os.remove(dir)

if __name__ == '__main__':
    _prueba()
