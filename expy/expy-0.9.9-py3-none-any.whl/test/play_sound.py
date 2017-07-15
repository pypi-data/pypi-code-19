# coding:utf-8
##### package test #####
import sys
sys.path = ['../../']+sys.path
################

from expy import *  # Import the needed functions
start(sample_rate=44100)  # Initiate the experiment environment


'''General usage'''
sound = loadSound('data/demo.WAV')  # Load the wav file
playSound(sound)  # Play the wav file
''''''
show(0.5)  # Pause (Keep displaying in 0.5s)

# Load many wav files and concat them
sound = loadManySound('data', ['ba','da','ba','da'], 'wav')
playSound(sound)
show(0.5)

# Play multiple soundtrack at the same time
sound = loadManySound('data', ['demo','demo','demo','demo'], 'wav')
playFreeSound(sound)  # Play the wav file
sound = loadManySound('data', ['ba','da','ba','da'], 'wav')
playFreeSound(sound)
show(5)

# sound = makeSound(data)
# playSound(sound)
# show(1)

sound = makeBeep(440, 0.5)
playSound(sound)

sound = makeNoise(10)
playSound(sound)

# s = makeBeep(440, 15)
s = loadManySound('data', ['ba','da','ba','da'], 'wav')
index = playAlterableSound(s,effect=change_pitch)
print('The change is', index)



