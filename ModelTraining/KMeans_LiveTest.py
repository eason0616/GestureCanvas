import cv2

import TrainingFunc
from LiveTest_DataProcessing import LiveTest_DataProcessing as DataProcessing

class GestureCanvas_KMeans:
    def __init__(self):
        self.model = TrainingFunc.load_model("KMeans_2")
        self.scaler = TrainingFunc.load_scaler("KMeans_2")
        self.DataProcessing = DataProcessing()

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
    canvas = GestureCanvas_KMeans()
    canvas.startCanvas()