# encoding:utf-8

# Documentación de la función add_argument: https://docs.python.org/3.5/library/argparse.html#the-add-argument-method

import sys
from argparse import ArgumentParser

from openvpn_reconnect.program.statics import Statics


class Parser:
    def __init__(self):
        self.parser = ArgumentParser(prog='OpenVPN Reconnect', description='Comprueba el estado del programa OpenVPN y, si no hay conectividad, lo reinicia, da igual que sea cliente o servidor.',
                                     epilog='El programa debe ser ejecutado como root para funcionar.')
        daemon_group = self.parser.add_mutually_exclusive_group(required=True)
        daemon_group.add_argument('--start', action='store_true', default=False, help='Lanza el demonio que controla este programa.')
        daemon_group.add_argument('--stop', action='store_true', default=False, help='Detiene el demonio que controla este programa.')
        daemon_group.add_argument('--restart', action='store_true', default=False, help='Reinicia el demonio que controla este programa.')
        self.parser.add_argument('-i', '--interface', default=None, help='La interfaz por la que queremos enviar los paquetes ping para comprobar la conectividad del host. (Defecto: todas las '
                                                                         'interfaces)')
        self.parser.add_argument('-p', '--packets', type=int, default=5, help='El número de paquetes que enviaremos con ping para comprobar la conectividad del host. (Defecto: %(default)d paquetes.')
        self.parser.add_argument('-s', '--seconds', type=int, default=60, help='El número de segundos que deben transcurrir entre dos comprobaciones del host por parte del programa (no entre dos '
                                                                               'peticiones de ping). (Defecto: %(default)d segundos)')
        self.parser.add_argument('host', help='El host cuya conectividad queremos comprobar.')
        self.args = vars(self.parser.parse_args())
        self.__parse_options()

    def __parse_options(self):
        Statics.HOST = self.args['host']
        Statics.INTERFACE = self.args['interface']
        Statics.PACKETS = self.args['packets']
        Statics.SECONDS = self.args['seconds']
        if (Statics.SECONDS // Statics.PACKETS) < 10:
            print('Error: Por cada paquete que se quiera enviar con ping, es necesario esperar al menos 10 segundos más para la siguiente iteración del programa, para evitar colapsar a peticiones '
                  'el servidor OpenVPN. Es decir, el cociente SEGUNDOS / PAQUETES debe ser, al menos, 10.', file=sys.stderr)
            print('Por favor, aumenta el tiempo de espera o disminuye el número de paquetes.', file=sys.stderr)
            sys.exit(1)
