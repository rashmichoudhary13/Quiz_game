import cv2
import csv
import os
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0) #to activate video cam
cap.set(3,1280) #for width of image
cap.set(4,720) #for height

try:
    detector = HandDetector(detectionCon=0.8)
except Exception as error:
    print("An exception occurred (1) :", error)
    detector = None  # Set detector to None if initialization fails


class MCQ():
    def __init__(self,data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2= data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None


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
    img = cv2.flip(img,1)
    if detector is not None:  # Check if detector is initialized successfully
        try:
            hands, img = detector.findHands(img)
        except Exception as error:
            print("An exception occurred (2):", error)
            
    cv2.imshow("Img",img)
    cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()