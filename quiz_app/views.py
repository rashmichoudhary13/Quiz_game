from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import cv2
import csv
import os
import cvzone
import threading
import time
import HandDec

# class for question
class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update_ans(self, frame, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            print("Bounding box: ",x1,y1,x2,y2)
            cursor_x, cursor_y = int(cursor[0]), int(cursor[1])
            print("cusor_x: ", cursor_x)
            print("cusor_y: ", cursor_y)
            if x1 < cursor_x < x2 and y1 < cursor_y < y2:
                self.userAns = x + 1
                # Change the color of rectangle when it is clicked
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)

current_directory = os.path.dirname(__file__)
pathCSV = os.path.join(current_directory, 'mcq.csv')
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

# #to calculate points
qTotal = len(dataAll)  

#create object for each MCQ
mcqList = []
for q in dataAll:
    mcqList.append(MCQ(q))
print("Total question: ", len(mcqList))

# Create your views here.
def index(request):
    return render(request, 'index.html')


# Fuction for webcam
@gzip.gzip_page
def webcam(request):
    try:
        cam = VideoCamera(mcqList)
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print(e)
        pass
    return render(request, 'webcam.html')

class VideoCamera(object):
    def __init__(self, mcq_list, width=1280, height=720, flip=True):
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, width)   # Set frame width
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.flip = flip
        (self.grabbed, self.frame) = self.video.read()
        self.class_obj = HandDec.HandDetector()  # Initialize hand detector
        threading.Thread(target=self.update, args=()).start()
        self.mcq_list = mcq_list
        self.qNo = 0
        
    def __del__(self):
        self.video.release()

    def get_frame(self):
        _, frame = self.video.read()  # Read the frame from the camera
        if self.flip: 
            frame = cv2.flip(frame, 1)  # Flip the frame horizontally if flip is True
        detected_hand = self.class_obj.findHand(frame, draw_detect=True)  # Detect hand
        hand_landmark = self.class_obj.findLocations(frame, draw_id=8)  # Find hand landmarks
        if hand_landmark[0]:
            distance = self.class_obj.findDistance(frame, 8, 12, draw_detect=True)  # Example usage of findDistance
            print("Distance:", distance)
            
        # Draw question and choices on webcam
        if self.qNo < qTotal:
            mcq = mcqList[self.qNo]  # Get the first question
            frame,bbox = cvzone.putTextRect(frame, mcq.question, [100,100],2,2,offset=51,border=5)
            frame,bbox1 = cvzone.putTextRect(frame, mcq.choice1, [100,250],2,2,offset=51,border=5)
            frame,bbox2 = cvzone.putTextRect(frame, mcq.choice2, [400,250],2,2,offset=51,border=5)
            frame,bbox3 = cvzone.putTextRect(frame, mcq.choice3, [100,400],2,2,offset=51,border=5)
            frame,bbox4 = cvzone.putTextRect(frame, mcq.choice4,  [400,400],2,2,offset=51,border=5)
            
            for hand_landmarks in detected_hand:
                if hand_landmarks:
                     cursor_norm = hand_landmarks[8]  # Normalized coordinates of the tip of the index finger
                     # Convert normalized coordinates to image coordinates
                     cursor_img_x = int(cursor_norm[0] * 1280)
                     cursor_img_y = int(cursor_norm[1] * 720)
                     if distance < 0.05: #if length < 35 means the ans is clicked
                        mcq.update_ans(frame, (cursor_img_x, cursor_img_y), [bbox1, bbox2, bbox3, bbox4])
                        print(mcq.userAns)
                        if mcq.userAns is not None:
                            time.sleep(0.03)
                            self.qNo+=1
        else: 
            score = 0
            for mcq in mcqList:
                if mcq.answer == mcq.userAns:
                    score += 1
            score = round((score/qTotal)*100, 2)
            frame, _ = cvzone.putTextRect(frame, "Quiz Completed", [250, 300], 2, 2, offset=50, border=5)
            frame, _ = cvzone.putTextRect(frame, f'Your Score: {score}%', [700, 300], 2, 2, offset=50, border=5)
            
        # Draw a progress bar           
        barValue = 150 + (950 //qTotal)*self.qNo                
        cv2.rectangle(frame, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
        cv2.rectangle(frame, (150, 600), (1100, 650), (250, 0, 255), 5)
        frame, _ = cvzone.putTextRect(frame, f'{round((self.qNo/qTotal)*100)}%', [1130, 635], 2, 2, offset=16)
    
                   
        # Convert frame to JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def update(self):
          while True:
            (self.grabbed, self.frame) = self.video.read()
            time.sleep(0.03)  # Add a short delay to control frame rate
       
def gen(camera):
    while True:
        frame = camera.get_frame()  
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
