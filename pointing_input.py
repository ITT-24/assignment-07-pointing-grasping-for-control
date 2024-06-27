# Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from collections import deque

from pynput.mouse import Button, Controller

model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

RESOLUTION = (1920, 1200)
NUM_SAVED_PREVIOUS_POSIITIONS = 10
MARGIN = 0.1
CHECK_BEFORE_ACTIVATION = 1

THRESHHOLD = 0.1
THRESHHOLD_D = 0.2




def determine_distance(detection_result):
    hand_landmarks_list = detection_result.hand_landmarks 
    distance = None
    interaction_point = None
    
    for idx in range(len(hand_landmarks_list)):
        
        hand_landmarks = hand_landmarks_list[idx]
                
        selected_landmarks = [landmark for i, landmark in enumerate(hand_landmarks) if i in [4, 8]]

        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in selected_landmarks
        ])
        
        
        if len(selected_landmarks) == 2:
            x1, y1 = selected_landmarks[0].x, selected_landmarks[0].y 
            x2, y2 = selected_landmarks[1].x, selected_landmarks[1].y

            # Calculate the distance between the points
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            midpoint = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            interaction_point = (x1, y1)
    
    return distance, interaction_point
    
def determine_interaction(threshold, threshold_deactivate, distance, activation_countdown, interacting_old):    
    interacting= interacting_old
    # Loop through the detected hand landmarks to visualize.    
    if distance:
        if distance <= threshold:
            if activation_countdown <= 0:
                interacting =True
            else:
                activation_countdown-=1
        elif distance > threshold_deactivate:
            activation_countdown = CHECK_BEFORE_ACTIVATION
            interacting = False
    return interacting, activation_countdown

class HandDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.dimensions = (480, 640, 3)
        self.interacting = False
        self.interaction_point = None
        self.annotated_image = np.zeros(self.dimensions, dtype=np.uint8)
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.get_interaction)
        self.landmarker = HandLandmarker.create_from_options(self.options)
        self.threshold = 0.1
        self.threshold_deactivate = 0.2
        self.activation_countdown=CHECK_BEFORE_ACTIVATION
        
        self.mouse = Controller()
        self.lmb_status = False # True: Left Mouse Button is held down. False: Left Mouse Button is not pressed.
        self.previous_positions = deque([], maxlen=NUM_SAVED_PREVIOUS_POSIITIONS)
        self.cursor_velocity = 1
        self.distance = None
            # Create a hand landmarker instance with the live stream mode:
    def get_interaction(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        out = np.zeros(self.dimensions)
        self.distance, self.interaction_point= determine_distance(result)
        
    
        
        #print("reached"+str(self.interacting)+" "+ str(d))

    def control_cursor(self):
        
        lmb_down = self.interacting 
        if not self.interaction_point is None:
            cursor_x, cursor_y = self.interaction_point # TODO: Map image coordinates to screen coordinates
            
            self.previous_positions.append((cursor_x, cursor_y))
            average_x, average_y = 0, 0
            for position in self.previous_positions:
                average_x += position[0]
                average_y += position[1]
            average_x = average_x / len(self.previous_positions)
            average_y = average_y / len(self.previous_positions)
            self.mouse.position = ((average_x - MARGIN) * (1 + 2 * MARGIN) * RESOLUTION[0], (average_y - MARGIN) * (1 + 2 * MARGIN) * RESOLUTION[1]) # TODO: Smoothing
        else:
            self.previous_positions.clear()
            lmb_down = False
        
        if lmb_down != self.lmb_status:
            if lmb_down:
                self.mouse.press(Button.left)
            else:
                self.mouse.release(Button.left)
        
        self.lmb_status = lmb_down

        #if lmb_down != self.lmb_status: # Either LMB was pressed before and was just released, or vice versa; which means that we have to trigger an event.
        
        
        
    def run(self):
    
        success, frame = self.cap.read()
        #if not success:
        #    break

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        pose_result=self.landmarker.detect_async(mp_image, int(time.time() * 1000))
        self.interacting, self.activation_countdown = determine_interaction(self.threshold, self.threshold_deactivate, self.distance, self.activation_countdown, self.interacting)   
        #if self.interaction_point and self.interacting:
        #    print(str(self.interacting) + " " +str(self.interaction_point))
        
        if cv2.waitKey(1) == ord('q'):
            self.running = False
        return self.interacting, self.interaction_point



    def calibration(self):
        
        success, frame = self.cap.read()
        #if not success:
        #    break

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        pose_result=self.landmarker.detect_async(mp_image, int(time.time() * 1000))
        return self.distance


if __name__ == '__main__':
    detector = HandDetector()
    print("For calibration, please position your hand in front of the camera so that the index finger and thumb are almost touching, and press enter.")
    input()
    print("calibrating")
    distance_open = None
    distance_closed = None
    while distance_closed==None:
        distance_closed = detector.calibration()

    
    
    print("Now, with your hand in the same place, spread your thumb and index finger away from each other and hit enter again.")
    input()
    print("calibrating")
    while distance_open==None:
        distance_open = detector.calibration()
    
    detector.threshold = distance_closed*1.5
    
    detector.threshold_deactivate = distance_closed +(distance_open-distance_closed)/2
    if detector.threshold >detector.threshold_deactivate:
        detector.threshold_deactivate = detector.threshold * 1.5
    
    
    print(str(detector.threshold_deactivate)+ " " + str( detector.threshold) )
    
    print("Hand interaction mode active")
    
    while detector.running:
        a, b =detector.run()
        detector.control_cursor()
        if cv2.waitKey(1) == ord('q'):
                detector.running = False
    detector.cap.release()
    cv2.destroyAllWindows()
    
