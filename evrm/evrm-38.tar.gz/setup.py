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
    version='38',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Gif toedienende artsen de cel in !!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''

.. title:: Gif toedienende artsen de cel in !!

.. image:: jpg/doodskop.jpg


Geachte Minister-President,

In 2012 heb ik het Europeese Hof voor de Rechten van de Mens :ref:`aangeschreven <evrm>` om een :ref:`klacht <greffe>` tegen Nederland in te
dienen. De klacht betrof het afwezig zijn van verpleging in het nieuwe ambulante behandeltijdperk van de GGZ, uitspraak is niet-ontvankelijk. 
Ik heb zowel Koningin Beatrix en Koning Willem-Alexander aangeschreven over problemen met de invoering van de :ref:`(F)ACT <fact>` methodiek in Nederland. 
Nog voor de :ref:`Koningin <beuker>`, noch de :ref:`Koning <beuker2>` is het mogelijke om verdere tussenkomst te verlenen.

U bent ministerieel verantwoordelijk voor de zorg die u namens de Koning aan de meest kwetsbaren in onze samenleving
levert, daarom richt ik mij tot u.

| Er is bewijs dat antipsychotica gif zijn:

1) haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
2) clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
3) olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
4) aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

Omdat het hier gif betreft, eis ik van u het volgende:

1) direct bekend te maken welke medicatie gif is.
2) direct deze medicatie van de markt te halen.
3) direct maatregelen te treffen voor patienten die zonder deze medicatie komen te zitten.
4) direct de vervolging van deze giftoedieningen door het Openbaar Minsterie ter hand te laten nemen.
5) direct een antipsychotica wet in te voeren die expliciet de toediening van deze gifstoffen onder elk denkbare omstandiheid verbied.

Als u burgers laat bellen voor een GGZ behandeling van een buurman dan maakt u hem opdrachtgever voor het plegen van gijzeling, mishandeling, verzwijging en
moord.
De rechterlijke macht is alleen geeigend tot vrijheidsontneming nadat iemand schuldig is bevonden, niet tot het toedienen van gif, het verzwijgen van de 
giftigheid en de moord met dat gif. 
U zelf kunt natuurlijk ook geen opdrachten geven voor het plegen van strafbare feiten dus waar u zelf opdracht voor geeft
voor het plegen van strafbare feiten zult u ook voor een strafrechter moeten uitleggen.

Ik neem dat u direct mijn eisen zult in willigen voor het belang van de Nederlands bevolking, men is op grote schaal gif als een medicijn aan het verkopen.

Gif toedienen is mishandeling.

.. raw:: html

    <br>



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

