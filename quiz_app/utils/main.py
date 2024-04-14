import cv2
import csv
import cvzone
import time
import os
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0) #to activate video cam
cap.set(3,1280) #for width of image
cap.set(4,720) #for height

try:
    detector = HandDetector(detectionCon=0.8)
except Exception as error:
    print("An exception occurred (1) :", error)
    detector = None 


class MCQ():
    def __init__(self,data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2= data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None
    
    def update(self, cursor, bboxs):
        
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), cv2.FILLED)

#Import csv file data
current_directory = os.path.dirname(__file__)
pathCSV = os.path.join(current_directory, 'mcq.csv')
with open(pathCSV,newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

#create object for each MCQ
mcqList = []
for q in dataAll:
    mcqList.append(MCQ(q))

print(len(mcqList))

#to calculate points
qNo = 0
qTotal = len(dataAll)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1) #to flip the cam
    if detector is not None:  # Check if detector is initialized successfully
        try:
            hands, img = detector.findHands(img)
        except Exception as error:
            print("An exception occurred (2):", error)
            
    

    #Putting question on webcam/screen
    if qNo < qTotal:
        mcq = mcqList[qNo]
        img,bbox = cvzone.putTextRect(img, mcq.question, [100,100],2,2,offset=51,border=5)
        img,bbox1 = cvzone.putTextRect(img, mcq.choice1, [100,250],2,2,offset=51,border=5)
        img,bbox2 = cvzone.putTextRect(img, mcq.choice2, [400,250],2,2,offset=51,border=5)
        img,bbox3 = cvzone.putTextRect(img, mcq.choice3, [100,400],2,2,offset=51,border=5)
        img,bbox4 = cvzone.putTextRect(img, mcq.choice4, [400,400],2,2,offset=51,border=5)

        # Checking if the ans is clicked
        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]
            length,info,img = detector.findDistance(lmList[8][0:2], lmList[12][0:2], img)
            if length < 35:
                mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                print(mcq.userAns)
                if mcq.userAns is not None:
                    time.sleep(0.3)
                    qNo += 1

    else: 
        score = 0
        for mcq in mcqList:
            if mcq.answer == mcq.userAns:
                score += 1
        score = round((score/qTotal)*100, 2)
        img, _ = cvzone.putTextRect(img, "Quiz Completed", [250, 300], 2, 2, offset=50, border=5)
        img, _ = cvzone.putTextRect(img, f'Your Score: {score}%', [700, 300], 2, 2, offset=50, border=5)
    
    # Draw a progress bar
    barValue = 150 + (950 //qTotal)*qNo                
    cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (150, 600), (1100, 650), (250, 0, 255), 5)
    img, _ = cvzone.putTextRect(img, f'{round((qNo/qTotal)*100)}%', [1130, 635], 2, 2, offset=16)

    cv2.imshow("Img",img)
    cv2.waitKey(1)
    #Used to terminate the screen
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break