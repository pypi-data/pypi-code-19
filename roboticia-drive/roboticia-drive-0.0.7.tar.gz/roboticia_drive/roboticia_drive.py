from pypot.creatures import AbstractPoppyCreature

from .sensor import RPLidarA2, VoiceRecognition
from subprocess import call

def speak(phrase):
    call(["roboticia-speak.sh", phrase])

class RoboticiaDrive(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        for m in robot.motors:
            m.goto_behavior = 'dummy'
            m.moving_speed = 0
            m.pid = (6.0,10.0,0.0)
            
        sensor1 = RPLidarA2('lidar', 'normal')
        robot._sensors.append(sensor1)
        setattr(robot, sensor1.name, sensor1)
        
        sensor2 = VoiceRecognition('speech')
        robot._sensors.append(sensor2)
        setattr(robot, sensor2.name, sensor2)
        
        robot.speak = speak
        
        

        if robot.simulated:
            cls.vrep_hack(robot)


    @classmethod
    def vrep_hack(cls, robot):
        # fix vrep orientation bug
        wrong_motor = []
        
        for m in wrong_motor:
            m.direct = not m.direct
            #m.offset = -m.offset
            
        # use minjerk to simulate speed in vrep
        for m in robot.motors:
            m.goto_behavior = 'minjerk'

        
