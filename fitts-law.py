import numpy as np
import pandas as pd
import pyglet
from pointing_input import HandDetector
from pyglet.window import mouse
import itertools
import random
import math
import time
import sys
import os

participant_id = -1
input_device_condition = "no_condition"
num_trials_per_condition = 20
latency_s = 0

# usage: python fitts-law.py [PARTICIPANT ID] [INPUT DEVICE CONDITION] [NUMBER OF TRIALS PER TARGET CONDITION] [LATENCY IN SECONDS]
if len(sys.argv) >= 4:
    participant_id = sys.argv[1]
    input_device_condition = sys.argv[2]
    num_trials_per_condition = int(sys.argv[3])
    if len(sys.argv) >= 5:
        latency_s = float(sys.argv[4])


#circle point calculation was done with chatGPT
def point_on_circle(cx,cy,radius,angle_deg):
    angle_rad = np.radians(angle_deg)
    x = cx + radius * np.cos(angle_rad)
    y = cy + radius * np.sin(angle_rad)
    return x, y

#setup pyglet window
WINDOW_WIDTH = 1220
WINDOW_HEIGHT = 760
CURSOR_FNAME = "cursor.png"
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# a very hacky way of hiding the cursor. Loads a fully transparent image as the cursor.
cursor_image = pyglet.image.load(CURSOR_FNAME)
dummy_cursor = pyglet.window.ImageMouseCursor(cursor_image)
window.set_mouse_cursor(dummy_cursor)

color_inactive=(210,210,210,255)
color_active=(255,247,5,255)
cursor = pyglet.shapes.Circle(-10,-10,10,color=(210,204,0,100))
target = pyglet.shapes.Circle(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,100,color=(100,100,100,255))


#Setting Up the conditions
distances = [100,200,300]
sizes = [30,40,50]
conditions = list(itertools.product(distances, sizes))
conditions = random.sample(conditions, len(conditions))
distance_con = None
size_con = None
target_number = 11
target_index = num_trials_per_condition
pressing = False
angle = 360 / target_number

current_trial = None
current_ts = None
trials = []

output_dir = "results"

def get_distance(x1,y1,x2,y2):
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def get_next_target():
    global distance_con
    global size_con
    global target_index
    global conditions

    global current_trial
    global current_ts
    global trials

    print(target_index)
    #if distance_con and size_con:
        #normal state
    # start new trial
    if current_trial:
        trials.append(current_trial)
    current_trial = {}

    if target_index == num_trials_per_condition:
        #check if there are conditions left.                
        if conditions:
            #get new conditions
            con = conditions.pop(0)
            distance_con = con[0]
            size_con = con[1]
            target_index = 1

            pass
        else:
            #end of the test for this input device
            print("end test")

            trials_df = pd.DataFrame(trials, columns=trials[0].keys())
            print(trials_df)
            output_fpath = os.path.join(output_dir, f"{participant_id}-{input_device_condition}.csv")
            trials_df.to_csv(output_fpath)
            return
            pass
    else:
        target_index += 1    
        pass
    
    #there is only one target that gets relocated after each click  
    circle_index = (target_index * int(math.floor(target_number * 0.5))) % target_number
    x,y = point_on_circle(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,distance_con,angle*circle_index)
    target.x = x
    target.y=y
    target.radius=size_con

    # instantiate values of new trial
    current_trial["distance"] = distance_con
    current_trial["size"] = size_con


def update_cursor_position(x,y):
    global cursor
    cursor.x = x
    cursor.y = y
    
    
@window.event
def on_draw():
    window.clear()
    target.draw()
    cursor.draw()
    pass

@window.event
def on_mouse_motion(x, y, dx, dy):
    if latency_s > 0:
        pyglet.clock.schedule_once(lambda dt: update_cursor_position(x,y), latency_s)
    else:
        update_cursor_position(x,y)


    
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        if latency_s > 0:
            pyglet.clock.schedule_once(lambda dt: press_interaction(x,y), latency_s)
        else:
            #Start Recording
            press_interaction(x, y)

@window.event
def on_mouse_release(x,y, button, modifiers):
    if button == mouse.LEFT:
        if latency_s > 0:
            pyglet.clock.schedule_once(lambda dt:release_interaction(x,y), latency_s)
        else:
            release_interaction(x,y)
        

def release_interaction(x,y):
    cursor.color = color_inactive

#gather input from all input devices here
def press_interaction(x,y):
    global current_trial
    global current_ts
    global cursor
    d = get_distance(x,y,target.x,target.y)
    success = d < cursor.radius + target.radius
    if current_trial:
        if current_ts == None:
            current_trial["valid"] = False
            current_trial["time"] = np.NaN
        else:
            duration = time.time() - current_ts
            current_trial["valid"] = True

            current_trial["time"] = duration

        current_trial["success"] = True
    if success:
        #the target was hit.
        #print("Hit")
        current_ts = time.time()
    else:
        #the target was not hit.
        #print("Miss")
        current_ts = None # this means that every trial where the previous circle was not hit is invalid. Should it be like that?
        pass

    #print(current_trial)
    
    cursor.color = color_active

    #check if Target was clicked.
    #if target
    #go to next target.
    get_next_target()
    pass

#pyglet.clock.schedule_interval(update, 1/120) 
pyglet.app.run()




#The circle should always be on the other side of the last one.
#timing between circle interaction
#logging results
#Possebility for lagging input