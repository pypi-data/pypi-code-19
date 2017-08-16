#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run evrm with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "evrm"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)

    return upl

setup(
    name='evrm',
    version='43',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Gif toediende artsen de cel in !!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''

Geachte Minister-President,

In 2012 heb ik het Europeese Hof voor de Rechten van de Mens aangeschreven om een klacht tegen Nederland in te dienen. 
De klacht betrof het afwezig zijn van verpleging in het nieuwe ambulante behandeltijdperk van de GGZ, uitspraak is niet-ontvankelijk.
Ik heb zowel Koningin Beatrix en Koning Willem-Alexander aangeschreven over problemen met de invoering van de (F)ACT methodiek in Nederland.
Nog voor de Koningin, noch de Koning is het mogelijke om verdere tussenkomst te verlenen.

U bent ministerieel verantwoordelijk voor de zorg die u namens de Koning aan de meest kwetsbaren in onze samenleving levert, daarom richt ik mij tot u.

gif
===

| Er is bewijs dat antipsychotica gif zijn:

1) haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
2) clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
3) olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
4) aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

Omdat het hier gif betreft is er een vermoeden dat er in deze "zorg" strafbare feiten gepleegd worden:

mishandeling
============

* De medicijnen blijken gif te zijn

300.4 Met mishandeling wordt gelijkgesteld opzettelijke benadeling van de gezondheid.

304.3 indien het misdrijf wordt gepleegd door toediening van voor het leven of de gezondheid schadelijke stoffen.

verzwijging
===========

* De arts informeert de patient niet dat het een gif betreft.
* De arts verzwijgt het schadelijk karakter van zijn medicijnen.

174.1 Hij die waren verkoopt, te koop aanbiedt, aflevert of uitdeelt, wetende dat zij voor het leven of de gezondheid schadelijk zijn, en dat schadelijk karakter verzwijgende, wordt gestraft met gevangenisstraf van ten hoogste vijftien jaren of geldboete van de vijfde categorie.

174.2 Indien het feit iemands dood ten gevolge heeft, wordt de schuldige gestraft met levenslange gevangenisstraf of tijdelijke van ten hoogste dertig jaren of geldboete van de vijfde categorie.

moord
=====

* Als de medicijnen dodelijke aandoeningen kunnen veroorzaken noem ik het medicijn dodelijk. Dodelijke stof toedienen is een misdrijf tegen het leven gericht.

285.1 Bedreiging met enig misdrijf tegen het leven gericht wordt gestraft met gevangenisstraf van ten hoogste twee jaren of geldboete van de vierde categorie.

287 Hij die opzettelijk een ander van het leven berooft, wordt, als schuldig aan doodslag, gestraft met gevangenisstraf van ten hoogste vijftien jaren of geldboete van de vijfde categorie.

289 Hij die opzettelijk en met voorbedachten rade een ander van het leven berooft, wordt, als schuldig aan moord, gestraft met levenslange gevangenisstraf of tijdelijke van ten hoogste dertig jaren of geldboete van de vijfde categorie.

294.1 Hij die opzettelijk een ander tot zelfdoding aanzet, wordt, indien de zelfdoding volgt, gestraft met een gevangenisstraf van ten hoogste drie jaren of geldboete van de vierde categorie.

eisen
=====

Om dat het hier gif toedieningen betreft en niet medicatie toedieningen eis ik van u het volgende:

1) direct ervoor zult zorgen dat de GGZ patient in staat word gesteld om daadwerkelijk aangifte te kunnen doen voor de strafbare feiten die hij in het kader van zorg geleverd aan de meest kwetsbaren in onze samenleving krijgt aangedaan.

2) direct het Openbaar Ministerie instrueren om vervolging ook daadwerkelijk in te zetten.

3) direct voor patienten die zelf geen aangifte van mishandeling kunnen doen dat voor hen te doen.

Ik neem aan dat u het met mijn eisen eens bent en deze dan ook inwilligt.

Hoogachtend,


Bart Thate

| email is bthate@dds.nl or thatebart@gmail.com 
| botfather on #dunkbots irc.freenode.net


''',
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(j("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(j("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(j("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
