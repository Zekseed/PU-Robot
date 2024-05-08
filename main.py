#!/usr/bin/env pybricks-micropython

import json
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

zone_storage = {}
for i in drop_off_colors:
    zone_storage.update({i: 0})

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

def robot_to_start():
    if not rotation_sensor.pressed():
        print("Robot going to start.")
        rotation_motor.run_target(turnSpeed, 0, then=Stop.HOLD, wait=True)
        print("Robot back to start.")
    
def claw_grab(speed):
    return claw_motor.run_until_stalled(speed, then=Stop.HOLD, duty_limit=60)

def claw_release(speed, angle):
    claw_motor.run_target(speed, 0, then=Stop.COAST, wait=True)

def lift_up(speed, angle, height):
    Elbow_motor.run_angle(speed, angle + height, then=Stop.HOLD, wait=True)

def lift_down(speed, angle, height):
    Elbow_motor.run_angle(speed, angle - height, then=Stop.COAST, wait=True)

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
    
    current_height = 0

    grip_Angle = claw_grab(claw_grip_speed)

    lift_up(turnSpeed, elbow_angle, 0)
        
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

        print("Elbow angle : " + str(elbow_angle))
        print("Current Height : " + str(current_height))

        claw_release(claw_grip_speed, grip_Angle)

        lift_down(turnSpeed, -elbow_angle, 0)

        grip_Angle = claw_grab(claw_grip_speed)

        lift_up(turnSpeed, elbow_angle, 0)
            
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

    rotate_base(base_rot_speed, drop_off_zones[current_color])

    lift_down(turnSpeed, -elbow_angle, current_height)

    claw_release(claw_grip_speed, grip_Angle)

    lift_up(turnSpeed, elbow_angle, current_height)

    rotate_base(base_rot_speed, -drop_off_zones[current_color])

    lift_down(turnSpeed, -elbow_angle, 0)
    start_sort(interval)

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
    
    rotation_motor.track_target(start_angle)

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

    lift_down(turnSpeed, -elbow_angle, 0)
    lift_up(turnSpeed, elbow_angle, 0)

    print("Rotating to drop off zone")
    rotate_base(base_rot_speed, drop_off_zones[checking_location])


    impact_angle = Elbow_motor.run_until_stalled(turnSpeed, then=Stop.COAST, duty_limit=10)
    print("Impact angle = " + str(impact_angle))
    if impact_angle < 40:
        print("Detected")
        ev3.speaker.say("DETECTED")
    else:
        ev3.speaker.say("NOT DETECTED")

    lift_up(turnSpeed, elbow_angle, 0)

    rotate_base(base_rot_speed, -drop_off_zones[checking_location])
    
    main_menu()

def conveyor_sort():
    drop_off_zones = update_program_settings(read_settings())
    
    current_height = -120
    storage_height = 0
    current_color = None

    while current_color not in drop_off_colors:
        current_color = detect_color()

    print(current_color)
    
    wait(900)
    
    while current_color not in drop_off_colors:
        current_color = detect_color()

    print(current_color)

    lift_down(turnSpeed, 0, current_height)
    
    grip_Angle = claw_grab(claw_grip_speed)

    lift_up(turnSpeed, 0, current_height)
    
    for i in zone_storage:
        if zone_storage[i] >= 3 and i == current_color:
            overflow = True

    if overflow == False:
        storage_height = zone_storage[current_color] * 110
        zone_storage[current_color] += 1
        print("Zone storage: " + str(zone_storage))
        print("current height: " + str(current_height))

        rotate_base(base_rot_speed, drop_off_zones[current_color])

        lift_down(turnSpeed, -elbow_angle, current_height + storage_height) # TODO

        claw_release(claw_grip_speed, grip_Angle)

        lift_up(turnSpeed, elbow_angle, current_height + storage_height)

        rotate_base(base_rot_speed, -drop_off_zones[current_color])
    else:
        claw_release(turnSpeed, grip_Angle)
        lift_up(turnSpeed, elbow_angle, current_height+storage_height)
        lift_down(turnSpeed, -elbow_angle, current_height+storage_height)
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
            start_sort(sort_interval)
            break
        elif ev3.buttons.pressed() == [Button.LEFT]:
            check_locations()
            break
        elif ev3.buttons.pressed() == [Button.DOWN]:
            sort_interval = set_sort_interval()
            break
        elif ev3.buttons.pressed() == [Button.CENTER]:
            conveyor_sort()
            break
        else:
            pass
        wait(250)

if __name__ == '__main__':
    main_menu()

