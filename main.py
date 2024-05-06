#!/usr/bin/env pybricks-micropython

import json
import threading
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
from pybricks import messaging 

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
drop_off_colors = ["pickup", Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]
manual_input = False
interval_per_click = 0.5

zone_storage = {}
for i in drop_off_colors:
    zone_storage.update({i: 0})

"""
OBSOLETE
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
"""

def update_settings(base_angle, arm_angle, claw_angle, drop_off_zones):

    drop_off_zones_temp = {}
    for x, y in zip(drop_off_zones.keys(), drop_off_colors):
            y = str(y)
            y.replace("Color.", '')
            drop_off_zones_temp.update({y: drop_off_zones[x]})
    drop_off_zones = drop_off_zones_temp

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

"""
OBSOLETE

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

"""

def robot_to_start():
    if not rotation_sensor.pressed():
        print("Robot going to start.")
        rotation_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
        #rotation_motor.run_until_stalled(-50, then=Stop.COAST, duty_limit=25)
        print("Robot back to start.")
    
def claw_grab(speed):
    #claw_motor.track_target(80)
    return claw_motor.run_until_stalled(speed, then=Stop.HOLD, duty_limit=60)

def claw_release(speed, angle):
    claw_motor.run_target(speed, 0, then=Stop.COAST, wait=True)

def lift_up(speed, angle, height):
    Elbow_motor.run_angle(speed, -(angle) + height, then=Stop.HOLD, wait=True)
    print("lift up height " + str(angle - height))

def lift_down(speed, angle, height):
    Elbow_motor.run_angle(speed, angle - height, then=Stop.HOLD, wait=True)
    print("lift down height " + str(-(angle) + height))

def detect_color():
    return color_sensor.color()

def rotate_base(speed, angle):
    if angle < 0:
        angle -= 10
    else:
        angle += 10

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

def start_sort(interval):
    drop_off_zones = update_program_settings(read_settings())
    overflow = False

    wait(interval)
    
    current_height = drop_off_zones["pickup"][1]
    
    # Reset to pick up location
    lift_up(turnSpeed, current_height, 0)
    rotate_base(base_rot_speed, drop_off_zones["pickup"][0])

    grip_Angle = claw_grab(claw_grip_speed)

    lift_up(turnSpeed, drop_off_zones["pickup"][1], current_height)
        
    print("GRIP ANG = " + str(grip_Angle))

    wait(500)
    current_color = detect_color()
    print(current_color)

    for i in zone_storage:
        if zone_storage[i] >= 3 and i == current_color:
            overflow = True
    
    color_test = [i for i in drop_off_colors if i == current_color]
    while len(color_test) == 0 or overflow == True:
        print("No color detected")
        #claw_motor.run_until_stalled(claw_grip_speed, then=Stop.HOLD, duty_limit=90)

        print("Elbow angle : " + str(elbow_angle))
        print("Current Height : " + str(current_height))

        #print("Releasing claw")
        claw_release(claw_grip_speed, grip_Angle)

        #print("Lifting down")
        lift_down(turnSpeed, current_height, 0)

        #print("Getting grip angle and grabbing")
        grip_Angle = claw_grab(claw_grip_speed)

        lift_up(turnSpeed, current_height, 0)
            
        current_color = detect_color()
        print(current_color)

        for i in zone_storage:
            if zone_storage[i] < 3 and i == current_color:
                overflow = False

        color_test = [i for i in drop_off_colors if i == current_color]

    current_height = zone_storage[current_color] * 110
    zone_storage[current_color] += 1
    print("Zone storage: " + str(zone_storage))
    print("current height: " + str(current_height))

    #print("Rotating to drop off zone")
    rotate_base(base_rot_speed, drop_off_zones[current_color][0])

    #print("Lifting down 2")
    lift_down(turnSpeed, drop_off_zones[current_color][1] + current_height, zone_storage[current_color]) # recently only current_height

    #print("Releasing claw 2")
    claw_release(claw_grip_speed, grip_Angle)

    #print("Lifting up 2")
    lift_up(turnSpeed, drop_off_zones[current_color][1] + current_height, + zone_storage[current_color]) # recently only current_height

    #print("Rotating to start")
    rotate_base(base_rot_speed, -drop_off_zones[current_color][0])

    #print("Lifting down 2")
    lift_down(turnSpeed, current_height, 0)
    start_sort(interval)

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

