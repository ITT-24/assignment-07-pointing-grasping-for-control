import numpy as np
import pyglet
from pointing_input import HandDetector
from pyglet.window import mouse
import itertools

#circle point calculation was done with chatGPT
def point_on_circle(cx,cy,radius,angle_deg):
    angle_rad = np.radians(angle_deg)
    x = cx + radius * np.cos(angle_rad)
    y = cy + radius * np.sin(angle_rad)
    return x, y


WINDOW_WIDTH = 1220
WINDOW_HEIGHT = 760
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
color_inactive=(210,204,0,255)
color_active=(255,247,5,255)
cursor = pyglet.shapes.Circle(-10,-10,10,color=(210,204,0,100))
target = pyglet.shapes.Circle(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,100,color=(100,100,100,255))

detector = HandDetector()


#Seting Up the conditions
distances = [100,200,300]
distance_con = None
distance_con_index = 0
sizes = [30,40,50]
size_con = None
size_con_index = 0
target_number = 5
target_index = 0

conditions = list(itertools.product(distances, sizes))


pressing = False
angle = 360 / target_number


def get_distance(x1,y1,x2,y2):
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

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

def get_next_target():
    global distance_con
    global size_con
    global distance_con_index
    global size_con_index
    global distances
    global sizes
    global target_index
    if distance_con and size_con:
        #normal state
        if target_index == target_number:
            #check if there are conditions left.
            if distance_con_index < len(distances) -1 or size_con_index < len(sizes)-1:                
                
                if size_con_index < len(sizes)-1:
                    size_con_index += 1
                else:
                    size_con_index = 0
                    distance_con_index +=1
                #start new condition
                distance_con = distances[distance_con_index]
                size_con = sizes[size_con_index]
                
                target_index = 1
            else: 
                #end test
                print("end test")
                pass
        else:
            target_index += 1    
        pass
    else:
        #first click
        target_index = 1
        distance_con = distances[distance_con_index]
        size_con = sizes[size_con_index]
        pass
    
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
    interacting, interaction_point= detector.run()
    if interaction_point:
        x = interaction_point[0] * WINDOW_WIDTH
        cursor.x = x
        y =  WINDOW_HEIGHT-interaction_point[1] * WINDOW_HEIGHT
        cursor.y = y
    else:
        cursor.x -10
        cursor.y -10
        
    if interacting and pressing == False:
        cursor.color = color_active
        pressing = True
        press_interaction(x,y)
        
    elif not interacting:
        cursor.color = color_inactive
        pressing = False
    pass
    
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        #Start Recording
        press_interaction(x, y)
    
pyglet.clock.schedule_interval(update, 1/120) 
pyglet.app.run()



#timing between circle interaction
#logging results