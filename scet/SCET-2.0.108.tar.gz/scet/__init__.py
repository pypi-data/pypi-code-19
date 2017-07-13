#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Modulo de librerias personales y componentes para crear un sistema de
 administracion, Compuesto por:

    - bd_xml: una libreria que define un objeto tipo tabla que puede
    exportarse e importarse desde un archivo XML y una base de datos
    MySQL

    - libsa: una libreria que define conceptos de un programa
    administrativo como formularios, tablas, selectores de registros,
    generadores de reportes, verificacion de datos entrados por el
    usuario, etc.

Ademas contiene varios modulos que definen componentes especificos del
SCET, por ejemplo:

    - Contenedores: marco de ventana comun para poner un formulario

    - Formularios: los diferentes formularios del sistema: clientes,
    equipos, etc.

    - Mostradores: muestran informacion de un objeto sin la capasidad de
     editar

    - Objetos: los objetos son abstraciones de un componente de la base
    de datos, los formularios los usan para modificar los registros

    - Plantillas: Son como formularios pero enves de escribir a un
    registro de tabla, escribe muchos registros a una tabla con una
    estructura llave - valor

    - Reportes: define todos los reportes del sistema, entradas, listados

    - Selectores: permiten buscar y selecionar registros de una tabla

    - Tablas: muestran muchos registros en una tabla

    - Ventanas: define conceptualmente las ventanas que organisan los
    elementos anteriores de forma usable por el usuario
"""


__all__ = [
    "main",
    "globales",
    "libsa",
    "bd_xml",
    "Contenedores",
    "Formularios",
    "Mostradores",
    "Objetos",
    "Plantillas",
    "Reportes",
    "Selectores",
    "Tablas",
    "Ventanas",
    ]
