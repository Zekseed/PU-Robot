## Introduction

In this project we have developed a program for the LEGO® MINDSTORMS EV3 programmable hub Brick using MicroPython and pybricks.
# Reference picture to the hub used:
<picture>
  <img alt="Shows an illustrated lego programmable hub." src="https://pybricks.com/ev3-micropython/_images/ev3brick.png">
</picture>

In this project we are using robot arm H25. refrence picture:
<picture>
  <img alt="Shows an illustrated lego programmable hub." src="https://pybricks.com/ev3-micropython/_images/robot_arm.jpg">
</picture>

This is project is a sorting robot, capable of sorting different colors and putting them in a designated position.
the amount of colors is orginally based on 4 color (Red, Green, Blue and yellow) but the amount of colors can be changed in the code. The color sensor can detect the colors previously mentioned but also black, white, brown, orange and purple.

The robot have 5 functions each called upon by the hubs buttons when starting the program.

- when set manual location gets the colors from the a list in the code and with the manual input from the hubs buttons you control the robot arms rotation and set the designated drop off zones for each color.

- The sort objects function sorts the objects by moving them to the drop off zones based on the color detected.

- The conveyor sort function when the objects reach the color sensor the arm goes to down and picks up the object and moves it the the drop off zones based on the color detected.

- The check location function checks if an item is present at a drop of zone by pressing the claw down at the location. If there is resistance, it will return "DETECTED" and if not, it will return "NOT DETECTED".

- The set interval function sets the interval at which the sorting function will wait before starting. The default interval is 1 second and can be increased or decreased by one minute based on user input.

## Getting started

Requirements for development is
- Having pybricks installed
For testing you require: 
- A robot capable of running pybricks and some colored objects, optionally a conveyor belt.

What the robot needs:
- A hub
- A motorized arm with a claw, that is connected to port A
- A color sensor connected to port S2
- A rotation motor connected to port B
- A rotation sensor connected to port S1

building instructions can be found here: https://education.lego.com/en-us/product-resources/mindstorms-ev3/downloads/building-instructions/#building-core but modified with an color sensor by the under the lifting mechanism


## Building and running

This is where you explain how to make the project run. What is your startup procedure? Does the program accept different arguments to do different things?

You should also describe how to operate your program. Does it need manual input before it starts picking up and sorting the items?

In order for the program to work, the option "manual setup" needs to be chosen on the screen of the robot and filled out before doing anything else and the robot claw need to be very close to the ground (preferably touches the ground) or else the robot will not work properly
In order to use the robot's various functions, you need to select them on the robot screen using the arrown on the robot.

here are a few manual inputs neccesary to run the functions.

- when set manual location the robot is controlled by the hubs buttons then with the hubs center button the location of the color drop off is confirmed.

- The sort objects function need to have a block placed on the pickup zone. pickup zone is always where the robot starts when booted.

- The conveyor sort function needs to have the conveyor periodically fed the colored objects. 

- The check location needs input by the hubs buttons to see which color location to check.

- The set interval needs input by the hubs buttons, up and down changes the interval per sort by increments of one minute

## Features
- [x] US01: As a customer, I want the robot to pick up items
- [x] US02: As a customer, I want the robot to drop off items 
- [x] US03: As a customer, I want the robot to be able to determine if an item is present at a given location
- [x] US04: As a customer, I want the robot to tell me the colour of an item
- [x] US05: As a customer, I want the robot to drop items off at different locations based on the colour of the item
- [x] US06: As a customer, I want the robot to be able to pick up items from elevated positions (Change to set elevated location)
- [x] US07: As a customer, I want to be able to calibrate maximum of three different colours and assign them to specific drop-off zones
- [x] US09: As a customer, I want the robot to check the pickup location periodically to see if a new item has arrived
- [x] US10: As a customer, I want the robots to sort items at a specific time
- [ ] US11: As a customer, I want two robots (from two teams) to communicate and work together on items sorting without colliding with each other
- [ ] US12: As a customer, I want to be able to manually set the locations and heights of one pick-up zone and two drop-off zones
- [x] US13: As a customer, I want to easily reprogram the pickup and drop off zone of the robot
- [ ] US14: As a customer, I want to easily change the schedule of the robot pick up task
- [ ] US15: As a customer, I want to have an emergency stop button, that immediately terminates the operation of the robot safely
- [x] US16: As a customer, I want the robot to be able to pick an item up and put it in the designated drop-off location within 5 seconds
- [x] US17: As a customer, I want the robot to pick up items from a rolling belt and put them in the designated positions based on color and shape (color sensor)
- [ ] US18: As a customer, I want to have a pause button that pauses the robot's operation when the button is pushed and then resumes the program from the same point when I push the button again
- [ ] US19: As a customer, I want a very nice dashboard to configure the robot program and start some tasks on demand
