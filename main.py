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
import json

# Create your objects here.
ev3 = EV3Brick()
claw_motor = Motor(Port.A)
Elbow_motor = Motor(Port.B)
rotation_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12,36])

# Sensor definitions
color_sensor = ColorSensor(Port.S2)
rotation_sensor = TouchSensor(Port.S1)

# Custom variables
screen_xy = [50, 50]
start_configuration_speech = "Input color drop off zones"
turnSpeed = 50
claw_grip_speed = 50
elbow_angle = -180
base_rot_speed = 50
drop_off_zones = {}
drop_off_colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]
manual_input = False

def manual_reset():
    rotation_motor.run_angle(turnSpeed, 0, then=Stop.COAST, wait=True)
    Elbow_motor.run_angle(turnSpeed, 0, then=Stop.COAST, wait=True)
    claw_motor.run_angle(claw_grip_speed, 0, then=Stop.COAST, wait=True)
    flag = False

    while ev3.buttons.pressed() == [Button.DOWN] and not flag:
        print("Reseted")
        rotation_motor.reset_angle(0)
        Elbow_motor.reset_angle(0)
        claw_motor.reset_angle(0)
        if ev3.buttons.pressed() == [Button.DOWN, Button.UP]:
            rotation_motor.run_angle(turnSpeed, 0, then=Stop.HOLD, wait=True)
            Elbow_motor.run_angle(turnSpeed, 0, then=Stop.HOLD, wait=True)
            claw_motor.run_angle(claw_grip_speed, 0, then=Stop.HOLD, wait=True)
            flag = True

def update_settings(base_angle, arm_angle, claw_angle, drop_off_zones):
    file = open("settings.json", "w")
    json.dump({"base_angle": base_angle, 
               "arm_angle": arm_angle, 
               "claw_angle": claw_angle, 
               "drop_off_zones": drop_off_zones}, 
               file)
    file.close()

def read_settings():
    with open("settings.json", "r") as file:
        settings = json.load(file)
    return settings

def update_program_settings(settings):
    rotation_motor.reset_angle(int(settings["base_angle"]))
    Elbow_motor.reset_angle(int(settings["arm_angle"]))
    claw_motor.reset_angle(int(settings["claw_angle"]))
    drop_off_zones = settings["drop_off_zones"]
    print(drop_off_zones)
    drop_off_zones_temp = {}
    for x, y in zip(drop_off_zones.keys(), drop_off_colors):
            drop_off_zones_temp.update({y: drop_off_zones[x]})

    drop_off_zones = drop_off_zones_temp
    return drop_off_zones

def reset_robot_by_settings():
    print("Resetting robot by settings")
    rotation_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
    Elbow_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
    claw_motor.run_target(claw_grip_speed, 0, then=Stop.HOLD, wait=True)
    print("Done resetting robot by settings")


def reset_robot():
    if not rotation_sensor.pressed():
        print("Resetting robot")

        rotation_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
        #rotation_motor.run_until_stalled(-50, then=Stop.COAST, duty_limit=25)
        print("rotation done")

        Elbow_motor.run_target(turnSpeed, -180, then=Stop.HOLD, wait=True)
        print("elbow done")
        
        print("start angle: " + str(claw_motor.angle()))
        claw_motor.run_target(claw_grip_speed, 0, then=Stop.HOLD, wait=True)
        print("claw done")

    print("Done resetting robot.")

def robot_to_start():
    if not rotation_sensor.pressed():
        print("Robot going to start.")
        rotation_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
        #rotation_motor.run_until_stalled(-50, then=Stop.COAST, duty_limit=25)
        print("Robot back to start.")
    
def claw_grab(speed):
    #claw_motor.track_target(80)
    return claw_motor.run_until_stalled(speed, then=Stop.HOLD)

def claw_release(speed, angle):
    claw_motor.run_target(speed, 0, then=Stop.COAST, wait=True)

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

    # rotation_motor.track_target(angle)
    rotation_motor.run_angle(speed, angle, then=Stop.HOLD, wait=True)

