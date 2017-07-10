#!/usr/bin/env python3

import asyncio
from . import _util as util

from .async import *
from .async import message_pb2 as prex_pb
from .peripherals import *

import math
import os
import websockets

__all__ = ['FormFactor', 'Linkbot', 'Daemon', 'CLinkbot', 'ArduinoLinkbot']
__all__ += async.__all__

class Daemon():
    def __init__(self):
        self.__io_core = util.IoCore()
        self._loop = self.__io_core.get_event_loop()
    
        fut = util.run_coroutine_threadsafe(
                AsyncDaemon.create(), self._loop)
        try:
            self._proxy = fut.result()
        except:
            raise Exception("Could not connect to daemon.")

    def cycle(self, seconds):
        util.run_coroutine_threadsafe(
            self._proxy.cycle(seconds),
            self._loop)

    def ping(self, destinations = [], peripheral_reset_mask = 0x1F):
        fut = util.run_coroutine_threadsafe(
            self._proxy.ping(destinations, peripheral_reset_mask), 
            self._loop)
        fut.result()

class FormFactor():
    I = 0
    L = 1
    T = 2
    DONGLE = 3

class Linkbot():
    MOTOR1 = 0
    MOTOR2 = 1
    MOTOR3 = 2
    LED = 3
    BUZZER = 4
    
    def __init__(self, serial_id=None):
        ''' Create a new Linkbot handle.

        :param serial_id: The 4 digit alpha-numeric unique Linkbot identifier
            printed on the top of the Linkbot.
        :type serial_id: string
        :raises concurrent.futures._base.TimeoutError: if the remote robot
            cannot be be reached.
        '''
        self.__io_core = util.IoCore()
        self._loop = self.__io_core.get_event_loop()
    
        fut = util.run_coroutine_threadsafe(
                AsyncLinkbot.create(serial_id), self._loop)
        self._proxy = fut.result()
       
        self._accelerometer = Accelerometer(self)
        self._battery = Battery(self)
        self._button = Button(self)
        self._buzzer = Buzzer(self)
        self._eeprom_obj = Eeprom(self)
        self._led = Led(self)
        self._motors = Motors(self)
        self._twi = Twi(self)
        self._serial_id = serial_id

    @property
    def serial_id(self):
        raw_id = self._eeprom.read(0x412, 4)
        return raw_id.decode()

    def _set_serial_id(self, serial_id):
        assert( len(serial_id) == 4 )
        self._eeprom.write(0x412, serial_id.encode())

    @property
    def accelerometer(self):
        '''
        The robot accelerometer.

        See :class:`linkbot3.peripherals.Accelerometer`
        '''
        return self._accelerometer

    @property
    def battery(self):
        '''
        The robot battery.

        See :class:`linkbot3.peripherals.Battery`
        '''
        return self._battery

    @property
    def buttons(self):
        '''
        Access to the robot's buttons.

        See :class:`linkbot3.peripherals.Button`
        '''
        return self._button

    @property
    def buzzer(self):
        '''
        Control the Linkbot's buzzer.

        See :class:`linkbot3.peripherals.Buzzer`
        '''
        return self._buzzer

    def disconnect(self):
        '''
        Disconnect from the Linkbot.
        '''
        util.run_coroutine_threadsafe(self._proxy.disconnect(), self._loop)

    @property
    def _eeprom(self):
        """
        Access the robot's EEPROM memory.

        Warning: Improperly accessing the robot's EEPROM memory may yield
        unexpected results. The robot uses EEPROM memory to store information
        such as its serial ID, calibration data, etc.
        """
        return self._eeprom_obj

    def form_factor(self):
        '''
        Get the form factor of the Linkbot. See :class:`linkbot3.FormFactor`.
        '''
        return util.run_linkbot_coroutine(self._proxy.form_factor(), self._loop)

    @property
    def led(self):
        '''
        Access to the robot's multi-color LED.

        See :class:`linkbot3.peripherals.Led`.
        '''
        return self._led

    @property
    def motors(self):
        """
        The motors of the Linkbot.

        See :class:`linkbot3.peripherals.Motors` . To access individual motors,
        you may do::

            Linkbot.motors[0].is_moving()

        or similar. Also see :class:`linkbot3.peripherals.Motor`
        """
        return self._motors

    @property
    def twi(self):
        """
        Access the I2C two-wire interface of the Linkbot.

        See :class:`linkbot3.peripherals.Twi` .
        """
        return self._twi

    def reboot(self):
        util.run_linkbot_coroutine(
            self._proxy.reboot(),
            self._loop)
    
    def set_peripherals_reset(self, peripheral_mask, mask=0xff):   
        '''
        Specify which peripherals to reset when the robot is disconnected.

        Values should be "1<<Linkbot.MOTOR1 | 1<<Linkbot.LED", etc. Valid peripheral_mask values are:

        Linkbot.MOTOR1
        Linkbot.MOTOR2
        Linkbot.MOTOR3
        Linkbot.LED
        Linkbot.BUZZER

        or any or'd combination thereof.
        '''
        return util.run_linkbot_coroutine(self._proxy.set_peripherals_reset(peripheral_mask, mask), self._loop)

    def version(self):
        '''
        Get the firmware version

        :rtype: (int, int, int)
        '''
        return util.run_linkbot_coroutine(
                self._proxy.version(),
                self._loop)

