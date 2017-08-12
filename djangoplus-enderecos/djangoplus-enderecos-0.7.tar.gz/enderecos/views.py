# -*- coding: utf-8 -*-
import json
import urllib2
from urllib2 import HTTPError

from enderecos.models import Municipio, Estado
from django.http.response import HttpResponse


def consultar(request, cep):
    try:
        # {u'bairro': u'Santos Reis', u'cidade': u'Parnamirim', u'logradouro': u'Avenida Jo\xe3o XXIII', u'estado_info':
        # {u'area_km2': u'52.811,110', u'codigo_ibge': u'24', u'nome': u'Rio Grande do Norte'}, u'cep': u'59141030',
        # u'cidade_info': {u'area_km2': u'123,471', u'codigo_ibge': u'2403251'}, u'estado': u'RN'}

        dados = json.loads(urllib2.urlopen('http://api.postmon.com.br/v1/cep/%s' % cep).read())
        codigo_estado = dados['estado_info']['codigo_ibge']
        codigo_cidade = dados['cidade_info']['codigo_ibge']
        nome_cidade = cidade = dados['cidade']
        
        qs = Municipio.objects.filter(codigo=dados['cidade_info']['codigo_ibge'])
        if qs.exists():
            cidade = qs[0]
            dados['cidade_id'] = cidade.pk
            dados['cidade'] = unicode(cidade)
        else:
            estado = Estado.objects.get(codigo=codigo_estado)
            cidade = Municipio.objects.create(nome=nome_cidade, estado=estado, codigo=codigo_cidade)
            dados['cidade_id'] = cidade.pk
            dados['cidade'] = unicode(cidade)
        return HttpResponse(json.dumps(dados))
    except HTTPError:
        return HttpResponse(json.dumps(dict(message=u'CPF inválido!')))