if __name__ == '__main__':

    while not ev3.buttons.pressed() == [Button.DOWN]:
        if ev3.buttons.pressed() == [Button.DOWN]:
            manual_reset()

    base_angle = rotation_motor.angle()
    arm_angle = Elbow_motor.angle()
    claw_angle = claw_motor.angle()
    drop_off_zones = {"Color.RED": 180, "Color.GREEN": 180, "Color.BLUE": 180, "Color.YELLOW": 180}
    update_settings(base_angle, arm_angle, claw_angle, drop_off_zones)

    drop_off_zones = update_program_settings(read_settings())

    if drop_off_zones == {}: 
        manual_input = True
    else:
        manual_input = False

    print("Starting robot")

    ev3.speaker.set_speech_options(language='en-sc', voice=None, speed=None, pitch=None)

    # reset_robot()
    reset_robot_by_settings()

    ev3.speaker.say(start_configuration_speech)
    ev3.screen.draw_text(screen_xy[0], screen_xy[1], start_configuration_speech, text_color=Color.BLACK, background_color=None)
    
    if manual_input:
        
        # Set drop off zones for each color in drop_off_colors RED, GREEN, BLUE, YELLOW
        index = 0
        lastIndex = -1
        while len(drop_off_zones) < len(drop_off_colors):
            if (index != lastIndex):
                lastIndex = index
                ev3.screen.clear()
                ev3.speaker.say("Input destination for " + str(drop_off_colors[index]).replace("Color.", ''))
                ev3.screen.draw_text(screen_xy[0], screen_xy[1], "Input destination for color: " + str(drop_off_colors[index]).replace("Color.", ''), text_color=Color.BLACK, background_color=None)
            if ev3.buttons.pressed() == [Button.CENTER]:
                print(ev3.buttons.pressed())
                drop_off_zones.update({drop_off_colors[index] : rotation_motor.angle()})
                index += 1

            elif ev3.buttons.pressed() == [Button.RIGHT]:
                print(ev3.buttons.pressed())
                rotation_motor.run(turnSpeed)

            elif ev3.buttons.pressed() == [Button.LEFT]:
                print(ev3.buttons.pressed())
                rotation_motor.run(-turnSpeed)

            else:
                rotation_motor.stop()
    
    print("Done setting settings")
    robot_to_start()

    print(drop_off_zones)

    for i in range(len(drop_off_colors)):
        #claw_release(claw_grip_speed, grip_Angle)
        lift_down(turnSpeed, elbow_angle + 10)
        print("Lifting down")
        wait(1000)

        print("Getting grip angle and grabbing")
        grip_Angle = claw_grab(claw_grip_speed)
        wait(1000)

        print("Lifting up")
        lift_up(turnSpeed, elbow_angle - 10)
        wait(1000)
        
        print("GRIP ANG" + str(grip_Angle))

        current_color = detect_color()
        print(current_color)
        
        color_test = [i for i in drop_off_colors if i == current_color] 
        while len(color_test) == 0:
            print("No color detected")
            #claw_motor.run_until_stalled(claw_grip_speed, then=Stop.HOLD, duty_limit=90)

            print("Releasing claw")
            claw_release(claw_grip_speed, grip_Angle)
            
            print("Lifting down")
            lift_down(turnSpeed, elbow_angle)
            
            print("Getting grip angle and grabbing")
            grip_Angle = claw_grab(claw_grip_speed)

            print("Lifting up")
            lift_up(turnSpeed, elbow_angle)
            
            current_color = detect_color()
            print(current_color)

            color_test = [i for i in drop_off_colors if i == current_color]             
            
        print("Rotating to drop off zone")
        rotate_base(base_rot_speed, drop_off_zones[current_color])

        wait(1000)

        print("Lifting down 2")
        lift_down(turnSpeed, elbow_angle)

        print("Releasing claw 2")
        claw_release(claw_grip_speed, grip_Angle)

        print("Lifting up 2")
        lift_up(turnSpeed, elbow_angle)

        print("Rotating to start")
        rotate_base(base_rot_speed, -drop_off_zones[current_color])
        wait(5000)
    
    reset_robot()