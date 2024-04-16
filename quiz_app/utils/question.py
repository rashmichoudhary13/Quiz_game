import os
import csv
import cv2

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
        print("Inside update_ans")
        cursor_int = [int(coord) for coord in cursor] 
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            print("Bounding Box Coordinates:", x1, y1, x2, y2)
            print("Cursor integer Coordinates:", cursor_int)
            if x1 < cursor_int[0] < x2 and y1 < cursor_int[1] < y2:
                print("Inside the box")
                self.userAns = x + 1
                print("updated the ans")
                # It changes the color of rectangle when it is clicked
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), cv2.FILLED)

def load_questions_from_csv():
    current_directory = os.path.dirname(__file__)
    pathCSV = os.path.join(current_directory, 'mcq.csv')
    with open(pathCSV, newline='\n') as f:
        reader = csv.reader(f)
        dataAll = list(reader)[1:]
    mcqList = [MCQ(q) for q in dataAll]
    
    qTotal = len(dataAll)
    return mcqList