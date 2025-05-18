import cv2
import numpy as np
from typing import Optional, Tuple, Any
from mediapipe.python.solutions import hands

# 初始化 mediapipe 模組
mp_hands = hands

class DataProcessBase:
    """
    手部關鍵點資料處理基類
    
    此類別使用 MediaPipe 偵測手部關鍵點, 並將其轉換為機器學習模型可用的格式
    此類別負責處理手部關鍵點資料, 包括:
    1. 偵測手部關鍵點
    2. 正規化手部關鍵點座標
    3. 繪製手部關鍵點並對比原始影像
    """

    def __init__(self, static_image_mode: bool = True):
        """
        初始化 MediaPipe 偵測手部關鍵點的物件
        Args:
            static_image_mode (bool): 是否使用靜態圖片模式, 預設為 True
        """

        # 宣告 MediaPipe 偵測手部關鍵點的物件
        self.mp_hands = mp_hands.Hands(
            static_image_mode=static_image_mode,    # 設定為靜態圖片模式
            max_num_hands=1,                        # 設定最大偵測手部數量為 1
            min_detection_confidence=0.5,           # 最小偵測信心值
            min_tracking_confidence=0.5             # 最小追蹤信心值
        )

    def __del__(self):
        """
        釋放 MediaPipe 偵測手部關鍵點的物件
        """
        self.mp_hands.close()

    def Normalize_Landmark_Coords(self,
                                landmarks: Any,
                                draw: bool = False,
                                frame: Optional[np.ndarray] = None) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """
        歸一化手部關鍵點座標

        將手部關鍵點座標進行標準化處理:
        1. 提取所有關鍵點的 x, y, z 座標
        2. 計算所有關鍵點的中心點並進行平移使中心點置中
        3. 計算手掌方向並進行旋轉, 使手掌朝向固定方向

        Args:
            landmarks: 由 MediaPipe 偵測到的手部關鍵點
            draw: 是否繪製關鍵點到影像上
            frame: 若 draw=True 時要繪製的影像
        Returns:
            tuple: (frame, coords)
            - frame (numpy.ndarray): 繪製後的影像, 如果 draw=False 則為 None
            - coords (numpy.ndarray): 歸一化後的手部關鍵點座標, 形狀為 (21, 3), 每個關鍵點包含 (x, y, z) 座標
        """

        # 提取所有關鍵點的 x, y, z 座標為 numpy 陣列 格式為 [[x, y, z], ...], 並四捨五入到小數點後 4 位
        coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])

        # 計算中心點
        center = np.mean(coords, axis=0)
        coords = coords - center

        # 計算手掌方向向量 (從手腕到中指根部)
        direction_vector = coords[9] - coords[0]

        # 計算Z軸旋轉角度 (使手掌朝右)
        angle_z = np.arctan2(direction_vector[1], direction_vector[0])

        # Z軸旋轉矩陣
        Rz = np.array([
            [np.cos(angle_z), -np.sin(angle_z), 0],
            [np.sin(angle_z), np.cos(angle_z), 0],
            [0, 0, 1]
        ])

        # 如果有要繪製的影像, 則保留原始座標作為對比使用
        origin_coords = coords.copy() if draw and frame is not None else None

        # 應用旋轉矩陣
        coords = coords @ Rz

        # 如果有要繪製, 則將關鍵點及原始座標繪製到影像上
        if draw and frame is not None and origin_coords is not None:
            frame = self.Render_Landmarks(frame, center, coords, origin_coords)
            return frame, coords
        else:
            # 回傳歸一化後的座標, 並四捨五入到小數點後 4 位
            return None, np.round(coords, 4)

    def Render_Landmarks(self,
                        frame: np.ndarray,
                        center: Tuple[float, float, float],
                        coords: np.ndarray,
                        origin_coords: np.ndarray) -> np.ndarray:
        """
        在畫面上渲染手部關鍵點。

        該函數在給定的影像幀上繪製手部關鍵點, 包括原始關鍵點和處理後的關鍵點, 並將兩種結果並排顯示。

        Args:
            frame (numpy.ndarray): 要繪製關鍵點的影像幀。
            center (tuple): 手部中心點的三維座標 (x, y, z)。
            coords (numpy.ndarray): 處理後的手部關鍵點座標, 形狀為 (n, 3), 每個關鍵點包含 (x, y, z) 座標。
            origin_coords (numpy.ndarray): 原始手部關鍵點座標，形狀為 (n, 3), 每個關鍵點包含 (x, y, z) 座標。
        Returns:
            numpy.ndarray: 繪製後的影像幀, 包含處理後的關鍵點和原始關鍵點。
        Notes:
            - 處理後的關鍵點使用綠色 (128, 255, 0) 顯示。
            - 原始關鍵點使用黃色 (0, 255, 255) 顯示。
            - 手部中心點在兩個畫面中都用藍色 (255, 0, 0) 顯示。
        """

        # 獲取畫面的高、寬、色彩
        height, width, _ = frame.shape
        origin_frame = frame.copy()

        # 獲取手部中心點座標
        center_x, center_y, center_z = center

        # 獲取手部中心點在畫面中的像素位置, 並繪製在畫面上
        handCenter_x, handCenter_y = int(
            center_x * width), int(center_y * height)  # 手部中心點在畫面中的像素位置

        # 繪製原始手部關鍵點
        cv2.circle(origin_frame, (handCenter_x, handCenter_y),
                   5, (255, 0, 0), -1)
        if origin_coords is not None:
            Pos = np.array([[int((center_x + x) * width), int((center_y + y) * height)]
                           for x, y, z in origin_coords])
            for p in Pos:
                cv2.circle(origin_frame, p, 5, (0, 255, 255), -1)

        # 繪製處理後的手部關鍵點
        cv2.circle(frame, (handCenter_x, handCenter_y), 5, (255, 0, 0), -1)
        Pos = np.array([[int((center_x + x) * width),
                       int((center_y + y) * height)] for x, y, z in coords])
        for p in Pos:
            cv2.circle(frame, p, 5, (128, 255, 0), -1)

        # 將兩個畫面並排顯示
        origin_frame = cv2.resize(origin_frame, (640, 480))
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.hconcat([frame, origin_frame])

        return frame

    def PreprocessImage(self, frame: np.ndarray) -> Tuple[np.ndarray, Any]:
        """
        將圖片進行預處理, 包括旋轉、調整大小和顏色轉換

        Args:
            frame (numpy.ndarray): 要處理的圖片
        Returns:
            tuple: (frame, result)
            - frame (numpy.ndarray): 處理後的圖片
            - result (mp.solutions.hands.Hands): MediaPipe 偵測結果, 包含手部關鍵點資訊
        """

        # 獲取圖片的高、寬、色彩, 並將圖片統一旋轉為橫向
        height, width, _ = frame.shape
        if height > width:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 將圖片轉換為 RGB 格式, 並將圖片大小統一為 640x480以加速處理
        frame = cv2.resize(frame, (640, 480))
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 利用 MediaPipe 偵測手部關鍵點
        result = self.mp_hands.process(imgRGB)

        return frame, result
