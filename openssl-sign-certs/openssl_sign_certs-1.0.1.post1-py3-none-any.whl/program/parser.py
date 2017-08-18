# encoding:utf-8

# Documentación de la función add_argument: https://docs.python.org/3.5/library/argparse.html#the-add-argument-method

import os
import sys
from argparse import ArgumentParser
from configparser import ConfigParser

from openssl_sign_certs.program.statics import Statics


class Parser:
    def __init__(self):
        self.batch_parser = ArgumentParser(add_help=False)
        self.batch_parser.add_argument('-b', '--batch')
        self.args = vars(self.batch_parser.parse_known_args()[0])
        self.__parse_batch()
        self.parser = ArgumentParser(prog='OpenSSL Sign Certificates', description='Firma certificados rápida y fácilmente con tu Autoridad de Certificación.')
        self.parser.add_argument('-b', '--batch', help='Archivo con campos preestablecidos para este programa, pensado para ser reutilizable. Los campos que se especifiquen en la llamada tienen '
                                                       'prioridad sobre los presentes en el archivo.')
        self.parser.add_argument('-c', '--ca-cert', required=True, help='El certificado de la Autoridad de Certificación.')
        self.parser.add_argument('-k', '--key', '--ca-key', required=True, help='La clave de la Autoridad de Certificación.')
        self.parser.add_argument('-i', '--in', required=True, metavar='CSR', help='El certificado que debe ser firmado por la Autoridad de Certificación.')
        self.parser.add_argument('-o', '--out', required=True, metavar='SIGNED_CERT', help='La ubicación y el nombre del archivo con el que se guardará el certificado ya firmado.')
        self.parser.add_argument('-md', '--hash', metavar='ALGO', choices=['md5', 'sha1', 'sha256', 'sha512'], default='sha256',
                                 help='El algoritmo de resumen para la firma que se va a realizar. (Defecto: %(default)s)')
        self.parser.add_argument('-s', '--serial', type=int, default=None, metavar='NUMBER',
                                 help='El número de serie que queremos asignarle al certificado que se va a firmar. Si no se especifica, se genera automáticamente un entero de 64 bits.')
        self.parser.add_argument('-sd', '--start-date', default=None, metavar='DATE', nargs='+',
                                 help='La fecha a partir de la cual el certificado es válido en formato dd-mm-AAAA HH:MM:SS (GMT). Se pueden omitir tanto los segundos como todo el campo horario. '
                                      'También se puede utilizar el formato de fecha AAAA-mm-dd. Si no se especifica, se utilizan la fecha y hora actuales.')
        self.parser.add_argument('-ed', '--expiry-date', default=None, metavar='DATE', nargs='+',
                                 help='La fecha en la que caduca la firma del certificado. Acepta los mismos formatos de fecha y hora que --start-date.  Si no se especifica, '
                                      'la firma del certificado caduca a los 30 días contando desde la fecha presente.')
        self.parser.add_argument('-sc', '--section', default=None, help='La sección de extensiones para la firma del certificado.')
        self.parser.add_argument('-ef', '--extensions-file', default=None,
                                 help='Archivo extra donde se especifican más secciones X509v3 para añadir a la lista de disponibles para ser usadas con la opción --section.')
        self.parser.add_argument('-cf', '--config', default=None, help='Archivo alternativo de configuración al proporcionado por defecto por OpenSSL (/usr/lib/ssl/openssl.cnf).')
        self.args = vars(self.parser.parse_args())
        self.__parse_options()

    def __parse_batch(self):
        if self.args['batch'] is None:
            return None
        Statics.BATCH = os.path.realpath(os.path.expandvars(os.path.expanduser(self.args['batch'])))
        config = ConfigParser(inline_comment_prefixes='#')
        config.read(Statics.BATCH)
        config = config['OPENSSL-SIGN-CERTS PARAMETERS']
        params_list = ('ca-cert', 'ca-key', 'in', 'out', 'hash', 'serial', 'start-date', 'expiry-date', 'section', 'extensions-file', 'config')
        for param in params_list:
            try:
                value = config[param]
                if param == 'extensions-file' and value == 'this':
                    value = Statics.BATCH
                sys.argv.insert(1, value)
                sys.argv.insert(1, '--{0}'.format(param))
            except KeyError:
                pass

    def __parse_options(self):
        Statics.CA_CERT = self.args['ca_cert']
        Statics.CA_KEY = self.args['key']
        Statics.CONFIG = self.args['config']
        Statics.EXTENSIONS_FILE = self.args['extensions_file']
        Statics.HASH = self.args['hash']
        Statics.IN = self.args['in']
        Statics.OUT = self.args['out']
        Statics.SECTION = self.args['section']
        Statics.SERIAL = self.args['serial']
        Statics.START_DATE = ' '.join(self.args['start_date'][:2]) if self.args['start_date'] is not None else None
        Statics.EXPIRY_DATE = ' '.join(self.args['expiry_date'][:2]) if self.args['expiry_date'] is not None else None
