#!/usr/bin/env pybricks-micropython

import json
#import asyncio
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
from pybricks.media.ev3dev import SoundFile, ImageFile, Font

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
turnSpeed = 300
claw_grip_speed = 200
elbow_angle = -230
base_rot_speed = 200
drop_off_zones = {}
drop_off_colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]
manual_input = False
interval_per_click = 0.5

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
    return claw_motor.run_until_stalled(speed, then=Stop.HOLD, duty_limit=80)

def claw_release(speed, angle):
    claw_motor.run_target(speed, 0, then=Stop.COAST, wait=True)

def lift_up(speed, angle):
    Elbow_motor.run_target(speed, angle, then=Stop.HOLD, wait=True)

def lift_down(speed):
    return Elbow_motor.run_until_stalled(speed, then=Stop.COAST, duty_limit=10)

def detect_color():
    return color_sensor.color()

def rotate_base(speed, angle):
    if angle < 0:
        angle -= 10
    else:
        angle += 10

    # rotation_motor.track_target(angle)
    rotation_motor.run_angle(speed, angle, then=Stop.HOLD, wait=True)

def set_sort_interval():
    interval = 1000
    while not ev3.buttons.pressed() == [Button.CENTER]:
        if ev3.buttons.pressed() == [Button.DOWN]:
            # 60000 = 1 minute
            if interval >= (60000 * interval_per_click):
                interval -= 60000 * interval_per_click
                ev3.screen.clear()
                ev3.screen.draw_text(screen_xy[0], screen_xy[1], str(interval//60000) + "minutes", text_color=Color.BLACK, background_color=None)
        elif ev3.buttons.pressed() == [Button.UP]:
            interval += 60000 * interval_per_click
            ev3.screen.clear()
            ev3.screen.draw_text(screen_xy[0], screen_xy[1], str(interval//60000) + "minutes", text_color=Color.BLACK, background_color=None)
        wait(250)
    return interval


def _main_loop(interval):
    wait(interval)
    
    ground_angle = abs(lift_down(turnSpeed))
    print("ground angle = " + str(ground_angle))
    #print("Lifting down")

    #print("Getting grip angle and grabbing")
    grip_Angle = claw_grab(claw_grip_speed)

    #print("Lifting up")
    lift_up(turnSpeed, elbow_angle + ground_angle)
    print("Calculated elbow angle = " + str(elbow_angle + ground_angle))
        
    print("GRIP ANG = " + str(grip_Angle))

    wait(500)
    current_color = detect_color()
    print(current_color)
        
    color_test = [i for i in drop_off_colors if i == current_color]
    while len(color_test) == 0:
        print("No color detected")
        #claw_motor.run_until_stalled(claw_grip_speed, then=Stop.HOLD, duty_limit=90)

        #print("Releasing claw")
        claw_release(claw_grip_speed, grip_Angle)
            
        #print("Lifting down")
        lift_down(turnSpeed)
            
        #print("Getting grip angle and grabbing")
        grip_Angle = claw_grab(claw_grip_speed)

        #print("Lifting up")
        lift_up(turnSpeed, elbow_angle + ground_angle)
            
        current_color = detect_color()
        print(current_color)

        color_test = [i for i in drop_off_colors if i == current_color]             
            
    #print("Rotating to drop off zone")
    rotate_base(base_rot_speed, drop_off_zones[current_color])

    #print("Lifting down 2")
    lift_down(turnSpeed)

    #print("Releasing claw 2")
    claw_release(claw_grip_speed, grip_Angle)

    #print("Lifting up 2")
    lift_up(turnSpeed, elbow_angle)

    #print("Rotating to start")
    rotate_base(base_rot_speed, -drop_off_zones[current_color])
    _main_loop(interval)

""" 
from multiprocessing import Process 

def emergency_stop():
    while True:
        if ev3.buttons.pressed() == [Button.CENTER]:
            rotation_motor.stop()
            Elbow_motor.stop()
            claw_motor.stop()

            rotation_motor.run_target(turnSpeed, 0, then=Stop.COAST, wait=True)
            Elbow_motor.run_target(turnSpeed, 0, then=Stop.COAST, wait=True)
            claw_motor.run_target(claw_grip_speed, 0, then=Stop.COAST, wait=True)
            break

"""


def set_manual_locations():
    start_angle = rotation_motor.angle()
    drop_off_zones = {}
    ev3.speaker.say(start_configuration_speech)
    ev3.screen.clear()
    ev3.screen.draw_text(screen_xy[0], screen_xy[1], start_configuration_speech, text_color=Color.BLACK, background_color=None)
    
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
    
    rotate_base(base_rot_speed, start_angle)
    update_settings(rotation_motor.angle(), Elbow_motor.angle(), claw_motor.angle(), drop_off_zones)
    main_menu()

def check_locations():
    ev3.screen.clear()
    ev3.screen.set_font(Font('Lucida', 20))
    ev3.screen.draw_text(0, 0, "Red", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0, 100, "Yellow", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0, 50, "Blue", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(70, 50, "Green", text_color=Color.BLACK, background_color=None)
    
    while len(ev3.buttons.pressed()) != 2:
        print(ev3.buttons.pressed())
        if ev3.buttons.pressed() == [Button.UP]:
            checking_location = Color.RED
            break
        elif ev3.buttons.pressed() == [Button.RIGHT]:
            checking_location = Color.GREEN
            break
        elif ev3.buttons.pressed() == [Button.LEFT]:
            checking_location = Color.BLUE
            break
        elif ev3.buttons.pressed() == [Button.DOWN]:
            checking_location = Color.YELLOW
            break
        elif ev3.buttons.pressed() == [Button.CENTER]:
            main_menu()
            break
        else:
            pass
        wait(250)

    lift_down(turnSpeed)
    lift_up(turnSpeed, elbow_angle)

    print("Rotating to drop off zone")
    rotate_base(base_rot_speed, drop_off_zones[checking_location])


    print("Lifting down 2")
    impact_angle = lift_down(turnSpeed)
    print("Impact angle = " + str(impact_angle))
    if impact_angle < 40:
        print("Detected")
        ev3.speaker.say("DETECTED")
    else:
        ev3.speaker.say("NOT DETECTED")

    print("Lifting up 2")
    lift_up(turnSpeed, elbow_angle)

    print("Rotating to start")
    rotate_base(base_rot_speed, -drop_off_zones[checking_location])
    
    main_menu()

def main_menu():
    ev3.screen.clear()
    ev3.screen.set_font(Font('Lucida', 12))
    ev3.screen.draw_text(0, 0, "Set manual locations", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0, 100, "Set sort interval", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0, 50, "Check location", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(100, 50, "Start sort", text_color=Color.BLACK, background_color=None)

    sort_interval = 1000

    while len(ev3.buttons.pressed()) != 2:
        print(ev3.buttons.pressed())
        if ev3.buttons.pressed() == [Button.UP]:
            #set_manual_locations()
            break
        elif ev3.buttons.pressed() == [Button.RIGHT]:
            _main_loop(sort_interval)
            break
        elif ev3.buttons.pressed() == [Button.LEFT]:
            check_locations()
            break
        elif ev3.buttons.pressed() == [Button.DOWN]:
            sort_interval = set_sort_interval()
            break
        else:
            pass
        wait(250)

if __name__ == '__main__':
    
    drop_off_zones = update_program_settings(read_settings())
    reset_robot_by_settings()
    main_menu()

    #while not ev3.buttons.pressed() == [Button.DOWN]:
    #    if ev3.buttons.pressed() == [Button.DOWN]:
    #        manual_reset()

    # base_angle = rotation_motor.angle()
    # arm_angle = Elbow_motor.angle()
    # claw_angle = claw_motor.angle()
    # drop_off_zones = {"Color.RED": 90, "Color.GREEN": 180, "Color.BLUE": 225, "Color.YELLOW": 180}
    # update_settings(base_angle, arm_angle, claw_angle, drop_off_zones)


    # print("Starting robot")

    # ev3.speaker.set_speech_options(language='en-sc', voice=None, speed=None, pitch=None)

    # # reset_robot()
    
    # interval = set_sort_interval()

    # print("Done setting settings")
    # robot_to_start()

    # """
    #     asyncio.run(emergency_stop())
        
    # """

    # _main_loop(interval)
    # print(drop_off_zones)
    
    # reset_robot()