def pause(main):
    while len(ev3.buttons.pressed) == 0 and ev3.buttons.pressed != [Button.CENTER]:
        continue
    while len(ev3.buttons.pressed) == 0 and ev3.buttons.pressed != [Button.CENTER]:
        main.wait(1)

    main.notify()

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
            drop_off_zones.update({drop_off_colors[index] : [rotation_motor.angle(), Elbow_motor.angle()]})
            index += 1

        elif ev3.buttons.pressed() == [Button.RIGHT]:
            print(ev3.buttons.pressed())
            rotation_motor.run(-turnSpeed)

        elif ev3.buttons.pressed() == [Button.LEFT]:
            print(ev3.buttons.pressed())
            rotation_motor.run(turnSpeed)
        
        elif ev3.buttons.pressed() == [Button.UP]:
            print(ev3.buttons.pressed())
            Elbow_motor.run(-turnSpeed/4)

        elif ev3.buttons.pressed() == [Button.DOWN]:
            print(ev3.buttons.pressed())
            Elbow_motor.run(turnSpeed/4)

        else:
            rotation_motor.stop()
            Elbow_motor.stop()
    
    Elbow_motor.track_target(drop_off_zones["pickup"][1])
    rotation_motor.track_target(start_angle)
    #rotate_base(base_rot_speed, start_angle) # start_angle should be start, i.e. 0

    drop_off_zones_temp = {}
    for x, y in zip(drop_off_zones, drop_off_colors):
        y = str(y)
        y.replace("Color.", '')
        drop_off_zones_temp.update({y: drop_off_zones[x]})

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

    # ??? varför
    lift_down(turnSpeed, -elbow_angle, 0)
    lift_up(turnSpeed, elbow_angle, 0)

    print("Rotating to drop off zone")
    rotate_base(base_rot_speed, drop_off_zones[checking_location][0])


    impact_angle = Elbow_motor.run_until_stalled(turnSpeed, then=Stop.COAST, duty_limit=10)
    print("Impact angle = " + str(impact_angle))
    if impact_angle < 40:
        print("Detected")
        ev3.speaker.say("DETECTED")
    else:
        ev3.speaker.say("NOT DETECTED")

    print("Lifting up 2")
    lift_up(turnSpeed, elbow_angle, 0)

    print("Rotating to start")
    rotate_base(base_rot_speed, -drop_off_zones[checking_location][0])
    
    main_menu()

def conveyor_sort():
    drop_off_zones = update_program_settings(read_settings())
    
    overflow = False
    
    current_height = drop_off_zones["pickup"][1]
    storage_height = 0
    current_color = None

    while current_color not in drop_off_colors:
        current_color = detect_color()

    print(current_color)
    
    wait(900)

    # overwrite current color when brick is closer to get a more acurate reading 
    while current_color not in drop_off_colors:
        current_color = detect_color()
        print(current_color)

    print(current_color)

    lift_down(turnSpeed, drop_off_zones["pickup"][1], 0)
    
    grip_Angle = claw_grab(claw_grip_speed)

    lift_up(turnSpeed, current_height, 0)
    
    for i in zone_storage:
        if zone_storage[i] >= 3 and i == current_color:
            overflow = True

    if overflow == False:
        storage_height = zone_storage[current_color] * 70
        zone_storage[current_color] += 1
        print("Zone storage: " + str(zone_storage))
        print("current height: " + str(current_height))

        rotate_base(base_rot_speed, drop_off_zones[current_color][0])

        lift_down(turnSpeed, drop_off_zones[current_color][1] + current_height, storage_height)

        claw_release(claw_grip_speed, grip_Angle)

        lift_up(turnSpeed, drop_off_zones[current_color][1] + current_height, storage_height)

        rotate_base(base_rot_speed, -drop_off_zones[current_color][0])
    else:
        claw_release(turnSpeed, grip_Angle)
        lift_up(turnSpeed, current_height, 0)
        lift_down(turnSpeed, current_height, 0)


    conveyor_sort()

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
            set_manual_locations()
            break
        elif ev3.buttons.pressed() == [Button.RIGHT]:
            pause.start()
            start_sort(sort_interval)
            break
        elif ev3.buttons.pressed() == [Button.LEFT]:
            check_locations()
            break
        elif ev3.buttons.pressed() == [Button.DOWN]:
            sort_interval = set_sort_interval()
            break
        elif ev3.buttons.pressed() == [Button.CENTER]:
            pause.start()
            conveyor_sort()
            break
        else:
            pass
        wait(250)

main = threading.Thread(target=main_menu)
pause = threading.Thread(target=pause, args=main)

def create_server():
    server = messaging.BluetoothMailboxServer()
    mbox = messaging.TextMailbox("greeting", server)

    # The server must be started before the client!
    print("waiting for connection...")
    server.wait_for_connection()
    print("connected!")

    # In this program, the server waits for the client to send the first message
    # and then sends a reply.
    mbox.wait()
    print(mbox.read())
    mbox.send("hello to you!")
    

if __name__ == '__main__':
    create_server()
    #main.start()
