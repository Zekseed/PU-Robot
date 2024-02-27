#!/usr/bin/env pybricks-micropython

from pybricks import robotics
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Create your objects here.
ev3 = EV3Brick()
claw_motor = Motor(Port.A)
Elbow_motor = Motor(Port.B)
rotation_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12,36])

# Sensor definitions
color_sensor = ColorSensor(Port.S2)
rotation_sensor = TouchSensor(Port.S1)

# Custom variables
turnSpeed = 50
claw_grip_speed = 50
elbow_angle = -180
base_rot_speed = 50
drop_off_zones = {}
drop_off_colors = [Color.RED, Color.GREEN, Color.BLUE]

def reset_robot(angle):
    rotation_motor.run_angle(base_rot_speed, -angle, then=Stop.COAST, wait=True)
    #Elbow_motor.run_target(turnSpeed, 0, then=Stop.COAST, wait=True)
    #claw_motor.run_target(claw_grip_speed, elbow_angle, then=Stop.COAST, wait=True)

def claw_grab(speed):
    return claw_motor.run_until_stalled(speed, then=Stop.HOLD, duty_limit=90)

def claw_release(speed, angle):
    claw_motor.run_angle(speed, -(angle), then=Stop.COAST, wait=True)

def lift_up(speed, angle):
    Elbow_motor.run_target(speed, angle, then=Stop.HOLD, wait=True)

def lift_down(speed, angle):
    Elbow_motor.run_angle(speed, -angle, then=Stop.COAST, wait=True)

def detect_color():
    return color_sensor.color()

def rotate_base(speed, angle):
    if angle < 0:
        angle -= 10
    else:
        angle += 10

    rotation_motor.run_angle(speed, angle, then=Stop.HOLD, wait=True)

if __name__ == '__main__':
    
    Elbow_motor.run_target(turnSpeed, elbow_angle, then=Stop.COAST, wait=True)

    index = 0
    while len(drop_off_zones) < len(drop_off_colors):
        if ev3.buttons.pressed() != []:
            print(ev3.buttons.pressed())
            drop_off_zones.update({drop_off_colors[index] : rotation_motor.angle()})
            index += 1
            wait(1000)


    print(drop_off_zones)

    reset_robot(rotation_motor.angle())

    # Reset motor angle
    claw_motor.reset_angle(0)
    rotation_motor.reset_angle(0)


    for i in range(len(drop_off_colors)):
        lift_down(turnSpeed, elbow_angle)
        grip_Angle = claw_grab(claw_grip_speed)
        lift_up(turnSpeed, elbow_angle)

        current_color = detect_color()
        rotate_base(base_rot_speed, drop_off_zones[current_color])

        wait(5000)
        lift_down(turnSpeed, elbow_angle)
        claw_release(claw_grip_speed, grip_Angle)
        lift_up(turnSpeed, elbow_angle)
        rotate_base(base_rot_speed, -drop_off_zones[current_color])
        wait(5000)
    