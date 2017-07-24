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
    version='36',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Toegang tot de rechter voor de GGZ patient !!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''

Geachte Minister-President,

In 2012 heb ik het Europeese Hof voor de Rechten van de Mens :ref:`aangeschreven <evrm>` om een :ref:`klacht <greffe>` tegen Nederland in te
dienen. De klacht betrof het afwezig zijn van verpleging in het nieuwe ambulante behandeltijdperk van de GGZ, uitspraak is niet-ontvankelijk. 
Ik heb zowel Koningin Beatrix en Koning Willem-Alexander aangeschreven over problemen met de invoering van de :ref:`(F)ACT <fact>` methodiek in Nederland. 
Nog voor de :ref:`Koningin <beuker>`, noch de :ref:`Koning <beuker2>` is het mogelijke om verdere tussenkomst te verlenen.

Aangezien noch onze voormalige Koningin, noch onze huidige Koning, in deze zaak tussenkomst heeft kunnen verlenen, richt ik mij tot u.
U bent ministerieel verantwoordelijk voor de zorg die U namens de Koning aan de meest kwetsbaren in onze samenleving levert.

| Er is bewijs dat antipsychotica gif zijn:

1) haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
2) clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
3) olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
4) aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

Omdat het hier gif betreft, heb ik de volgende eisen aan u:

1) direct aan de Nederlandse bevolking bekend te maken dat deze medicijnen gif zijn. 
2) direct deze medicijnen van de markt te halen.
3) direct de artsen die gif hebben toegediend te vervolgen.
4) direct toegang tot de strafrechter voor de GGZ patient realiseren.

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