class CLinkbot(Linkbot):
    class FormFactor:
        I = 0
        L = 1
        T = 2

    class JointStates:
        STOP = 0
        HOLD = 1
        MOVING = 2
        FAIL = 3
    def __init__(self, serial_id):
        super().__init__(serial_id)

    # This method allows us to programatically support both mixedCase and
    # lowercase_with_underscore method names. If an attribute cannot be found,
    # it is converted to the equivalent lowercase attribute name and checked
    # again. If it still cannot be found, AttributeError is raised.
    def __getattr__(self, name):
        # Strategy: First, convert the name to a PEP8 style name and see if it
        # is an attribute. If it is, return that. If not, try to see if the
        # original name is an attribute and return that. If not, raise
        # AttributeError.
        origname = name
        # Convert the name to a new PEP8 style name
        import re
        if name.endswith('NB'):
            name = name[:-2] + 'Nb'
        if name.endswith('CB'):
            name = name[:-2] + 'Cb'
        newname = re.sub(r'([A-Z])', lambda x: '_'+x.group(1).lower(), name)
        if newname == origname:
            raise AttributeError(origname)
        # return self.__dict__[newname]
        return getattr(self, newname)

    # GETTERS
    def get_accelerometer(self):
        '''Get the current accelerometer values for 3 primary axes

        :rtype: (number, number, number)
          Returned values are expressed in "G's", where one G is equivalent
          to one earth-gravity, or 9.81 m/s/s.
        '''
        return self.accelerometer.values()

    def get_accelerometer_data(self):
        return self.get_accelerometer()

    def get_battery_voltage(self):
        ''' Get the robot's current battery voltage '''
        return self.battery.voltage()

    def get_form_factor(self):
        return self.form_factor()

    def get_joint_angle(self, joint):
        '''
        Get the current angle for a particular joint

        
        :type joint: int 
        :param joint: The joint number of robot.

        Example::

            # Get the joint angle for joint 1
            angle = robot.get_joint_angle(1)
        '''
        return self.motors[joint-1].angle()

    def get_joint_angles(self):
        '''
        Get the current joint angles of the robot.

        :rtype: (number, number, number)
           Returned values are in degrees. The three values indicate the
           joint angles for joints 1, 2, and 3 respectively. Values
           for joints which are not movable (i.e. joint 2 on a Linkbot-I)
           are always zero.

        Example::

            j1, j2, j3 = robot.get_joint_angles()

        '''
        a1, a2, a3, _ = self.motors.angles()
        return (a1, a2, a3)

    def get_joint_speed(self, joint):
        """Get the current speed for a joint

        :param joint: A joint number.
        :type joint: int
        :rtype: float (degrees/second)

        Example::

            # Get the joint speed for joint 1
            speed = robot.get_joint_speed(1)
        """
        return self.motors[joint-1].omega()

    def get_joint_speeds(self):
        r = ()
        for i in range(3):
            r += (self.motors[i].omega(),)
        return r

    def get_led_color(self):
        return self.led.color()

    def get_serial_id(self):
        return self.serial_id

    # SETTERS
    def reset_to_zero(self):
        self.motors.reset()
        self.motors.move([0, 0, 0], relative=False)

    def reset_to_zero_nb(self):
        self.motors.reset()
        self.motors.move([0, 0, 0], relative=False, wait=False)

    def set_buzzer_frequency(self, freq):
        '''
        Set the Linkbot's buzzer frequency. Setting the frequency to zero turns
        off the buzzer.

        :type freq: int
        :param freq: The frequency to set the buzzer, in Hertz.
        '''
        self.buzzer.set_frequency(float(freq))

    def set_joint_acceleration(self, joint, alpha):
        ''' Set a single joint's acceleration value.

        See :func:`Linkbot.set_joint_accelerations` and 
        :func:`CLinkbot.move_smooth` .
        '''
        self.motors[joint-1].set_accel(alpha)

    def set_joint_accelerations(self, alpha1, alpha2, alpha3, mask=0x07):
        '''
        Set the rate at which joints should accelerate during "smoothed"
        motions, such as "move_smooth". Units are in deg/sec/sec.
        '''
        for i, alpha in enumerate([alpha1, alpha2, alpha3]):
            if (1<<i) & mask:
                self.motors[i].set_accel(alpha)

    def set_joint_deceleration(self, joint, alpha):
        ''' Set a single joint's deceleration value.

        See :func:`Linkbot.set_joint_decelerations` and 
        :func:`Linkbot.move_smooth` .
        '''
        self.motors[joint-1].set_decel(alpha)

    def set_joint_decelerations(self, alpha1, alpha2, alpha3, mask=0x07):
        '''
        Set the rate at which joints should decelerate during "smoothed"
        motions, such as "move_smooth". Units are in deg/sec/sec.
        '''
        for i, alpha in enumerate([alpha1, alpha2, alpha3]):
            if (1<<i) & mask:
                self.motors[i].set_decel(alpha)

    def set_joint_speed(self, joint, speed):
        '''
        Set the speed for a single joint on the robot.

        :type joint: int
        :param JointNo: The joint to set the speed. Should be 1, 2, or 3.
        :type speed: float
        :param speed: The new speed of the joint, in degrees/second.

        Example::

            # Set the joint speed for joint 3 to 100 degrees per second
            robot.set_joint_speed(3, 100)
        '''
        self.motors[joint-1].set_omega(speed)

    def set_joint_speeds(self, s1, s2, s3, mask=0x07):
        """Set the joint speeds for all of the joints on a robot.

        :type s1: float
        :param s1: The speed, in degrees/sec, to set the first joint. Parameters
            s2 and s3 are similar for joints 2 and 3.
        :type mask: int 
        :param mask: (optional) A bitmask to specify which joints to modify the
           speed. The speed on the robot's joint is only changed if
           (mask&(1<<(joint-1))).
        """
        for i, speed in enumerate([s1, s2, s3]):
            if (1<<i) & mask:
                self.motors[i].set_omega(speed)

    def set_led_color(self, r, g, b):
        ''' Set the LED color on the robot.

        :type r: int [0,255]
        :type g: int [0,255]
        :type b: int [0,255]
        '''
        self.led.set_color(r, g, b)

    def set_motor_power(self, joint, power):
        """Apply a direct power setting to a motor
        
        :type joint: int (1,3)
        :param joint: The joint to apply the power to
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        self.motors[joint-1].set_power(power)

    def set_motor_powers(self, power1, power2, power3, mask=0x07):
        """Apply a direct power setting to all motors
        
        :type power: int (-255,255)
        :param power: The power to apply to the motor. 0 indicates no power
        (full stop), negative number apply power to turn the motor in the
        negative direction.
        """
        self.motors.set_powers([power1, power2, power3], mask)

    # MOVEMENT
    def __set_controller(self, value):
        for m in self.motors:
            m.set_controller(value)

    def drive(self, j1, j2, j3, mask=0x07):
        """Move a robot's motors using the on-board PID controller. 

        This is the fastest way to get a Linkbot's motor to a particular angle
        position. The "speed" setting of the joint is ignored during this
        motion.

        :type j1: float
        :param j1: Relative angle in degrees to move the joint. If a joint is
              currently at a position of 30 degrees and a 90 degree drive is
              issued, the final position of the joint will be at 120 degrees.
              Parameters j2 and j3 are similar for joints 2 and 3.
        :type mask: int
        :param mask: (optional) A bitmask to specify which joints to move. 
              The robot will only move joints where (mask&(1<<(joint-1))) is
              true.
        """
        self.__set_controller(Motor.Controller.PID)
        self.motors.move([j1, j2, j3], mask=mask)

    def drive_nb(self, j1, j2, j3, mask=0x07):
        """Non blocking version of :func:`CLinkbot.drive`."""
        self.__set_controller(Motor.Controller.PID)
        self.motors.move([j1, j2, j3], mask=mask, wait=False)

    def drive_joint(self, joint, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`CLinkbot.drive`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.
        """
        self.motors[joint-1].set_controller(Motor.Controller.PID)
        self.motors[joint-1].move(angle)

    def drive_joint_nb(self, joint, angle):
        """Non-blocking version of :func:`Linkbot.drive_joint`"""
        self.motors[joint-1].set_controller(Motor.Controller.PID)
        self.motors[joint-1].move(angle, wait=False)

    def drive_joint_to(self, joint, angle):
        """Move a single motor using the on-board PID controller.

        This is the fastest way to drive a single joint to a desired position.
        The "speed" setting of the joint is ignored during the motion. See also:
        :func:`CLinkbot.drive`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: An absolute angle in degrees to move the joint. 

        Example::

            robot.driveJointTo(1, 20)
            # Joint 1 is now at the 20 degree position.
            # The next line of code will move joint 1 10 degrees in the negative
            # direction.
            robot.drive_joint_to(1, 10)
        """
        self.motors[joint-1].set_controller(Motor.Controller.PID)
        self.motors[joint-1].move(angle, relative=False)
        
    def drive_joint_to_nb(self, joint, angle):
        """Non-blocking version of :func:`CLinkbot.drive_joint_to`"""
        self.motors[joint-1].set_controller(Motor.Controller.PID)
        self.motors[joint-1].move(angle, relative=False, wait=False)

    def drive_to(self, j1, j2, j3, mask=0x07):
        """Move a robot's motors using the on-board PID controller. 

        This is the fastest way to get a Linkbot's motor to a particular angle
        position. The "speed" setting of the joint is ignored during this
        motion.

        :type j1: float
        :param j1: Absolute angle in degrees to move the joint. If a joint is
              currently at a position of 30 degrees and a 90 degree drive is
              issued, the joint will move in the positive direction by 60 
              degrees.
              Parameters j2 and j3 are similar for joints 2 and 3.
        :type mask: int
        :param mask: (optional) A bitmask to specify which joints to move. 
              The robot will only move joints where (mask&(1<<(joint-1))) is
              true.
        """
        self.__set_controller(Motor.Controller.PID)
        self.motors.move([j1, j2, j3], mask=mask, relative=False)

    def drive_to_nb(self, j1, j2, j3, mask=0x07):
        """Non-blocking version of :func:`linkbot3.CLinkbot.drive_to`"""
        self.__set_controller(Motor.Controller.PID)
        self.motors.move([j1, j2, j3], mask=mask, wait=False, relative=False)

    def drive_angle(self, angle):
        """Drive the motors of a 2-wheeled Linkbot by "angle" degrees.

        (Since v3.1.11)

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.drive_angle_nb(angle)
        self.move_wait()

    def drive_angle_nb(self, angle):
        """Drive the motors of a 2-wheeled Linkbot by "angle" degrees.

        (Since v3.1.11)

        This is the non-blocking version of :func:`linkbot3.CLinkbot.drive_angle`.

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.move_nb(angle, 0, -angle)

    def drive_backward(self, angle):
        """Drive the motors of a 2-wheeled Linkbot backward by "angle" degrees.

        (Since v3.1.11)

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.drive_backward_nb(angle)
        self.move_wait()

    def drive_backward_nb(self, angle):
        """Drive the motors of a 2-wheeled Linkbot backward by "angle" degrees.

        (Since v3.1.11)

        This is the non-blocking version of :func:`linkbot3.CLinkbot.drive_backward`.

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.move_nb(-angle, 0, angle)

    def drive_distance(self, distance, radius):
        """Drive the motors of a 2-wheeled Linkbot to move forward by "distance"

        (Since v3.1.11)

        :type distance: float
        :param distance: A distance. The units used here can be any unit of
            length, as long as the same units are used for the "radius" parameter.
        :type radius: float
        :param radius: The radius of the Linkbot's wheels. The units of radius
            can be anything as long as they are the same units as those used for
            the "distance" parameter.
        """
        self.drive_distance_nb(distance, radius)
        self.move_wait()

    def drive_distance_nb(self, distance, radius):
        """Drive the motors of a 2-wheeled Linkbot to move forward by "distance"

        (Since v3.1.11)

        This is the non-blocking version of :func:`linkbot3.CLinkbot.drive_distance`.

        :type distance: float
        :param distance: A distance. The units used here can be any unit of
            length, as long as the same units are used for the "radius" parameter.
        :type radius: float
        :param radius: The radius of the Linkbot's wheels. The units of radius
            can be anything as long as they are the same units as those used for
            the "distance" parameter.
        """
        angle = (distance / radius) * 180 / math.pi
        self.drive_angle_nb(angle)

    def drive_forever_nb(self):
        """Drive the motors of a 2-wheeled Linkbot forward ad-infinitum

        (Since v3.1.11)
        
        This non-blocking function will make a 2-wheeled Linkbot-I begin
        driving forward. It will remain driving forward until it receives other
        movement commands.
        """
        self.motors.begin_move(
            0x05,
            timeouts = (0, 0, 0),
            forward = (True, True, False),
            states_on_timeout = (peripherals.Motor.State.HOLD,)*3,
            wait=False
            )

    def drive_forward(self, angle):
        """Drive the motors of a 2-wheeled Linkbot forward by "angle" degrees.

        (Since v3.1.11)

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.drive_forward_nb(angle)
        self.move_wait()

    def drive_forward_nb(self, angle):
        """Drive the motors of a 2-wheeled Linkbot forward by "angle" degrees.

        (Since v3.1.11)

        This is the non-blocking version of :func:`linkbot3.CLinkbot.drive_forward`.

        :type angle: float
        :param angle: An angle in degrees.
        """
        self.move_nb(angle, 0, -angle)

    def drive_time(self, seconds):
        """Drive the motors of a 2-wheeled Linkbot forward for a set amount of time.

        (Since v3.1.11)

        :type seconds: float
        :param seconds: The number of seconds to drive the motors.
        """
        self.drive_time_nb(seconds)
        self.move_wait(0x05)

    def drive_time_nb(self, seconds):
        """Drive the motors of a 2-wheeled Linkbot forward for a set amount of time.

        (Since v3.1.11)

        This is the non-blocking version of :func:`linkbot3.CLinkbot.drive_time`.

        :type seconds: float
        :param seconds: The number of seconds to drive the motors.
        """
        self.motors.begin_move(
            0x05,
            timeouts = (seconds, 0, seconds),
            forward = (True, True, False),
            states_on_timeout = (peripherals.Motor.State.HOLD,)*3,
            wait=False)


    def move(self, j1, j2, j3, mask=0x07):
        '''Move the joints on a robot and wait until all movements are finished.

        Move a robot's joints at the constant velocity previously set by a call
        to :func:`CLinkbot.set_joint_speed` or similar functions.

        :type j1: float
        :param j1: An angle in degrees. The joint moves this amount from wherever the joints are currently positioned.

        Example::

            robot.move(90, 0, -90) # Drives Linkbot-I forward by turning wheels
                                   # 90 degrees.
        '''
        self.__set_controller(Motor.Controller.CONST_VEL)
        self.motors.move([j1, j2, j3], mask=mask)

    def move_nb(self, j1, j2, j3, mask=0x07):
        '''Non-blocking version of :func:`Linkbot.move`

        Example::

            # The following code makes a Linkbot-I change its LED color to red 
            # and then blue while it is rolling forward.
            robot.move_nb(90, 0, -90)
            robot.set_led_color(255, 0, 0)
            time.sleep(0.5)
            robot.set_led_color(0, 0, 255)

        '''
        self.__set_controller(Motor.Controller.CONST_VEL)
        self.motors.move([j1, j2, j3], mask=mask, wait=False)


    def move_continuous(self, mask=0x07):
        '''
        This function makes the joints on a robot begin moving continuously,
        "forever". 

        Begin moving the joint at whatever speed the joint was last set to with
        the setJointSpeeds() function.
        '''
        self.__set_controller(Motor.Controller.CONST_VEL)
        self.motors.begin_move(mask=mask)

    def move_joint(self, joint, angle):
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`CLinkbot.set_joint_speed` or other speed setting functions.
        See also: :func:`CLinkbot.move`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 90 degrees, and then moves joint
            # 3 90 degrees after joint 1 has stopped moving.
            robot.move_joint(1, 90)
            robot.move_joint(3, 90)
        """
        self.motors[joint-1].set_controller(Motor.Controller.CONST_VEL)
        self.motors[joint-1].move(angle)

    def move_joint_nb(self, joint, angle):
        '''Non-blocking version of :func:`CLinkbot.move_joint`
        '''
        self.motors[joint-1].set_controller(Motor.Controller.CONST_VEL)
        self.motors[joint-1].move(angle, wait=False)

    def move_joint_to(self, joint, angle):
        """Move a single motor using the on-board constant velocity controller.

        Move a single joint at the velocity last set by
        :func:`CLinkbot.set_joint_speed` or other speed setting functions. The 
        'angle' parameter is the absolute position you want the motor to move
        to.
        See also: :func:`CLinkbot.move`

        :type joint: int
        :param joint: The joint to move.
        :type angle: float
        :param angle: A relative angle in degrees to move the joint.

        Example::

            # The following code moves joint 1 to the 90 degree position, and 
            # then moves joint3 to the 90 degree position after joint 1 has 
            # stopped moving.
            robot.move_joint_to(1, 90)
            robot.move_joint_to(3, 90)
        """
        self.motors[joint-1].set_controller(Motor.Controller.CONST_VEL)
        self.motors[joint-1].move(angle, relative=False)

    def move_joint_to_nb(self, joint, angle):
        '''Non-blocking version of :func:`Linkbot.move_joint_to`
        '''
        self.motors[joint-1].set_controller(Motor.Controller.CONST_VEL)
        self.motors[joint-1].move(angle, relative=False, wait=False)

    def move_joint_wait(self, joint):
        ''' Wait for a single joint to stop moving.

        This function blocks until the joint specified by the parameter
        ``joint`` stops moving.

        :type joint: int
        :param joint: The joint to wait for.

        '''
        self.motors[joint-1].move_wait()

    def move_joint_smooth(self, joint, angle):
        ''' Move a single joint using the "Smooth" motor controller.

        See :func:`CLinkbot.move_smooth` 
        '''
        self.motors[joint-1].set_controller(Motor.Controller.SMOOTH)
        self.motors[joint-1].move(angle)

    def move_joint_smooth_nb(self, joint, angle):
        ''' Non-blocking version of :func:`Linkbot.move_joint_smooth` '''
        self.motors[joint-1].set_controller(Motor.Controller.SMOOTH)
        self.motors[joint-1].move(angle, wait=False)

    def move_smooth(self, j1, j2, j3, mask=0x07):
        ''' Move joints with smooth acceleration and deceleration.

        The acceleration and deceleration can be set with the functions
        :func:`Linkbot.set_joint_accelerations` and 
        :func:`Linkbot.set_joint_decelerations`. The maximum velocity the 
        joint will travel at during the motion can be set with the
        :func:`Linkbot.set_joint_speeds` family of functions.

        :type j1: float
        :param j1: Number of degrees to move joint 1. Similar for j2 and j3.

        Example::

            # Move joint 1 720 degrees, accelerating at 45 deg/sec, traveling at
            # a maximum speed of 90 deg/sec, and decelerating at 120 deg/sec at
            # the end of the motion.
            robot.set_joint_accelerations(45, 45, 45)
            robot.set_joint_speeds(90, 90, 90)
            robot.set_joint_decelerations(120, 120, 120)
            robot.move_smooth(720, 0, 0)
        '''
        self.__set_controller(Motor.Controller.SMOOTH)
        self.move([j1, j2, j3], mask=mask)

    def move_smooth_nb(self, j1, j2, j3, mask=0x07):
        '''Non-blocking version of :func:`Linkbot.move_smooth` '''
        self.__set_controller(Motor.Controller.Smooth)
        self.move([j1, j2, j3], mask=mask, wait=False)
        
    def move_smooth_to(self, j1, j2, j3, mask=0x07):
        ''' Move joints with smooth acceleration and deceleration.

        The acceleration and deceleration can be set with the functions
        :func:`Linkbot.set_joint_accelerations` and 
        :func:`Linkbot.set_joint_decelerations`.

        :type j1: float
        :param j1: The position to move joint 1 to (in degrees).
        '''
        self.__set_controller(Motor.Controller.SMOOTH)
        self.move([j1, j2, j3], mask=mask, relative=False)
        
    def move_smooth_to_nb(self, j1, j2, j3, mask=0x07):
        ''' Non-blocking version of :func:`move_smooth_to` '''
        self.__set_controller(Motor.Controller.Smooth)
        self.move([j1, j2, j3], mask=mask, wait=False, relative=False)

    def move_to(self, j1, j2, j3, mask=0x07):
        ''' Move a Linkbot's joints to specified degree locations. '''
        self.__set_controller(Motor.Controller.CONST_VEL)
        self.motors.move([j1, j2, j3], mask=mask, relative=False)

    def move_to_nb(self, j1, j2, j3, mask=0x07):
        ''' Non-blocking version of :func:`CLinkbot.move_to` '''
        self.__set_controller(Motor.Controller.CONST_VEL)
        self.motors.move([j1, j2, j3], mask=mask, relative=False, wait=False)

    def move_wait(self, mask=0x07):
        ''' Wait for all masked joints (all joints by default) to stop moving.
        '''
        self.motors.move_wait(mask=mask)

    def stop_joint(self, joint):
        '''
        Stop a single joint on the robot, immediately making the joint coast.
        '''
        self.motors[joint-1].stop()

    def stop(self, mask=0x07):
        '''Immediately stop and relax all joints on the Linkbot.'''
        self.motors.stop(mask=mask)

    def turn_left(self, angle, radius=1.75, track_length=3.7):
        '''
        Turn a two-wheeled robot left by a number of degrees.

        :param angle: The number of degrees you want to turn a two-wheeled Linkbot to the left
        :param radius: The radius of the wheels
        :param track_length: The distance between the wheels
        '''
        diameter = radius*2
        self.motors.move([
            track_length*(-1*angle)/diameter,
            0,
            track_length*(-1*angle)/diameter])

    def turn_left_nb(self, angle, radius=1.75, track_length=3.7):
        '''
        Non-blocking version of :func:`CLinkbot.turn_left`.

        :param angle: The number of degrees you want to turn a two-wheeled Linkbot to the left
        :param radius: The radius of the wheels
        :param track_length: The distance between the wheels
        '''
        diameter = radius*2
        self.motors.move([
            track_length*(-1*angle)/diameter,
            0,
            track_length*(-1*angle)/diameter],
            wait=False)

    def turn_right(self, angle, radius=1.75, track_length=3.7):
        '''
        Turn a two-wheeled robot right by a number of degrees.

        :param angle: The number of degrees you want to turn a two-wheeled Linkbot to the right
        :param radius: The radius of the wheels
        :param track_length: The distance between the wheels
        '''
        diameter = radius*2
        self.motors.move([
            track_length*(angle)/diameter,
            0,
            track_length*(angle)/diameter])

    def turn_right_nb(self, angle, radius=1.75, track_length=3.7):
        '''
        Non-blocking version of :func:`CLinkbot.turn_right`.

        :param angle: The number of degrees you want to turn a two-wheeled Linkbot to the right
        :param radius: The radius of the wheels
        :param track_length: The distance between the wheels
        '''
        diameter = radius*2
        self.motors.move([
            track_length*(angle)/diameter,
            0,
            track_length*(angle)/diameter],
            wait=False)

    # Events
    def enable_accelerometer_events(self, callback, granularity=0.05):
        self.accelerometer.set_event_handler(callback, granularity)

    def disable_accelerometer_events(self):
        self.accelerometer.set_event_handler()

    def enable_button_events(self, callback):
        self.buttons.set_event_handler(callback)

    def disable_button_events(self):
        self.buttons.set_event_handler(None)

    def enable_encoder_events(self, callback, granularity=2.0):
        self.motors.set_event_handler(callback, granularity)

    def disable_encoder_events(self):
        self.motors.set_event_handler(None)

