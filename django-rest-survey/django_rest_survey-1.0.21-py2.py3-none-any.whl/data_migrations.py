# coding: utf-8
# flake8: noqa
from rest_survey.models import (
    Survey,
    Section,
    Question,
)
from rest_survey.choices import (
    QUESTION_TYPE_RADIO,
    QUESTION_TYPE_CHECKBOXES,
    QUESTION_TYPE_SELECT,
    QUESTION_TYPE_TEXT,
    QUESTION_TYPE_TEXTAREA,
    QUESTION_TYPE_NUMBER,
    QUESTION_TYPE_DATE,
    QUESTION_TYPE_DATETIME,
    QUESTION_TYPE_LIST,
    QUESTION_TYPE_GRID,
)

def create_aldeia_survey(schema, apps):
    survey = Survey.objects.create(
        name='aldeias.Aldeia',
        active=True
    )

    s1 = Section.objects.create(
        survey=survey,
        title=u'1. Informações da coleta de dados'
    )

    q0 = Question.objects.create(
        survey=survey,
        section=s1,
        text=u'1.1 Data de aplicação do questionário:',
        type=QUESTION_TYPE_DATE
    )

    q01 = Question.objects.create(
        survey=survey,
        section=s1,
        text=u'1.2 Responsável pela coleta de dados:',
        type=QUESTION_TYPE_TEXT,
        options={
            'autocomplete': {

            }
        }
    )

    s2 = Section.objects.create(
        survey=survey,
        title=u'2. Informações gerais sobre a aldeia ou bairro'
    )

    q1 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.1 Fonte(s) de Energia',
        help=u'',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                'Elétrica',
                'Eólica',
                'Solar',
                'Gerador a Diesel',
                'Gerador a Gasolina',
                'Não possui energia'
            ]
        }
    )

    q2 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.2 Existe Associação Comunitária ou Cooperativa Indígena',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q3 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.3 Existem locais no entorno da aldeia utilizados pela comunidade para',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Rituais',
                u'Plantio',
                u'Não existe'
            ]
        },
        other_token='Outras funções'
    )

    q4 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.3.1 Se "existem locais", quanto tempo ficam afastados da aldeia?',
        type=QUESTION_TYPE_RADIO,
        parent=q3,
        parent_value=u'!Não existe',
        options={
            'values': [
                u'Menos de 1 mês',
                u'Mais de 1 mês',
            ]
        }
    )

    q5 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.3.2 É necessário a intervenção de saneamento com a construção de abastecimento de água e melhorias sanitárias?',
        type=QUESTION_TYPE_RADIO,
        parent=q3,
        parent_value=u'!Não existe',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    s3 = Section.objects.create(
        survey=survey,
        title=u'3. Abastecimento de água'
    )

    q6 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.1 Fontes de água existentes na aldeia ou bairro',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Rio',
                u'Lagoa',
                u'Chuva',
                u'Açude/Represa',
                u'Poço tubular',
                u'Nascente/Mina/Olho d\'agua',
                u'Cacimba/Cacimbão/Poço raso/Poço amazonas',
                u'Córrego/Riacho/Ribeirão/Igarapé/Sanga'
            ]
        }
    )

    q7 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.2 A aldeia ou bairro é abastecida por',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'SAA',
                u'Solução Alternativa',
                u'Não abastecida'
            ]
        }
    )

    q8 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.2.1 O SAA ou SA está localizado na aldeia ou bairro?',
        help=u'(captação, adução, reservação, tratamento e distribuição)',
        type=QUESTION_TYPE_RADIO,
        parent=q7,
        parent_value=u'!Não abastecida',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q9 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.2.2 Em que aldeia ou bairro está localizado?',
        type=QUESTION_TYPE_TEXT,
        parent=q8,
        parent_value=u'Não'
    )

    q10 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.3 Ano de Implantação e funcionamento do SAA ou SA?',
        type=QUESTION_TYPE_NUMBER,
        parent=q7,
        parent_value=u'!Não abastecida'
    )

    q11 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.4 O SAA ou Solução Alternativa está funcionando?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q12 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.5 Quem construiu o SAA ou Solução Alternativa?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'FUNASA',
                u'FUNAI',
                u'Companhia de Saneamento',
                u'Comunidade Indígena',
                u'SESAI',
                u'Prefeitura Municipal',
                u'ONG',
            ]
        },
        other_token='Outro'
    )

    q13 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.6 Ocorre manutenção no SAA ou Solução Alternativa?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q14 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.7 Quem é o responsável pela operação e manutenção do sistema?',
        type=QUESTION_TYPE_RADIO,
        parent=q13,
        parent_value=u'Sim',
        options={
            'values': [
                u'SESAI',
                u'FUNAI',
                u'Companhia de Saneamento',
                u'Comunidade Indígena',
                u'Prefeitura Municipal',
                u'ONG',
            ]
        },
        other_token=u'Outro'
    )

    q15 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.7.1 Existe AISAN na aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q16 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.8 A água distribuída pelo sistema é tratada?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q17 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.8.1 Qual o tipo de tratamento realizado?',
        type=QUESTION_TYPE_RADIO,
        parent=q16,
        parent_value=u'Sim',
        options={
            'values': [
                u'Filtração',
                u'Tratamento Completo',
                u'Desinfecção por ultravioleta',
                u'Desinfecção por ozônio',
                u'Somente cloração',
            ]
        }
    )

    q18 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.9 A água distribuída é fluoretada?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values':[
                u'Sim',
                u'Não'
            ]
        }
    )

    q19 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.10 A água distribuída pelo sistema é cobrada?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q20 = Question.objects.create(
        survey=survey,
        section=s3,
        parent=q19,
        parent_value=u'Sim',
        text=u'3.10.1 Marque quem é o responsável pelo pagamento da água distribuída SAA ou Solução Alternativa?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'DSEI',
                u'FUNAI',
                u'Companhia de Saneamento',
                u'Comunidade Indígena',
                u'Prefeitura Municipal',
                u'ONG',
            ]
        },
        other_token='Outro'
    )

    q21 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.11 Fontes Mananciais que alimentam o SAA ou SA?',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Rio',
                u'Córrego/Riacho/Ribeirão/Igarapé/Sanga',
                u'Lago',
                u'Açude/Represa',
                u'Nascente/Mina/Olho d\'agua',
                u'Cacimba/Cacimbão/Poço raso/Poço amazonas',
                u'Poço tubular (artesiano ou semi artesiano)'
            ]
        }
    )

    q22 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.11.1 Se poço tubular, descreva:',
        type=QUESTION_TYPE_GRID,
        parent=q21,
        parent_value=u'Poço tubular (artesiano ou semi artesiano)',
        options={
            'columns': [
                    {
                        'name': "pergunta",
                        'label': "",
                        'cell': "string",
                        'editable': False
                    }, {
                        'name': "valor",
                        'label': "Valor",
                        'cell': "integer"
                    }
                ],
            'rows': [
                    {
                        'pergunta': "Vazão(m3/h)", 
                        'valor': None
                    }, {
                        'pergunta': "Profundidade(m)", 
                        'valor': None
                    }, {
                        'pergunta': "Nível dinâmico(m)", 
                        'valor': None
                    }, {
                        'pergunta': "Nível estático(m)", 
                        'valor': None
                    },
            ]
        }
    )

    q26 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.11.2 Disponibilidade de água bruta para abastecimento durante o ano?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q27 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.11.3 Vazão de captação do sistema (soma de todas as vazões):',
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "valor",
                    'label': "Valor",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "m3/h em períodos normais", 
                    'valor': None
                }, {
                    'pergunta': "m3/h em períodos de estiagens", 
                    'valor': None
                }
            ]
        }
    )

    q29 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.12 O SAA ou SA possui reservatório?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q30 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.12.1 Informe o tipo de reservatório?',
        type=QUESTION_TYPE_CHECKBOXES,
        parent=q29,
        parent_value=u'Sim',
        options={
            'values': [
                u'Elevado',
                u'Enterrado',
                u'Apoiado',
                u'Semi enterrado'
            ]
        }
    )

    q31 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.13 Quantidade de reservatório(s) que faz(em) parte do sistema:',
        type=QUESTION_TYPE_GRID,
        parent=q29,
        parent_value=u'Sim',
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "elevado",
                    'label': "Elevado",
                    'cell': "integer"
                }, {
                    'name': "enterrado",
                    'label': "Enterrado",
                    'cell': "integer"
                }, {
                    'name': "apoiado",
                    'label': "Apoiado",
                    'cell': "integer"
                }, {
                    'name': "semi_enterrado",
                    'label': "Semi-enterrado",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Até 500 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "501 a 1.000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "1.001 a 3.000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "3.001 a 5000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "5.001 a 10.000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "10.001 a 20.000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                }, {
                    'pergunta': "Acima de 20.000 litros", 
                    'elevado': None, 
                    'enterrado': None,
                    'apoiado': None,
                    'semi_enterrado': None
                },
            ]
        }
    )

    q32 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.14 Tipo de material do(s) reservatório(s):',
        type=QUESTION_TYPE_GRID,
        parent=q29,
        parent_value=u'Sim',
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "fibra",
                    'label': "Fibra",
                    'cell': "integer"
                }, {
                    'name': "plastico",
                    'label': "Plástico",
                    'cell': "integer"
                }, {
                    'name': "concreto_armado",
                    'label': "Concreto armado",
                    'cell': "integer"
                }, {
                    'name': "metalico",
                    'label': "Metálico",
                    'cell': "integer"
                }, {
                    'name': "cimento_amianto",
                    'label': "Cimento amianto",
                    'cell': "integer"
                }, {
                    'name': "tijolo",
                    'label': "Tijolo",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Reservatório(s) elevado(s)", 
                    'fibra': None, 
                    'plastico': None,
                    'concreto_armado': None,
                    'metalico': None,
                    'cimento_amianto': None,
                    'tijolo': None,
                }, {
                    'pergunta': "Reservatório(s) apoiado(s)", 
                    'fibra': None, 
                    'plastico': None,
                    'concreto_armado': None,
                    'metalico': None,
                    'cimento_amianto': None,
                    'tijolo': None,
                }, {
                    'pergunta': "Reservatório(s) enterrado(s)", 
                    'fibra': None, 
                    'plastico': None,
                    'concreto_armado': None,
                    'metalico': None,
                    'cimento_amianto': None,
                    'tijolo': None,
                }, {
                    'pergunta': "Reservatório(s) semi-enterrado(s)", 
                    'fibra': None, 
                    'plastico': None,
                    'concreto_armado': None,
                    'metalico': None,
                    'cimento_amianto': None,
                    'tijolo': None,
                }
            ]
        }
    )

    q33 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.14.1 Tipo de material da torre do reservatório elevado:',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Ferro ou aço',
                u'Madeira',
                u'Concreto armado'
            ]
        }
    )

    q34 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.15 Forma de distribuição da Solução Alternativa:',
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "quantidade",
                    'label': "Quantidade",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Carro Pipa (litros/dia)", 
                    'quantidade': None, 
                }, {
                    'pergunta': "Chafariz", 
                    'quantidade': None, 
                }, {
                    'pergunta': "Ponto de água", 
                    'quantidade': None, 
                }, {
                    'pergunta': "Rede", 
                    'quantidade': None, 
                },
            ]
        }
    )
    
    q35 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.16 Extensão aproximada(m):',
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "valor",
                    'label': "Valor",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Adutora", 
                    'valor': None, 
                }, {
                    'pergunta': "Rede de distribuição", 
                    'valor': None, 
                }, {
                    'pergunta': "Ramal domiciliar", 
                    'valor': None, 
                }
            ]
        }
    )

    q36 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.17 O SAA ou Solução Alternativa possui bombas para elevação de água?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q37 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.17.1 Indique a quantidade de equipamentos utilizados para a elevação da água:',
        type=QUESTION_TYPE_GRID,
        parent=q36,
        parent_value=u'Sim',
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "valor",
                    'label': "Quantidade",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Grupo gerador", 
                    'valor': None, 
                }, {
                    'pergunta': "Cata vento", 
                    'valor': None, 
                }, {
                    'pergunta': "Compressor de ar", 
                    'valor': None, 
                }, {
                    'pergunta': "Bomba submersa", 
                    'valor': None, 
                }, {
                    'pergunta': "Carneiro hidráulico", 
                    'valor': None, 
                }, {
                    'pergunta': "Bomba centrífuga", 
                    'valor': None, 
                }, {
                    'pergunta': "Bomba manual de êmbolo", 
                    'valor': None, 
                }, {
                    'pergunta': "Outros tipos", 
                    'valor': None, 
                }
            ]
        }
    )

    q38 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.18 O SAA ou Solução Alternativa funciona de forma:',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Contínua',
                u'Intermitente'
            ]
        }
    )

    q39 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.18.1 Se intermitente ou descontínua, qual o motivo?',
        type=QUESTION_TYPE_RADIO,
        parent=q38,
        parent_value=u'Intermitente',
        options={
            'values': [
                u'Produção (vazão) insuficiente',
                u'Falta de equipe para manutenção',
                u'Rompimento de tubulações',
                u'Não há necessidade de funcionamento contínuo',
                u'Falta de energia'
            ]
        }
    )

    q40 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.18.2 Quando ocorre falta de água, como é feito o abastecimento nos imóveis?',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Carro pipa',
                u'Poços particulares',
                u'Mina ou nascente',
                u'Água de chuva'
            ]
        },
        other_token=u'Outras fontes'
    )

    q41 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.18.3 Energia utilizada no SAA:',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Eólica',
                u'Solar',
                u'Elétrica(Concessionária)',
                u'Gerador a diesel',
                u'Gerador a gasolina',
                u'Nenhuma'
            ]
        }
    )

    s4 = Section.objects.create(
        survey=survey,
        title=u'4. Esgotamento Sanitário'
    )

    q42 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.1 Tem privada coletiva na aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q43 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.1.1 Quantidade de privadas coletivas existentes na aldeia ou bairro:',
        type=QUESTION_TYPE_NUMBER,
        parent=q42,
        parent_value=u'Sim'
    )

    q44 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.1.2 Quem faz a limpeza das privadas coletiva?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'DSEI',
                u'FUNAI',
                u'Prefeitura Municipal',
                u'Comunidade Indígena',
                u'Outra Instituição',
                u'Ninguém'
            ]
        },
        parent=q42,
        parent_value=u'Sim'
    )

    q45 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.2 Existe rede de esgotos na aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        },
        parent=q42,
        parent_value=u'Sim'
    )

    q46 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.2.1 O esgoto é tratado?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        },
        parent=q45,
        parent_value=u'Sim'
    )

    q47 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.2.1.1 Tipos de tratamento:',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Fossa séptica',
                u'Filtro biológico',
                u'Lago de estabilização',
                u'Valo de oxidação'
            ]
        },
        parent=q46,
        parent_value=u'Sim'
    )

    q48 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.2.2 Onde são lançados os esgotos não tratados?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Curso d\'água',
                u'Céu aberto',
                u'Soluções Individuais'
            ]
        },
        parent=q46,
        parent_value=u'Não'
    )


    s5 = Section.objects.create(
        survey=survey,
        title=u'5. Resíduos Sólidos (lixo)'
    )

    q49 = Question.objects.create(
        survey=survey,
        section=s5,
        text=u'5.1 A comunidade tem o hábito de limpar os espaços coletivos da aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q50 = Question.objects.create(
        survey=survey,
        section=s5,
        text=u'5.1.1 Qual a periodicidade da limpeza?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Diária',
                u'Mensal',
                u'Trimestral',
                u'Semestral',
                u'Anual'
            ]
        },
        parent=q49,
        parent_value=u'Sim'
    )

    q51 = Question.objects.create(
        survey=survey,
        section=s5,
        text=u'5.2 Qual destinação final dos resíduos sólidos?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Queimado',
                u'Enterrado',
                u'Lançado próximo a cursos d\'água',
                u'Lançado próximo aos imóveis',
                u'Lançado próximo a área com atividade agropecuária',
                u'Coletado pelo serviço municipal',
                u'Reciclado',
                u'Reutilizado'
            ]
        },
        other_token=u'Outros'
    )

    s6 = Section.objects.create(
        survey=survey,
        title=u'6. Sistema de transporte e comunicação'
    )

    q52 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.1 Tipo(s) de transporte(s) usado(s) para chegar à aldeia ou bairro:',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Carro',
                u'Barco',
                u'Somente carro com tração',
                u'Canoa',
                u'Moto',
                u'Avião'
            ]
        },
        other_token=u'Outro'
    )

    q53 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.2 Que tipo(s) de equipamento(s) de comunicação é(são) usado(s)?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Rádio transceptor',
                u'Telefone fixo',
                u'Telefone celular',
                u'Correios',
                u'Nenhum'
            ]
        }
    )

    s7 = Section.objects.create(
        survey=survey,
        title=u'7. Atividades econômicas'
    )

    q54 = Question.objects.create(
        survey=survey,
        section=s7,
        text=u'7.1 Atividades que são desenvolvidas na aldeia ou bairro que geram renda e instituições de apoio:',
        help=u"""
        1.FUNASA
        2.FUNAI
        3.MMA
        4.IBAMA
        5.INCRA
        6.EMBRABA
        7.EMATER
        8.UNIVERSIDADE
        9.PREFEITURA
        10.ONG
        11.PRÓPRIA COMUNIDADE
        12.OUTROS
        13.NÃO HÁ
        """,
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                {
                    'name': "existe",
                    'label': "",
                    'cell': "boolean"
                },
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "apoio_tecnico",
                    'label': "Apoio Técnico",
                    'cell': "integer"
                }, {
                    'name': "apoio_financeiro",
                    'label': "Apoio Financeiro",
                    'cell': "integer"
                }
            ],
            'rows': [
                {
                    'pergunta': "Criação de aves", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Criação de peixes", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Criação de porcos", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Criação de camarão", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Criação de ostras", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Produção de farinha", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Produção de mel", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Viveiro de mudas", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Extrativismo mineral", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Extrativismo vegetal", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Pecuária(gado, bode, ovelha)", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Agroextrativismo", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Agricultura Extensiva", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Agricultura de Subsistência", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Produção e venda de artesanato", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }, {
                    'pergunta': "Outras atividades", 
                    'existe': None, 
                    'apoio_tecnico': None, 
                    'apoio_financeiro': None, 
                }
            ]
        }
    )

    s8 = Section.objects.create(
        survey=survey,
        title=u'8. Impactos Ambientais'
    )

    q55 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.1 Fatores que afetam a qualidade e quantidade de água nos mananciais:',
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                 {
                    'name': "existe",
                    'label': "",
                    'cell': "boolean"
                }, {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "montante",
                    'label': "Montante",
                    'cell': "boolean"
                }, {
                    'name': "jusante",
                    'label': "Jusante",
                    'cell': "boolean"
                }
            ],
            'rows': [
                {
                    'pergunta': "Assoreamento", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Mineração", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Garimpo", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Balneário", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Rodovias", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Enchentes", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Queimada", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Deslizamento", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Suinocultura", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Lixões", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Lançamento de esgoto", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Retirada de mata ciliar", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Desmatamentos", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Desertificação", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Degradação do solo / Erosão", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Desvios de curso d'água", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Transposição de rios", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Lançamento de agrotóxicos", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Represamento ou barragem", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Agricultura extensiva", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Despejos Industriais", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Ocupação irregular", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }, {
                    'pergunta': "Não existe", 
                    'existe': None, 
                    'montante': None, 
                    'jusante': None, 
                }
            ]
        }
    )

    q56 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.2 Há reflorestamento na aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q57 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.3 Existe agente agroflorestal ou ambiental indígena na aldeia ou bairro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

