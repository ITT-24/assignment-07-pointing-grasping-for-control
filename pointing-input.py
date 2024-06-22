# Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

def draw_landmarks_on_image(detection_result):
    print("3")
    hand_landmarks_list = detection_result.hand_landmarks 


    distance = None
    interaction_point = None
    # Loop through the detected hand landmarks to visualize.
    #print("-------------")
    #print(hand_landmarks_list[0])
    
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        #print(idx)
        
        selected_landmarks = [landmark for i, landmark in enumerate(hand_landmarks) if i in [4, 8]]
        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in selected_landmarks
        ])
        
        
        if len(selected_landmarks) == 2:
            x1, y1 = selected_landmarks[0].x, selected_landmarks[0].y 
            x2, y2 = selected_landmarks[1].x, selected_landmarks[1].y

            # Calculate and display the distance between the points
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            midpoint = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            interaction_point = selected_landmarks[1]
           
#        solutions.drawing_utils.draw_landmarks(
#            annotated_image,
#            hand_landmarks_proto,
#            solutions.hands.HAND_CONNECTIONS,
#            solutions.drawing_styles.get_default_hand_landmarks_style())

    return distance, interaction_point

class HandDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.dimensions = (480, 640, 3)
        self.distance = None 
        self.interaction_point = None
        self.annotated_image = np.zeros(self.dimensions, dtype=np.uint8)
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.get_interaction)
        self.landmarker = HandLandmarker.create_from_options(self.options)

        
            # Create a hand landmarker instance with the live stream mode:
    def get_interaction(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        out = np.zeros(self.dimensions)
        # Process and store the annotated image
        #self.annotated_image = draw_landmarks_on_image(output_image.numpy_view(), result)
     
        self.distance, self.interaction_point = draw_landmarks_on_image(result)
        
        
    def run(self):
    
        success, frame = self.cap.read()
        #if not success:
        #    break

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        pose_result=self.landmarker.detect_async(mp_image, int(time.time() * 1000))
        
        if self.interaction_point and self.distance:
        #try:
        #    cv2.imshow('Annotated Image', self.annotated_image)
        #except:
        #    return
        
            print(str(self.distance) + " " +str(self.interaction_point))
        
        if cv2.waitKey(1) == ord('q'):
            self.running = False


    # Create a hand landmarker instance with the live stream mode:
    def print_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        out = np.zeros(self.dimensions)
        # Process and store the annotated image
        #self.annotated_image = draw_landmarks_on_image(output_image.numpy_view(), result)
        self.annotated_image, a1, b2 = draw_landmarks_on_image(out, result)
        
    def run_old(self):
    
        success, frame = self.cap.read()
        #if not success:
        #    break

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        pose_result=self.landmarker.detect_async(mp_image, int(time.time() * 1000))

        try:
            cv2.imshow('Annotated Image', self.annotated_image)
        except:
            return
        #if self.annotated_image is not None:
        #    cv2.imshow('Annotated Image', self.annotated_image)
        #    print("hi")
        time.sleep(0.05)
        if cv2.waitKey(1) == ord('q'):
            self.running = False
def draw_landmarks_on_image_old(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks 
    annotated_image = np.copy(rgb_image)

    distance = None
    interaction_point = None
    # Loop through the detected hand landmarks to visualize.
    #print("-------------")
    #print(hand_landmarks_list[0])
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        #print(idx)
        
        selected_landmarks = [landmark for i, landmark in enumerate(hand_landmarks) if i in [4, 8]]
        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in selected_landmarks
        ])
        
        for landmark in selected_landmarks:
            landmark_point = (int(landmark.x * annotated_image.shape[1]), int(landmark.y * annotated_image.shape[0]))
            cv2.circle(annotated_image, landmark_point, 5, (0, 255, 0), -1)
        
        
        if len(selected_landmarks) == 2:
            x1, y1 = selected_landmarks[0].x * annotated_image.shape[1], selected_landmarks[0].y * annotated_image.shape[0]
            x2, y2 = selected_landmarks[1].x * annotated_image.shape[1], selected_landmarks[1].y * annotated_image.shape[0]

            # Calculate and display the distance between the points
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            midpoint = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            cv2.putText(annotated_image, f'Dist: {distance:.2f}', midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            interaction_point = selected_landmarks[1]
#        solutions.drawing_utils.draw_landmarks(
#            annotated_image,
#            hand_landmarks_proto,
#            solutions.hands.HAND_CONNECTIONS,
#            solutions.drawing_styles.get_default_hand_landmarks_style())

    return annotated_image, distance, interaction_point
    

if __name__ == '__main__':
    detector = HandDetector()
    while detector.running:
        detector.run()
        if cv2.waitKey(1) == ord('q'):
                detector.running = False
    detector.cap.release()
    cv2.destroyAllWindows()
    