class ArduinoLinkbot(Linkbot):
    TWI_ADDR = 0x02

    class PinMode:
        input = 0
        output = 1
        input_pullup = 2

    class Command:
        header = 0x22
        register_access = 0x01
        pin_mode = 0x02
        digital_write = 0x03
        digital_read = 0x04
        analog_write = 0x05
        analog_read = 0x06
        analog_ref = 0x07

    def analog_write(self, pin, value):
        buf = bytes([
            self.Command.header,
            self.Command.analog_write, 
            pin, 
            value])
        self.twi.write(self.TWI_ADDR, buf)

    def analog_read(self, pin):
        buf = bytes([
            self.Command.header,
            self.Command.analog_read, 
            pin])
        data = self.twi.write_read(self.TWI_ADDR, buf, 2)
        value = (data[0]<<8) + data[1]
        return value

    def digital_write(self, pin, value):
        buf = bytes([
            self.Command.header,
            self.Command.digital_write, 
            pin, 
            value])
        self.twi.write(self.TWI_ADDR, buf)
    
    def digital_read(self, pin):
        buf = bytes([
            self.Command.header,
            self.Command.digital_read, 
            pin])
        value = self.twi.write_read(self.TWI_ADDR, buf, 1)
        return value[0]

    def pin_mode(self, pin, mode):
        buf = bytes([
            self.Command.header,
            self.Command.pin_mode, 
            pin, 
            mode])
        self.twi.write(self.TWI_ADDR, buf)

