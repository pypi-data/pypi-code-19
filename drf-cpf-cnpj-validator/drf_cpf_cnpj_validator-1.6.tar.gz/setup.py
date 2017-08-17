# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
  name='drf_cpf_cnpj_validator',
  packages=['drf_cpf_cnpj_validator'],
  version='1.6',
  description='A small and quick validation plugin for CPF or CNPJ in django rest framework!',
  long_description=open('README.rst').read(),
  author='Júnior Souza',
  author_email='jr.souza9520@gmail.com',
  url='https://github.com/jrsouza95/drf-cpfcnpj-validator',
  download_url='https://github.com/jrsouza95/drf-cpfcnpj-validator/archive/1.6.tar.gz',
  keywords=[
        'django-rest-framework', 'cpf', 'cnpj', 'python', 'django', 'validation',
        'validation-library', 'cpf-validation', 'cnpj-validation', 'validação-de-cpf',
        'validação-de-cnpj', 'drf-validation', 'validação', 'django-rest-cpf-validation',
        'django-rest-cnpj-validation', 'validação-cpf-django-rest-framework', 'validação-cnpj-django-rest-framework'
  ],
  classifiers=[],
)
