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
    version='41',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Omdat het hier gif betreft !!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''

Geachte Rechter,

| Er is bewijs dat antipsychotica gif zijn:

1) haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
2) clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
3) olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
4) aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

Omdat het hier gif betreft, wil ik u verzoeken de Staat der Nederlanden direct opdracht te geven tot:

1) het van de medicijnen markt nemen van deze stoffen.

Zolang deze gifstoffen op de markt aanwezig zijn zal men ze als onschadelijk zien en zou de overheid de
schadelijkheid van dit product verzwijgen, een 15-30 jarig misdrijf.

2) medische begeleiding geven aan patienten die van de ene of de andere dag hun medicijnen moeten missen.

Het afkicken van gif is een moeilijk proces dat jaren kan duren. Patienten
die in plaats van een medicijn gif hebben gekregen moeten begeleiding
krijgen van artsen die hun symptomen zien als gevolg van de mishandeling met
gif zodat men deze patienten kan begeleiden met de onthoudingsverschijnselen.

3) mishandelingen die met deze gif stoffen zijn gepleegd te laten vervolgen.

Patienten die jarenlang zijn mishandelt met medicijnen die een gif blijken te zijn
hebben het recht om aangifte te kunnen doen van de mishandelingen die op hun
gepleegd zijn.

Ik neem aan dat u het met mij eens bent en de Staat der Nederlanden direct hiertoe opdracht zult geven.

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
