import logging
import nmap
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)


class LegoNmap(Lego):
    @staticmethod
    def listening_for(message):
        if message['text'] is not None:
            return message['text'].startswith('!nmap')

    def handle(self, message):
        if ' ' in message['text']:
            if len(message['text'].split()) > 2:
                self._dispatcher(message)
        else:
            opts = self._handle_opts(message)
            self.reply(message, 'Scan commands must be in the format '
                       + '!nmap {target} {port(s)}', opts)
        return

    def _dispatcher(self, message):
        command = message['text'].split()[1]
        commands = {'simple': self._basic_scan, 'os': self._os_detect}
        if command in commands:
            commands[command](message)
            return True
        else:
            self.reply(message, 'Command not supported. RTFM.',
                       self._handle_opts(message))
            return False

    def _os_detect(self, message):
        nm = nmap.PortScanner()
        try:
            hosts = message['text'].split()[2]
        except:
            self.reply(message, 'OS detect takes the form !nmap os {host}',
                       self._handle_opts(message))
        try:
            nm.scan(hosts=hosts, arguments='-O')
            self._report_results(nm, message)
        except nmap.nmap.PortScannerError:
            self.reply(message, 'Not running with sufficient privleges to '
                       + 'execute that request.', self._handle_opts(message))
        return True

    def _basic_scan(self, message):
        nm = nmap.PortScanner()
        try:
            host, ports = message['text'].split()[2:4]
        except:
            self.reply(message, 'Simple scan takes the form '
                       + '!nmap simple {host} {port(s}',
                       self._handle_opts(message))
            return False
        self.reply(message, 'Scanning {} {}'.format(host, ports),
                   self._handle_opts(message))
        nm.scan(host, ports)
        for node in nm.all_hosts():
            logger.info('got results for {}'.format(node))
        self._report_results(nm, message)

    def _report_results(self, nm, message):
        opts = self._handle_opts(message)

        for host in nm.all_hosts():
            text = "Host: {} | ".format(nm[host]['addresses']['ipv4'])
            logger.info(nm[host].keys())
            for proto in nm[host].all_protocols():
                text += "{} ".format(proto)
                lport = sorted(nm[host][proto].keys())
                open_ports = []

                for port in lport:
                    if nm[host][proto][port]['state'] == 'open':
                        open_ports.append(port)

                if len(open_ports) == 0:
                    text += "No open ports. | "
                else:
                    text += "{} | ".format(str(open_ports))
            if 'osmatch' in nm[host]:
                text += "OS best guess ({}% confidence): {} | ".format(
                    nm[host]['osmatch'][0]['accuracy'],
                    nm[host]['osmatch'][0]['name'])

            self.reply(message, text, opts)

    def _handle_opts(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            opts = None
            logger.error('''Could not identify message source in message:
                        {}'''.format(str(message)))
        return opts

    @staticmethod
    def get_name():
        return 'nmap'

    @staticmethod
    def get_help():
        help_text = "Run nmap scan from chat. " \
                "Usage: !nmap {target} {args}"
        return help_text
