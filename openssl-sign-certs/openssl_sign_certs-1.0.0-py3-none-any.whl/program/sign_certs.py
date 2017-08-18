# encoding:utf-8

import datetime
import os
import shutil
import subprocess
from random import SystemRandom


class SignCerts:
    def __init__(self, ca_cert, ca_key, cert_request, signed_cert, hash_algo='sha256', serial=None, start_date=None, expiry_date=None, section=None, extensions_file=None, config_file=None):
        self.ca_cert = self.__real_path(ca_cert)
        self.ca_key = self.__real_path(ca_key)
        self.cert_request = self.__real_path(cert_request)
        self.signed_cert = self.__real_path(signed_cert)
        self.hash_algo = hash_algo
        self.serial = int(serial) if serial is not None else None
        self.section = section
        self.extensions_file = self.__real_path(extensions_file) if extensions_file is not None else None
        self.config_file = self.__real_path(config_file) if config_file is not None else None
        self.start_date = self.__parse_dates(start_date) if start_date is not None else None
        self.expiry_date = self.__parse_dates(expiry_date) if expiry_date is not None else None
        self.__sign_certs()

    @staticmethod
    def __make_temp_folders():
        os.umask(0)
        carpeta_temporal = os.path.join('/', 'tmp', 'openssl-sign-certs_{0}'.format(SystemRandom().getrandbits(32)))
        os.makedirs(os.path.join(carpeta_temporal, 'demoCA', 'newcerts'), exist_ok=True)
        open(os.path.join(carpeta_temporal, 'demoCA', 'index.txt'), 'w').close()
        return carpeta_temporal

    @staticmethod
    def __real_path(path):
        return os.path.realpath(os.path.expandvars(os.path.expanduser(path)))

    @staticmethod
    def __parse_dates(date):
        new_formats = lambda sep, formats_list: [x.replace('-', sep) for x in formats_list if x.count('-') > 0]
        formats = ['%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d-%m-%Y', '%Y-%m-%d']
        formats.extend(new_formats('/', formats))
        formats.extend(new_formats('.', formats))
        res = None
        for formato in formats:
            try:
                formatted = datetime.datetime.strptime(date, formato)
                res = formatted
            except:
                pass
        if res:
            res = datetime.datetime.strftime(res, '%Y%m%d%H%M%SZ')
        return res

    def __make_serial(self, folder):
        if self.serial is None:
            self.serial = SystemRandom().getrandbits(64)
        serial = '0{number}'.format(number=format(self.serial, 'x'))  # Convierte el int a una cadena hex
        serial = '0' + serial if len(serial) % 2 != 0 else serial  # El número de caracteres debe ser par. Si no, OpenSSL lanza una excepción.
        file = os.path.join(folder, 'demoCA', 'serial')
        with open(file, 'w') as f:
            f.write(serial + '\n\n')

    def __sign_certs(self):
        carpeta_temporal = self.__make_temp_folders()
        self.__make_serial(carpeta_temporal)
        command = ['openssl', 'ca', '-policy', 'policy_anything', '-md', self.hash_algo, '-cert', self.ca_cert, '-keyfile', self.ca_key, '-in', self.cert_request, '-out', self.signed_cert]
        if self.start_date:
            command.extend(('-startdate', self.start_date))
        if self.expiry_date:
            command.extend(('-enddate', self.expiry_date))
        else:
            command.extend(('-days', str(30)))
        if self.section:
            command.extend(('-extensions', self.section))
        if self.extensions_file:
            command.extend(('-extfile', self.extensions_file))
        if self.config_file:
            command.extend(('-config', self.config_file))
        try:
            subprocess.run(command, cwd=carpeta_temporal, universal_newlines=True)
        except:
            print()
        shutil.rmtree(carpeta_temporal, ignore_errors=True)
