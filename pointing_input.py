# Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

from pynput.mouse import Button, Controller

model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

RESOLUTION = (1920, 1200)

def determine_interaction(threshold, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks 


    distance = None
    interaction_point = None
    interacting= False
    # Loop through the detected hand landmarks to visualize.
    
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
    if distance:
        if distance <= threshold:
            interacting =True
    
    return interacting, interaction_point

class HandDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.dimensions = (480, 640, 3)
        self.interacting = None 
        self.interaction_point = None
        self.annotated_image = np.zeros(self.dimensions, dtype=np.uint8)
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.get_interaction)
        self.landmarker = HandLandmarker.create_from_options(self.options)
        self.threshold = 0.1

        
        self.mouse = Controller()
        self.lmb_status = False # True: Left Mouse Button is held down. False: Left Mouse Button is not pressed.
        self.interaction_point_previous_position = None
        self.cursor_velocity = 1
        
            # Create a hand landmarker instance with the live stream mode:
    def get_interaction(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        out = np.zeros(self.dimensions)
     
        self.interacting, self.interaction_point = determine_interaction(self.threshold, result)
        #print("reached"+str(self.interacting)+" "+ str(d))

    def control_cursor(self):
        
        lmb_down = self.interacting 
        if not self.interaction_point is None:
            cursor_x, cursor_y = self.interaction_point # TODO: Map image coordinates to screen coordinates
            
            self.mouse.position = (cursor_x * RESOLUTION[0], cursor_y * RESOLUTION[1]) # TODO: Smoothing
        
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

        #if self.interaction_point and self.interacting:
        #    print(str(self.interacting) + " " +str(self.interaction_point))
        
        if cv2.waitKey(1) == ord('q'):
            self.running = False
        return self.interacting, self.interaction_point


if __name__ == '__main__':
    detector = HandDetector()
    while detector.running:
        a, b =detector.run()
        detector.control_cursor()
        if cv2.waitKey(1) == ord('q'):
                detector.running = False
    detector.cap.release()
    cv2.destroyAllWindows()
    
