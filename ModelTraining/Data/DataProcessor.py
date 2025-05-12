import cv2
import os
import numpy as np

from ModelTraining.Data.ProcessBase import DataProcessBase
from ModelTraining.Data.DataAugmentation import HandDataAugmentation

# 設定資料夾路徑
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
UNPROCESSDATA_PATH = os.path.join(DIR_PATH, "RawImgs")
DATASETS_PATH = os.path.join(DIR_PATH, "DataSets")

# 設定 numpy 的印出格式, 關閉科學記號表示法
np.set_printoptions(suppress=True)

class HandRecognition_DataTransform(DataProcessBase):
    """
    手部關鍵點資料處理類別

    此類別使用 MediaPipe 偵測手部關鍵點, 並將其轉換為機器學習模型可用的格式

    此類別負責處理手部關鍵點資料, 包括:
    1. 偵測手部關鍵點
    2. 正規化手部關鍵點座標
    3. 數據增強
    4. 儲存處理後的資料

    Attributes:
        augmentation (DataAugmentation.HandDataAugmentation): 資料增強工具
        labels (list[str]): 訓練標籤
        category_labels (list[str]): 所有資料類別的名稱
        unProcessData (list[list[str]]): 所有資料類別的訓練資料
        processedData (np.ndarray): 處理後的資料
    """

    def __init__(self):
        super().__init__(static_image_mode= True)

        # 宣告資料增強工具
        self.augmentation = HandDataAugmentation()

        # 訓練標籤
        self.labels: list[str] = []

        # 所有資料類別的名稱
        self.category_labels: list[str] = [label for label in os.listdir(UNPROCESSDATA_PATH)
                                        if os.path.isdir(os.path.join(UNPROCESSDATA_PATH, label))]

        # 所有資料類別的訓練資料
        self.unProcessData: list[list[str]] = [[category for category in os.listdir(os.path.join(UNPROCESSDATA_PATH, label))]
                                                for label in self.category_labels]
        
        # 準備儲存處理後的資料
        self.processedData: np.ndarray = np.empty((0, 21, 3), dtype= np.float32)

    def ProcessingImages(self, show: bool = False) -> None:
        """
        處理原始手勢資料，將其轉換為機器學習模型可用的格式
        
        此函數執行以下步驟：
        1. 檢查所需資料夾是否存在
        2. 遍歷每個類別的圖像數據
        3. 對每張圖像執行手部關鍵點檢測
        4. 標準化關鍵點座標
        5. 進行數據增強
        6. 將處理後的數據存入類別變數中
        
        Args:
            show (bool): 是否顯示處理過程的可視化結果, 預設為 False
        Returns:
            None: 處理結果儲存在類別變數 processedData 和 labels 中
        Notes:
            - 使用.saveData()方法來儲存處理後的數據
            - 如果 show=True, 將會顯示處理過程的可視化結果,
              並在每次處理完一張圖片後等待使用者按下任意鍵確認
            - 如果 show=False, 則在處理完成後顯示總結資訊
        """

        # 檢查資料夾是否存在
        if not os.path.exists(UNPROCESSDATA_PATH):
            raise FileNotFoundError(f"Unprocessed data path {UNPROCESSDATA_PATH} not found.")
        if not os.path.exists(DATASETS_PATH):
            raise FileNotFoundError(f"DataSets path {DATASETS_PATH} not found.")
        
        # 顯示所有類別
        print("Categorys:", self.category_labels)

        # 依照類別處理轉換影像
        for category, images in zip(self.category_labels, self.unProcessData):
            # 略過放置沒有手的資料夾, 之後會將沒有手的資料移到這裡
            if category == ".NoHand":
                continue

            # 獲取目前類別的資料夾路徑
            category_path = os.path.join(UNPROCESSDATA_PATH, category)

            # 依序讀取每一張圖片
            for img in images:
                # 獲取圖片路徑
                img_path = os.path.join(category_path, img)

                # 讀取圖片, 如果圖片轉換失敗則發出警告並跳過
                frame = cv2.imread(img_path)
                if frame is None:
                    print(f"Error: Error in reading {img_path}")
                    continue

                # 將圖片進行預處理
                frame, result = self.PreprocessImage(frame)

                if result is None:
                    # 如果沒有偵測到手部關鍵點, 則發出警告
                    print(f"Warning: No hand in {img}")

                    # 並將圖片移到沒有手的資料夾
                    os.rename(img_path, os.path.join(UNPROCESSDATA_PATH, ".NoHand", img))
                    continue

                # 如果偵測到手部關鍵點, 則進行處理
                # 將偵測到的每一個手依序處理 (目前只支援單手)
                for hand_lmks in result.multi_hand_landmarks:
                    # 使用 Normalize_Landmark_Coords 將手部關鍵點座標進行標準化處理
                    frame, landmarks = self.Normalize_Landmark_Coords(hand_lmks, draw= show, frame= frame)
                    if frame is not None:
                        # 如果有要繪製的影像, 則顯示處理後的影像
                        cv2.imshow("HandRecognition", frame)

                    # 將標準化後的手部資料進行增強處理
                    augmented_landmarks = np.append([landmarks], self.augmentation(landmarks), axis= 0)
                    augmented_landmarks = np.round(augmented_landmarks, 4)

                    # 將增強後的資料加入到 processedData 中, 等待儲存
                    self.processedData = np.append(self.processedData, augmented_landmarks, axis= 0)

                    # 將 len(augmented_landmarks) 個標籤加入到 labels 中
                    # 這裡的 len(augmented_landmarks) 是經過資料增強後的資料筆數
                    for _ in range(len(augmented_landmarks)):
                        self.labels.append(category)
                
                # 顯示處理完成的訊息
                print(f"Info: Data {img} processed.")

                # show= True: 按任何按鍵繼續, False: 直接往下進行
                cv2.waitKey(0) if show else cv2.waitKey(1)
        
        # 關閉所有視窗
        cv2.destroyAllWindows()

        # 如果不顯示處理過程, 則顯示處理完成的訊息
        if not show:
            print(f"Info: {len(self.processedData)} data processed.")

    def saveData(self) -> None:
        """
        儲存處理後的資料到檔案中

        此函數將處理後的資料儲存為 .npz 格式的檔案, 以便於後續使用。

        Args:
            None
        Returns:
            None
        Notes:
            - 儲存的檔案名稱為 handData_{資料筆數}_.npz
            - 儲存的資料包含 labels 和 processedData
            - 如果 labels 和 processedData 的長度不一致, 則會引發 ValueError
        """

        # 檢查 labels 和 processedData 的長度是否一致
        if not len(self.labels) == len(self.processedData):
            raise ValueError(f"Data length not match: {len(self.labels)} != {len(self.processedData)}")

        # 設定儲存的檔案名稱
        file_name = f"handData_{len(self.processedData)}_.npz"
        file_path = os.path.join(DATASETS_PATH, file_name)

        # 將 labels 和 processedData 儲存到.npz 檔案中
        np.savez(file_path, labels= self.labels, data= self.processedData)

        # 檢查儲存的檔案是否正確, 如果不正確則引發 ValueError
        test_data = np.load(file_path)
        if not(np.array_equal(test_data['labels'], self.labels) and np.array_equal(test_data['data'], self.processedData)):
            raise ValueError("Data not saved correctly")
        
        # 顯示儲存完成的訊息
        print(f"\nDataSet saved to {file_path}")

if __name__ == "__main__":
    handRecognition = HandRecognition_DataTransform()
    handRecognition.ProcessingImages(show= False)
    handRecognition.saveData()