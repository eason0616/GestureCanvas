import cv2
import os
import sys
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(parent_path)
from Models import _LoadSave as LoadSave
from ModelTraining.Testing.LiveTest_DataProcessing import LiveTest_DataProcessor as DataProcessor

class GestureCanvas_RandomForest:
    def __init__(self):
        self.model: SVC = LoadSave.load_model("SVC_1")
        self.scaler: StandardScaler = LoadSave.load_scaler("SVC_1")
        self.DataProcessing = DataProcessor()

        self.model.verbose = 0  # 關閉詳細輸出

        print("HandRecognition Initialized.")

    def __del__(self):
        cv2.destroyAllWindows()

    def startCanvas(self):
        print("Start Canvas")

        while True:
            frame, coords, Finger_pos = self.DataProcessing.getCoordData(draw=True)
            if frame is not None:
                cv2.imshow("Hand Recognition", frame)
                
            if cv2.waitKey(10) == ord('q'):
                break

            if coords is None:
                continue

            coords = self.scaler.transform([coords])

            prediction = self.model.predict(coords)
            print(*prediction)

if __name__ == "__main__":
    canvas = GestureCanvas_RandomForest()
    canvas.startCanvas()