class PrexChannel(metaclass=util.Singleton):
    def __init__(self):
        self.__io_core = util.IoCore()
        self._loop = self.__io_core.get_event_loop()
        self.socket = None
        self._port = None
        try:
            self._port = os.environ['PREX_IPC_PORT']
            fut = util.run_coroutine_threadsafe(self.connect(), self._loop)
            fut.result()
        except KeyError as e:
            pass

    @asyncio.coroutine
    def connect(self):
        if not self._port:
            raise RuntimeError(
                'No port was specified for the PREX communications channel. Perhaps the'
                'environment variable is not set?'
            )
        self.socket = yield from websockets.connect('ws://localhost:'+str(self._port))

    def input(self, prompt):
        # Inform the PREX server that the remote process is now waiting for
        # user input.
        fut = util.run_coroutine_threadsafe(self.__input(prompt), self._loop)
        fut.result()

    @asyncio.coroutine
    def __input(self, prompt):
        io = prex_pb.Io()
        io.type = prex_pb.Io.STDIN
        io.data = prompt.encode()
        msg = prex_pb.PrexMessage()
        msg.type = prex_pb.PrexMessage.IO
        msg.payload = io.SerializeToString()
        yield from self.socket.send(msg.SerializeToString())

    def image(self, data, format='SVG'):
        # Send image data back to the web app
        fut = util.run_coroutine_threadsafe(self.__image(data, format), self._loop)
        fut.result()

    def __image(self, data, format='SVG'):
        image = prex_pb.Image()
        image.payload = data
        image.format = format
        msg = prex_pb.PrexMessage()
        msg.type = prex_pb.PrexMessage.IMAGE
        msg.payload = image.SerializeToString()
        yield from self.socket.send(msg.SerializeToString())

