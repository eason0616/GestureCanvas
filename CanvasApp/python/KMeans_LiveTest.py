import cv2
import pyautogui

from Models import _LoadSave as LoadSave
from LiveTest_DataProcessing import LiveTest_DataProcessing as DataProcessing
from mouse_control import MouseController

class GestureCanvas_KMeans:
    def __init__(self):
        self.model = LoadSave.load_model("KMeans_2")
        self.scaler = LoadSave.load_scaler("KMeans_2")
        self.DataProcessing = DataProcessing()

        self.mouse = MouseController()

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
                pyautogui.mouseUp()
                continue
            else:
                pyautogui.mouseDown(button="left")
                pass

            try:
                coords = self.scaler.transform([coords])

                prediction = self.model.predict(coords)
                print(*prediction)

                screen_x = int(Finger_pos[0] * self.mouse.screen_width)
                screen_y = int(Finger_pos[1] * self.mouse.screen_height)
                self.mouse.move_to(screen_x, screen_y, duration=0)
            except Exception as e:
                print(f"Error: {e}")
                self.mouse.release()
                continue

if __name__ == "__main__":
    canvas = GestureCanvas_KMeans()
    canvas.startCanvas()
