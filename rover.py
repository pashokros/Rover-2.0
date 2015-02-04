import time
import pygame
from pygame.locals import *
# import time
# import serial
import maestro
import roboclaw

class Rover:
    def __init__(self):
        pygame.init()
        self.gamepad = pygame.joystick.Joystick(0).init()
        self.roboclaw = roboclaw.Roboclaw(0)
        self.maestro = maestro.Maestro(1)
        self.catch(0)

    def send_speed(self, speed_l, speed_r):
        if (speed_l != self.speed_l_old) or (speed_r != self.speed_r_old):
            cur_time = time.time()
            if cur_time - self.time_old >= self.TIME_LATENCY:
                self.roboclaw.SetMixedSpeed(speed_l,speed_r)
                self.time_old = cur_time
                self.speed_l_old = speed_l
                self.speed_r_old = speed_r
                print(speed_l, speed_r)

    def catch(self, catch):
        GRAB1 = 8000
        GRAB2 = 4000
        RELEASE1 = 9000
        RELEASE2 = 8500
        if catch:
            self.maestro.setTarget(0, GRAB1)
            self.maestro.setTarget(1, GRAB2)
        else:
            self.maestro.setTarget(1, RELEASE2)
            self.maestro.setTarget(0, RELEASE1)
    
    def remap(self, OldValue, OldMin, OldMax, NewMin, NewMax):
        OldRange = (OldMax - OldMin)
        NewRange = (NewMax - NewMin)
        NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
        return NewValue

    def clamp(self, n, minn, maxn):
        if n < minn:
            return minn
        elif n > maxn:
            return maxn
        else:
            return n

    def sign(self, val):
        if val < 0: return -1
        else: return 1

    def read_input(self):
        MIN_SPEED = 500
        MAX_SPEED = 1000
        TANK_MAX_SPEED = 1100
        SLOW_RATIO = 0.5
        FAST_MAX_SPEED = 1200
        # Left stick
        X1_AXIS = 0
        Y1_AXIS = 1
        # Right stick
        X2_AXIS = 4
        Y2_AXIS = 3
        # Dead zone
        Y_DZONE = 0.1
        X_DZONE = 0.1
        # Buttons
        X_BUTTON = 2
        Y_BUTTON = 3
        B_BUTTON = 1
        A_BUTTON = 0
        STOP_BUTTON = 5
        FAST_BUTTON = 4
        self.TIME_LATENCY = 0.0

        control_scheme = 1
        speed_mode = 1 # 0 - Slow Mode, 1 - Normal Mode, 2 - Speed Mode
        max_speed = MAX_SPEED
        speed = 0
        speed_l = 0
        speed_r = 0
        steer = 0
        catch = 0
        self.speed_l_old = 0
        self.speed_r_old = 0
        self.claw_old = 0
        self.time_old = 0

        while 1:
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN:
                    print(str(event.button))
                    if event.button == X_BUTTON:
                        control_scheme = 1
                        print('Scheme 1')
                    if event.button == Y_BUTTON:
                        control_scheme = 2
                        print('Scheme 2')
                    # On/Off
                    if event.button == B_BUTTON:
                        if speed_mode != 0: speed_mode = 0
                        else: speed_mode = 1
                        if speed_mode == 0:
                            max_speed = MAX_SPEED * SLOW_RATIO
                            print('Slow Mode')
                        else:
                            max_speed = MAX_SPEED
                            print('Normal Mode')
                    #
                    if event.button == A_BUTTON:
                        catch = not catch
                        print('Catch')
                        self.catch(catch)

                    if event.button == STOP_BUTTON:
                        print('STOP')
                        self.send_speed(0, 0)

                    if event.button == FAST_BUTTON:
                        if speed_mode != 2: speed_mode = 2
                        else: speed_mode = 1
                        if speed_mode == 2:
                            max_speed = FAST_MAX_SPEED
                            print('FAST Mode')
                        else:
                            max_speed = MAX_SPEED
                            print('Normal Mode')

                if event.type == JOYAXISMOTION:
                    # Scheme 1
                    if control_scheme == 1:
                        # Forward
                        if event.axis == Y1_AXIS:
                            if abs(event.value) > Y_DZONE:
                                speed = -self.sign(event.value)*self.remap(abs(event.value), Y_DZONE, 1, MIN_SPEED, max_speed)
                            else: speed = 0
                        # Turns
                        if event.axis == X1_AXIS:
                            if abs(event.value) > X_DZONE: steer = event.value
                            else: steer = 0
                        speed_r = speed*(1 + steer)
                        speed_l = speed*(1 - steer)
                        # Speed Limit
                        speed_l = self.clamp(speed_l, -max_speed, max_speed)
                        speed_r = self.clamp(speed_r, -max_speed, max_speed)
                        # Rover rotation
                        if event.axis == X2_AXIS:
                            if abs(event.value) > Y_DZONE:
                                speed_l =  -self.sign(event.value)*self.remap(abs(event.value), Y_DZONE, 1, MIN_SPEED, TANK_MAX_SPEED)
                                speed_r =  self.sign(event.value)*self.remap(abs(event.value), Y_DZONE, 1, MIN_SPEED, TANK_MAX_SPEED)

                    # Scheme 2
                    if control_scheme == 2:
                        # Left track
                        if event.axis == Y1_AXIS:
                            if abs(event.value) > Y_DZONE:
                                speed_l = -self.sign(event.value)*self.remap(abs(event.value), Y_DZONE, 1, MIN_SPEED, max_speed)
                            else: speed_l = 0
                        # Right track
                        if event.axis == Y2_AXIS:
                            if abs(event.value) > Y_DZONE:
                                speed_r = -self.sign(event.value)*self.remap(abs(event.value), Y_DZONE, 1, MIN_SPEED, max_speed)
                            else: speed_r = 0
                    speed_l = int(speed_l)
                    speed_r = int(speed_r)
                    self.send_speed(speed_l, speed_r)

rover = Rover()
rover.read_input()