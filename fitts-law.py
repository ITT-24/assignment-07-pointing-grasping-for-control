import numpy as np
import pyglet
from pointing_input import HandDetector
from pyglet.window import mouse
import itertools
import random

#circle point calculation was done with chatGPT
def point_on_circle(cx,cy,radius,angle_deg):
    angle_rad = np.radians(angle_deg)
    x = cx + radius * np.cos(angle_rad)
    y = cy + radius * np.sin(angle_rad)
    return x, y

#setup pyglet window
WINDOW_WIDTH = 1220
WINDOW_HEIGHT = 760
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
color_inactive=(210,204,0,255)
color_active=(255,247,5,255)
cursor = pyglet.shapes.Circle(-10,-10,10,color=(210,204,0,100))
target = pyglet.shapes.Circle(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,100,color=(100,100,100,255))

#instatiate detector
detector = HandDetector()


#Seting Up the conditions
distances = [100,200,300]
sizes = [30,40,50]
conditions = list(itertools.product(distances, sizes))
conditions = random.sample(conditions, len(conditions))
distance_con = None
size_con = None
target_number = 5
target_index = target_number
pressing = False
angle = 360 / target_number


def get_distance(x1,y1,x2,y2):
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance



def get_next_target():
    global distance_con
    global size_con
    global target_index
    global conditions
    #if distance_con and size_con:
        #normal state
    if target_index == target_number:
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
            pass
    else:
        target_index += 1    
        pass
    
    #there is only one target that gets relocated after each click  
    x,y = point_on_circle(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,distance_con,angle*target_index)
    target.x = x
    target.y=y
    target.radius=size_con
    
    
@window.event
def on_draw():
    window.clear()
    target.draw()
    cursor.draw()
    pass

def update(dt):
    global cursor
    global pressing
    x = 0
    y = 0
    
    #show hand recognition interaction on screen
    interacting, interaction_point= detector.run()
    if interaction_point:
        x = interaction_point[0] * WINDOW_WIDTH
        cursor.x = x
        y =  WINDOW_HEIGHT-interaction_point[1] * WINDOW_HEIGHT
        cursor.y = y
    else:
        cursor.x -10
        cursor.y -10
     
    # A "click" was made by pressing the thumb and index finger together    
    if interacting and pressing == False:
        cursor.color = color_active
        pressing = True
        press_interaction(x,y)
    
    # The "click" was released
    elif not interacting and pressing == True:
        cursor.color = color_inactive
        pressing = False
    pass
    
    
    
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        #Start Recording
        press_interaction(x, y)


#gather input from all input devices here
def press_interaction(x,y):
    d = get_distance(x,y,target.x,target.y)    
    if d < cursor.radius + target.radius:
        #the target was hit.
        print("Hit")
    else:
        #the target was not hit.
        print("Miss")
        pass
    #check if Target was clicked.
    #if target
    #go to next target.
    get_next_target()
    pass

pyglet.clock.schedule_interval(update, 1/120) 
pyglet.app.run()




#The circle should always be on the other side of the last one.
#timing between circle interaction
#logging results
#Possebility for lagging input