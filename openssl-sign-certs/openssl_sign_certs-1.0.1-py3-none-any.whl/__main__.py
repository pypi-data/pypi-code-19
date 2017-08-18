#!/usr/bin/env python3
# encoding:UTF-8

from openssl_sign_certs.program.parser import Parser
from openssl_sign_certs.program.sign_certs import SignCerts
from openssl_sign_certs.program.statics import Statics


def main():
    Parser()
    SignCerts(ca_cert=Statics.CA_CERT, ca_key=Statics.CA_KEY, cert_request=Statics.IN, signed_cert=Statics.OUT, hash_algo=Statics.HASH, serial=Statics.SERIAL, start_date=Statics.START_DATE,
              expiry_date=Statics.EXPIRY_DATE, section=Statics.SECTION, extensions_file=Statics.EXTENSIONS_FILE, config_file=Statics.CONFIG)


if __name__ == '__main__':
    main()