def scatter_plot(*args, **kwargs):
    ''' A helper function to generate and display graphical plots.

    :param args: These arguments are passed directly to matplotlib.pyplot.plot.
        Please see: http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot

        If the process is being executed as a Prex child process, the arguments
        should be in the format: [xs], [ys], [xs], [ys], ... etc.
    '''
    port = None
    try:
        port = os.environ['PREX_IPC_PORT']
    except KeyError as e:
        pass

    if port:
        scatter_plot_json(*args, **kwargs)
        return

    import io
    import matplotlib

    import matplotlib.pyplot as plt

    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111)
    ax.plot(*args, **kwargs)
    plt.show()

def scatter_plot_json(*args, **kwargs):
    import json
    data = []
    i = 0

    port = os.environ['PREX_IPC_PORT']
    if not port:
        raise IOError('No PREX port detected. Is the PREX_IPC_PORT environment variable set?')

    if len(args)%2 != 0:
        raise ValueError('Expected even number of arguments')

    for i,arg in enumerate(args):
        if 0 == (i%2):
            # Parse an "X" axis
            data.append({})
            data[-1]['type'] = 'scatter'
            data[-1]['x'] = arg
        else:
            data[-1]['y'] = arg

    channel = PrexChannel()
    print(json.dumps(data).encode())
    channel.image(json.dumps(data).encode(), format='JSON')

