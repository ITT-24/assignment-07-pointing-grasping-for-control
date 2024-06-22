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

def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks 
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hand landmarks to visualize.
    print("-------------")
    print(hand_landmarks_list[0])
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style())
    return annotated_image

class HandDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.dimensions = (480, 640, 3)
        self.annotated_image = np.zeros(self.dimensions, dtype=np.uint8)
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result)

    # Create a hand landmarker instance with the live stream mode:
    def print_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        out = np.zeros(self.dimensions)
        # Process and store the annotated image
        #self.annotated_image = draw_landmarks_on_image(output_image.numpy_view(), result)
        self.annotated_image = draw_landmarks_on_image(out, result)
        
    def run(self):
        with HandLandmarker.create_from_options(self.options) as landmarker:
            while self.running:
                success, frame = self.cap.read()
                #if not success:
                #    break

                frame = cv2.flip(frame, 1)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                pose_result=landmarker.detect_async(mp_image, int(time.time() * 1000))

                try:
                    cv2.imshow('Annotated Image', self.annotated_image)
                except:
                    continue
                #if self.annotated_image is not None:
                #    cv2.imshow('Annotated Image', self.annotated_image)
                #    print("hi")
                time.sleep(0.05)
                if cv2.waitKey(1) == ord('q'):
                    self.running = False

            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    detector = HandDetector()
    detector.run()
