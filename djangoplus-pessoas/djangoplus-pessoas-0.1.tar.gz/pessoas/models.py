# -*- coding: utf-8 -*-
from djangoplus.db import models
from enderecos.models import Endereco


class Pessoa(models.Model):

    nome = models.CharField(u'Nome', search=True, example=u'Carlos Breno')
    tipo = models.CharField(u'Tipo', choices=[[u'Física', u'Física'], [u'Jurídica', u'Jurídica']], filter=True, exclude=True, display=None)
    documento = models.CharField(u'Documento', exclude=True, search=True, display=None)

    endereco = models.OneToOneField(Endereco, verbose_name=u'Endereço', null=True, blank=True)

    telefone = models.PhoneField(verbose_name=u'Telefone', blank=True, null=True)
    email = models.EmailField(verbose_name=u'E-mail', blank=True, null=True)

    fieldsets = (
        (u'Dados Gerais', {'fields': ('nome',)}),
        (u'Endereço', {'fields': ('endereco',)}),
        (u'Telefone/E-mail', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = u'Pessoa'
        verbose_name_plural = u'Pessoas'
        verbose_female = True

    def __unicode__(self):
        return '%s (%s)' % (self.nome, self.documento)

    def can_add(self):
        return not self.pk


class PessoaFisicaAbstrata(Pessoa):

    cpf = models.CpfField(verbose_name=u'CPF', search=True)
    data_nascimento = models.DateField(verbose_name=u'Data de Nascimento', null=True, blank=True)

    fieldsets = (
        (u'Dados Gerais', {'fields': ('nome', ('cpf', 'data_nascimento'))}),
        (u'Endereço', {'fields': ('endereco',)}),
        (u'Contatos', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = u'Pessoa Física'
        verbose_name_plural = u'Pessoas Físicas'
        icon = 'fa-user'
        abstract = True

    def __unicode__(self):
        return '%s (%s)' % (self.nome, self.cpf)

    def save(self, *args, **kwargs):
        self.tipo = u'Física'
        self.documento = self.cpf
        super(PessoaFisicaAbstrata, self).save(*args, **kwargs)


class PessoaJuridicaAbstrata(Pessoa):

    cnpj = models.CnpjField(verbose_name=u'CNPJ', search=True)
    inscricao_estadual = models.CharField(verbose_name=u'Inscrição Estadual', null=True, blank=True)

    fieldsets = (
        (u'Dados Gerais', {'fields': ('nome', ('cnpj', 'inscricao_estadual'))}),
        (u'Endereço', {'fields': ('endereco',)}),
        (u'Contatos', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = u'Pessoa Jurídica'
        verbose_name_plural = u'Pessoas Jurídicas'
        icon = 'fa-building'
        abstract = True

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.tipo = u'Jurídica'
        self.documento = self.cnpj
        super(PessoaJuridicaAbstrata, self).save(*args, **kwargs)
