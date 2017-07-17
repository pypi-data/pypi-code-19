from setuptools import setup

setup(
    name='ruuvitag-thingsboard',    
    version='0.5',                         
    scripts=['ruuvitag-thingsboard'],  
    install_requires=['paho-mqtt','ruuvitag_sensor']
)
