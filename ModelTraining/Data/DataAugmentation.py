import numpy as np

class HandDataAugmentation:
    """
    手部關鍵點資料增強類別

    Attributes:
        noise_level (float): 隨機噪聲的標準差
        scale_range (tuple): 隨機縮放的範圍
        shift_range (tuple): 隨機平移的範圍
    """

    def __init__(self):
        self.noise_level = 0.002
        self.scale_range = (0.95, 1.05)
        self.shift_range = (-0.01, 0.01)
    
    def __call__(self, data: np.ndarray) -> np.ndarray:
        """對手部關鍵點資料進行增強"""
        return self.augment(data)

    def augment(self, data: np.ndarray) -> np.ndarray:
        """
        對手部關鍵點資料進行增強

        Args:
            data (np.ndarray): 原始手部關鍵點資料, 形狀為 (21, 3), 21 為關鍵點數量, 3 為 x, y, z 坐標
        Returns:
            np.ndarray: 增強後的資料, 形狀為 (3, 21, 3)
            其中 3 為增強後的資料數量, 21 為關鍵點數量, 3 為 x, y, z 坐標
        """
        results = []
        results.append(self.add_noise(data))
        results.append(self.add_shift(data))
        results.append(self.scale(data))

        return np.array(results)

    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """添加隨機噪聲"""
        noise = np.random.normal(0, self.noise_level, size= data.shape)
        return data + noise

    def add_shift(self, data: np.ndarray) -> np.ndarray:
        """隨機平移"""
        shift = np.random.uniform(*self.shift_range, size= 3)
        return data + shift
    
    def scale(self, data: np.ndarray) -> np.ndarray:
        """隨機縮放"""
        scale = np.random.uniform(*self.scale_range)
        return data * scale

if __name__ == "__main__":
    data = np.random.rand(21, 3)  # 模擬手部關鍵點資料
    aug = HandDataAugmentation()
    augmented = np.append([data], aug.augment(data), axis= 0)
    print(f"原始資料形狀: {data.shape}")
    print(data)
    print(f"增強後資料形狀: {augmented.shape}")  # 應為 (3, 21, 3)
    print(augmented)