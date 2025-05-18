import cv2
import numpy as np

from ModelTraining.Data.DataProcessBase import DataProcessBase

import warnings
warnings.filterwarnings("ignore", category= UserWarning)

class LiveTest_DataProcessor(DataProcessBase):
    """
    實時數據處理類別

    此類別負責從攝影機獲取實時數據, 並將數據轉換為可用於模型預測的格式

    Attributes:
        cap (cv2.VideoCapture): 影片擷取物件
        mp_hands (mediapipe.solutions.hands.Hands): MediaPipe 偵測手部關鍵點的物件
        mp_drawing (mediapipe.solutions.drawing_utils): MediaPipe 繪圖工具
        data_transform (DataTransform): 資料轉換工具
    """

    def __init__(self):
        """
        初始化實時數據處理類別
        """
        super().__init__(static_image_mode=False)

        # 初始化攝影機擷取物件, 並設定畫面大小為 640x480
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def getCoordData(self, draw=False) -> tuple[np.ndarray, np.ndarray, tuple[float, float]]:
        """
        獲取攝影機畫面, 並將畫面轉換為可用於模型預測的格式

        Args:
            draw (bool, optional): 是否繪製手部關鍵點. 預設為 False
        Returns:
            tuple: (np.ndarray, np.ndarray, tuple)
            - frame (np.ndarray): 獲取的畫面
            - coords (np.ndarray): 關鍵點座標
            - Finger_pos (tuple): 食指關鍵點螢幕相對位置
        Notes:
            - 如果畫面中沒有偵測到手部關鍵點, 則 coords 回傳 None
            - 回傳的座標為一維陣列, 形狀為 (63,), 原本為 (3, 21, 3) 的三維陣列
        """

        # 讀取攝影機畫面, 如果無法讀取則拋出異常
        ret, frame = self.cap.read()
        if not ret or frame is None:
            raise IOError("無法讀取攝影機畫面")
        
        # 將畫面處理過後, 並獲取手部關鍵點
        frame, result = self.PreprocessImage(frame)

        # 如果沒有偵測到手部關鍵點, 則回傳 None
        if result.multi_hand_landmarks is None:
            print("No hand detected.")
            return frame, None, None
        
        # 獲取食指關鍵點的螢幕相對位置
        Finger_pos = (result.multi_hand_landmarks[0].landmark[8].x, 
                      result.multi_hand_landmarks[0].landmark[8].y)

        # 正規化關鍵點座標並將其轉換為一維陣列, 形狀為 (63,)
        frame, coords = self.Normalize_Landmark_Coords(result.multi_hand_landmarks[0], draw=draw, frame=frame)

        # 回傳畫面和關鍵點座標
        return frame, coords.reshape(-1), Finger_pos