def create_imovel_survey(schema, apps):
    survey = Survey.objects.create(
        name='aldeias.Imovel',
        active=True
    )

    s1 = Section.objects.create(
        survey=survey,
        title=u'1. Identificação'
    )

    s2 = Section.objects.create(
        survey=survey,
        title=u'2. Situação do Imóvel'
    )

    q1 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.1 Tipo de Ocupação do Imóvel',
        help=u'',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Residência de Índio',
                u'Residência de Índio/Comércio',
                u'Residência de Não Índio',
                u'Residência de Não Índio/Comércio',
                u'Centro Comunitário',
                u'Casa de missionário',
                u'Casa de indigenista',
                u'Posto de Saúde',
                u'Pólo Base 1',
                u'Pólo Base 2',
                u'Posto da FUNAI',
                u'Galpão para depósito',
                u'Escola',
                u'Igreja',
                u'Comércio',
                u'Casa de farinha',
                u'Casa de cerimônia',
                u'Outro tipo',
            ]
        },
    )

    q3 = Question.objects.create(
        survey=survey,
        section=s2,
        text=u'2.3 Condição de Ocupação do imóvel',
        help='',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Particular Permanente',
                u'Particular Improvisado',
                u'Coletivo Permanente',
                u'Coletivo Improvisado',
                u'Alugado',
                u'Outra condição',
            ]
        }
    )

    s3 = Section.objects.create(
        survey=survey,
        title=u'3. Características do Imóvel'
    )

    q4 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.1 Material das paredes',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Tijolo/Alvenaria',
                u'Taipa revestida',
                u'Taipa não revestida',
                u'Material aproveitado',
                u'Adobe',
                u'Bambu',
                u'Paxiúba',
                u'Madeira',
                u'Palha ou sapê'
            ]
        },
        other_token='Outros'
    )

    q5 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.2 Paredes com reboco?',
        parent=q4,
        parent_value=u'Tijolo/Alvenaria',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q6 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.3 Material do Piso',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Cerâmica',
                u'Chão batido',
                u'Cimentado',
                u'Tijolo',
                u'Paxiúba',
                u'Ladrilho',
                u'Madeira',
                u'Outros',
            ]
        }
    )

    q7 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.4 Material da cobertura',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Alumínio',
                u'Madeira',
                u'Palha ou sapê',
                u'Material aproveitado',
                u'Barro (cerâmica)',
                u'Cimento amianto'
            ]
        },
        other_token='Outros'
    )

    q8 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.5 Número de comodos',
        type=QUESTION_TYPE_NUMBER,
    )

    q9 = Question.objects.create(
        survey=survey,
        section=s3,
        text=u'3.6 Fonte de Energia',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Elétrica',
                u'Solar',
                u'Eólica',
                u'Gerador a diesel',
                u'Gerador a gasolina',
                u'Nenhuma',
            ]
        }
    )

    s4 = Section.objects.create(
        survey=survey,
        title=u'4. Abastecimento de Água'
    )

    q10 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.1 Tem água encanada no imóvel?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q11 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.1.1 Se "Sim", de onde?',
        type=QUESTION_TYPE_RADIO,
        parent=q10,
        parent_value=u'Sim',
        options={
            'values': [
                u'Do SAA / SAC',
                u'De SAI'
            ]
        }
    )

    q12 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'Do item 4.2 ao 4.9 marcar o que tiver no imóvel (casa); caso não tenha deixe a opção em branco.',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'4.2 Tem poço no terreno e a água é utilizada para o consumo doméstico?',
                u'4.3 Tem bomba no poço?',
                u'4.4 Tem caixa d\'agua ou reservatório para água de chuva (cisterna)?',
                u'4.5 Tem caixa d\'agua ou reservatório para água de chuva no imóvel (mínimo 250 litros)?',
                u'4.5.1 Ligado a rede de água do sistema?',
                u'4.6 Tem banheiro?',
                u'4.7 Tem lavatório?',
                u'4.8 Tem tanque de lavar?',
                u'4.9 Tem pia de cozinha?',
                u'4.10 Tem filtro de água?',
            ]
        }
    )

    q22 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.11 É feito algum tipo de tratamento da água no imóvel?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q23 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.11.1 Informe o tipo de tratamento?',
        type=QUESTION_TYPE_RADIO,
        parent=q22,
        parent_value=u'Sim',
        options={
            'values': [
                u'Filtração',
                u'Fervura',
                u'Cloração',
                u'Radiação Solar',
            ]
        }
    )

    q24 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.12 Se existe SAA ou SAC na aldeia ou bairro, há pessoas no imóvel que não usam a água distribuída?',
        type=QUESTION_TYPE_RADIO,
        parent=q11,
        parent_value=u'Do SAA / SAC',
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q25 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.12.1 Qual(is) o(s) motivo(s) pelo(s) qual(is) não usa(m)?',
        parent=q24,
        parent_value=u'Sim',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Gosto ruim',
                u'Cheiro ruim',
                u'Água suja',
                u'Não chega água no imóvel',
                u'Outros',
            ]
        }
    )

    q26 = Question.objects.create(
        survey=survey,
        section=s4,
        text=u'4.13 Informe a origem da água preferida pela maioria das pessoas do imóvel:',
        type=QUESTION_TYPE_GRID,
        options={
            'columns': [
                {
                    'name': "pergunta",
                    'label': "",
                    'cell': "string",
                    'editable': False
                }, {
                    'name': "rio",
                    'label': "Rio",
                    'cell': "boolean"
                }, {
                    'name': "corrego",
                    'label': "Córrego/Riacho/Ribeirão/Igarapé/Sanga",
                    'cell': "boolean"
                }, {
                    'name': "lago",
                    'label': "Lago",
                    'cell': "boolean"
                }, {
                    'name': "acude",
                    'label': "Açude/Represa",
                    'cell': "boolean"
                }, {
                    'name': "nascente",
                    'label': "Nascente/Mina/Olho d'água",
                    'cell': "boolean"
                }, {
                    'name': "cacimba",
                    'label': "Cacimba/Cacimbão/Poço raso/Poço amazonas",
                    'cell': "boolean"
                }, {
                    'name': "poco",
                    'label': "Poço tubular profundo",
                    'cell': "boolean"
                }, {
                    'name': "chuva",
                    'label': "Chuva",
                    'cell': "boolean"
                }, {
                    'name': "encanada",
                    'label': "Encanada",
                    'cell': "boolean"
                }
            ],
            'rows': [
                {
                    'pergunta': "Para beber", 
                    'rio': None, 
                    'corrego': None, 
                    'lago': None, 
                    'acude': None, 
                    'nascente': None, 
                    'cacimba': None, 
                    'poco': None, 
                    'chuva': None, 
                    'encanada': None
                }, {
                    'pergunta': "Para preparar alimentos", 
                    'rio': None, 
                    'corrego': None, 
                    'lago': None, 
                    'acude': None, 
                    'nascente': None, 
                    'cacimba': None, 
                    'poco': None, 
                    'chuva': None, 
                    'encanada': None
                }, {
                    'pergunta': "Para tomar banho", 
                    'rio': None, 
                    'corrego': None, 
                    'lago': None, 
                    'acude': None, 
                    'nascente': None, 
                    'cacimba': None, 
                    'poco': None, 
                    'chuva': None, 
                    'encanada': None
                }, {
                    'pergunta': "Para lavar roupas", 
                    'rio': None, 
                    'corrego': None, 
                    'lago': None, 
                    'acude': None, 
                    'nascente': None, 
                    'cacimba': None, 
                    'poco': None, 
                    'chuva': None, 
                    'encanada': None 
                }
            ]
        }
    )

    s5 = Section.objects.create(
        survey=survey,
        title=u'5. Hábitos de Higiene'
    )

    q30 = Question.objects.create(
        survey=survey,
        section=s5,
        text=u'5.1 As pessoas do imóvel têm o hábito de limpar ou escovar os dentes?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    s6 = Section.objects.create(
        survey=survey,
        title=u'6. Destino dos dejetos'
    )

    q31 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.1 O imóvel possui privada individual?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q32 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.2 Com fossa seca?',
        parent=q31,
        parent_value=u'Sim',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q33 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.3 Com vaso sanitário ou bacia turca?',
        parent=q31,
        parent_value=u'Sim',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q34 = Question.objects.create(
        survey=survey,
        section=s6,
        text=u'6.3.1 Tipo de Ligação?',
        type=QUESTION_TYPE_RADIO,
        parent=q33,
        parent_value='Sim',
        options={
            'values': [
                u'Ligada a Fossa Séptica',
                u'Ligada somente ao sumidouro',
                u'Ligada a filtro biológico',
                u'Ligada a fossa séptica e sumidouro',
                u'Ligada a fossa séptica, filtro biológico e sumidouro',
                u'Ligada a rede de esgoto',
                u'Ligada a outros destinos',
            ]
        }
    )

    q35 = Question.objects.create(
        survey=survey,
        section=s6,
        parent=q31,
        parent_value=u'Não',
        type=QUESTION_TYPE_RADIO,
        text=u'6.4 Caso não possua privada individual, que local é utilizado para fazer as necessidades fisiológicas (fazer cocô)?',
        options={
            'values': [
                u'Privada Coletiva',
                u'Quintal',
                u'Fonte d\'agua',
                u'Terreno próximo aos imóveis',
                u'Terreno próximo a fonte d\'agua'
            ]
        },
        other_token='Outros locais'
    )

    q36 = Question.objects.create(
        survey=survey,
        section=s6,
        type=QUESTION_TYPE_RADIO,
        text=u'6.5 A água de banho, lavagem de roupa e louça é lançada a céu aberto?',
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    s7 = Section.objects.create(
        survey=survey,
        title=u'7. Destino dos resíduos sólidos (lixo)'
    )

    q37 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        text=u'7.1 Existe coleta dos resíduos sólidos?',
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q38 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        parent=q37,
        parent_value=u'Sim',
        text=u'7.1.1 Se "Sim", quem faz a coleta?',
        options={
            'values': [
                u'Serviço Municipal',
                u'Equipe de Saúde'
            ]
        },
        other_token=u'Outros'
    )

    q38 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        parent=q37,
        parent_value=u'Não',
        text=u'7.1.2 Se "Não", que destino é dado aos resíduos sólidos?',
        options={
            'values': [
                u'Lançado próximo a cursos d\'agua',
                u'Lançado próximo aos imóveis',
                u'Lançado próximo a área com atividade agropecuária',
                u'Queimado',
                u'Enterrado'
            ]
        },
        other_token=u'Outro'
    )

    q39 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        text=u'7.2 Os resíduos sólidos são acondicionados no imóvel?',
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        }
    )

    q40 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        parent=q39,
        parent_value=u'Sim',
        text=u'7.2.1 Onde é feito o acondicionamento dos resíduos sólidos no imóvel?',
        options={
            'values': [
                u'Saco plástico',
                u'Saco de papel',
                u'Tambor',
                u'Paneiro',
                u'Recipiente metálico ou plástico',
                u'Outros tipos de recipientes',
            ]
        }
    )

    q41 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_RADIO,
        text=u'7.3 Algum tipo de material do resíduo sólido é reaproveitado ou utilizado para reciclagem?',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q42 = Question.objects.create(
        survey=survey,
        section=s7,
        type=QUESTION_TYPE_CHECKBOXES,
        parent=q41,
        parent_value=u'Sim',
        text=u'7.3.1 Que tipo de material dos resíduos sólidos é reaproveitado ou utilizado para reciclagem?',
        options={
            'values': [
                u'Orgânico',
                u'Papel',
                u'Plástico',
                u'Vidro',
                u'Ferro',
                u'Cobre',
                u'Alumínio',
                u'Outros',
            ]
        }
    )

    s8 = Section.objects.create(
        survey=survey,
        title=u'8. Animais domésticos'
    )

    q43 = Question.objects.create(
        survey=survey,
        section=s8,
        type=QUESTION_TYPE_RADIO,
        text=u'8.1 Existe criação de animais domésticos no imóvel?',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q44 = Question.objects.create(
        survey=survey,
        section=s8,
        type=QUESTION_TYPE_RADIO,
        text=u'8.1.1 Os animais domésticos mantêm contato com resíduos sólidos?',
        parent=q43,
        parent_value=u'Sim',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q45 = Question.objects.create(
        survey=survey,
        section=s8,
        type=QUESTION_TYPE_RADIO,
        text=u'8.1.2 Os animais domésticos mantêm contato com as fezes das pessoas?',
        parent=q43,
        parent_value=u'Sim',
        options={
            'values': [
                u'Sim',
                u'Não',
            ]
        }
    )

    q46 = Question.objects.create(
        survey=survey,
        section=s8,
        type=QUESTION_TYPE_NUMBER,
        text=u'8.2.1 Qual é a quantidade de cachorros criados no imóvel?',
        parent=q43,
        parent_value=u'Sim',
    )

    q47 = Question.objects.create(
        survey=survey,
        section=s8,
        type=QUESTION_TYPE_NUMBER,
        text=u'8.2.2 Qual é a quantidade de gatos criados no imóvel?',
        parent=q43,
        parent_value=u'Sim',
    )

    q48 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.3 Que outros animais existem?',
        type=QUESTION_TYPE_CHECKBOXES,
        options={
            'values': [
                u'Animais silvestres',
                u'Cabra/bode',
                u'Cavalo',
                u'Gado',
                u'Galinha',
                u'Porco'
            ]
        },
        other_token=u'Outros animais'
    )

    q49 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.3.1 Criada no galinheiro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        },
        parent=q48,
        parent_value='Galinha'
    )


    q50 = Question.objects.create(
        survey=survey,
        section=s8,
        text=u'8.3.2 Criado no chiqueiro?',
        type=QUESTION_TYPE_RADIO,
        options={
            'values': [
                u'Sim',
                u'Não'
            ]
        },
        parent=q48,
        parent_value='Porco'
    )