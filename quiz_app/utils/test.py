import HandDec
import time
import cv2

timeS = time.time()

class_obj = HandDec.HandDetector()  # Correct class initialization
cam = cv2.VideoCapture(0)  # Correct camera initialization

while cam.isOpened():
    success, image = cam.read()
    if not success: continue

    detected_hand = class_obj.findHand(image, draw_detect=True)  # Correct method call
    hand_landmark = class_obj.findLocations(image, draw_detect=True,draw_id=8)  # Correct method call

    timeE = time.time()
    fps = int(1 / (timeE - timeS))
    timeS = timeE
    cv2.putText(image, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow('Hand Detection - Chanchal Roy', image)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
