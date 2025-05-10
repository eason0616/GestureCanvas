import os
import numpy as np

def load_dataset(info: int= 0) -> tuple[np.ndarray, np.ndarray]:
    """
    載入資料集, 回傳資料集的特徵features與標籤labels (Features, Labels)

    Args:
        info (int, optional): 顯示資料集的資訊. 預設為0 - 顯示模式 0: 顯示載入完成, 1: 顯示資料集形狀, 2: 顯示資料集內容
    """

    # 獲取資料集路徑
    dir_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(dir_path, "Data", "DataSets")

    # 獲取資料夾內所有資料集 (.npz檔)
    datasets = [dataset for dataset in os.listdir(data_path) if dataset.endswith('.npz')]

    # 顯示資料集名稱, 讓使用者選擇要載入的資料集
    choose = input(f"Choose a dataset to load: {datasets}\n")
    
    # 利用使用者輸入的資料集名稱, 獲取資料集路徑 (輸入選擇的的數字為資料集的資料數量)
    data_path = os.path.join(data_path, [dataset for dataset in datasets if dataset.split('_')[1] == choose][0])
    print(f"Loading {data_path}...")

    # 載入資料集, 並將資料集的特徵features與標籤labels分開
    data = np.load(data_path)
    X: np.ndarray = data['data']
    y: np.ndarray = data['labels']

    # 設定 info 參數, 顯示資料集的資訊
    if info >= 0:
        print("Dataset Loaded.")
    if info >= 1:
        print("Data Shape:", X.shape, ", Label Shape:", y.shape)
    if info >= 2:
        print(X, y, sep= '\n')

    return X, y

from joblib import dump, load

def save_model(model, model_name: str) -> None:
    """
    儲存模型, 將模型儲存為 .joblib 檔案

    Args:
        model (object): 要儲存的模型
        model_name (str): 模型名稱
    """

    # 設定模型儲存路徑, 路徑 .Data/TrainedModels/{ModelName}_Model.joblib
    dir_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(dir_path, "Data", "TrainedModels", model_name + "_Model.joblib")

    # 使用設定路徑儲存模型
    dump(model, model_path)

    # 顯示儲存路徑
    print(f"Storing model to {model_path}")

    return

def load_model(model_name: str) -> object:
    """
    載入模型, 將模型載入為指定的模型物件

    Args:
        model_name (str): 模型名稱
    Returns:
        object: 載入的模型
    Notes:
        載入路徑為 .Data/TrainedModels/{ModelName}_Model.joblib
    Example:
        model = load_model("KMeans_2")
    """

    # 設定模型載入路徑, 路徑 .Data/TrainedModels/{ModelName}_Model.joblib
    dir_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(dir_path, "Data", "TrainedModels", model_name + "_Model.joblib")

    # 顯示載入路徑
    print(f"Loading model from {model_path}")
    
    # 使用設定路徑載入模型並回傳
    return load(model_path)

from sklearn.preprocessing import StandardScaler

def save_scaler(scaler, scaler_name: str) -> None:
    """
    儲存標準化器, 將標準化器儲存為 .joblib 檔案

    Args:
        scaler (StandardScaler): 要儲存的標準化器
        scaler_name (str): 標準化器名稱
    """

    # 設定標準化器儲存路徑, 路徑 .Data/TrainedModels/{ScalerName}_Scaler.joblib
    dir_path = os.path.dirname(os.path.abspath(__file__))
    scaler_path = os.path.join(dir_path, "Data", "TrainedModels", scaler_name + "_Scaler.joblib")

    # 使用設定路徑儲存標準化器
    dump(scaler, scaler_path)

    # 顯示儲存路徑
    print(f"Storing scaler to {scaler_path}")

    return

def load_scaler(scaler_name: str) -> StandardScaler:
    """
    載入標準化器, 將標準化器載入為 StandardScaler 物件
    
    Args:
        scaler_name (str): 標準化器名稱
    Returns:
        StandardScaler: 載入的標準化器
    Notes:
        載入路徑為 .Data/TrainedModels/{ScalerName}_Scaler.joblib
    Example:
        scaler = load_scaler("KMeans_2")
    """

    # 設定標準化器載入路徑, 路徑 .Data/TrainedModels/{ScalerName}_Scaler.joblib
    dir_path = os.path.dirname(os.path.abspath(__file__))
    scaler_path = os.path.join(dir_path, "Data", "TrainedModels", scaler_name + "_Scaler.joblib")

    # 顯示載入路徑
    print(f"Loading scaler from {scaler_path}")

    # 使用設定路徑載入標準化器並回傳
    return load(scaler_path)