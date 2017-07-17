from setuptools import setup

setup(
    name='ruuvitag-thingsboard',    
    version='0.53',                         
    scripts=['ruuvitag-thingsboard'],  
    install_requires=['paho-mqtt','ruuvitag_sensor']
)
