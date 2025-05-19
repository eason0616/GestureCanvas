import os
import sys
import numpy as np
import seaborn as sns
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import make_scorer, f1_score, accuracy_score, classification_report, confusion_matrix

from sklearn.preprocessing import LabelEncoder


parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(parent_path)
from Models import _LoadSave as LoadSave

dir_path = os.path.dirname(os.path.abspath(__file__))
np.set_printoptions(suppress=True)

X, y = LoadSave.load_dataset(1)
X_flatten = X.reshape(X.shape[0], -1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flatten)
print(X_flatten.shape)

#print(data_flatten)

# 資料分割
X_train, X_test, y_train_original, y_test_original = train_test_split(
    X_flatten, y, test_size=0.2, random_state=1, stratify=y
)

le = LabelEncoder()
le.fit(y_train_original)
y_train = le.transform(y_train_original)
y_test = le.transform(y_test_original)
print(le.classes_)

# 標準化
pipe_svc = make_pipeline(scaler, SVC(random_state=1))

pipe_svc.fit(X_train, y_train)
y_pred = pipe_svc.predict(X_test)

# 繪製混淆矩陣
def plot_confusion_matrix(y_true, y_pred, class_names=None):
    cm = confusion_matrix(y_true, y_pred)
    
    # 創建漂亮的混淆矩陣圖
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names if class_names else np.unique(y_true),
                yticklabels=class_names if class_names else np.unique(y_true))
    plt.xlabel('Predict')
    plt.ylabel('Answer')
    plt.title('Confusion_matrix')
    
    # 計算每個類別的準確率
    class_accuracy = cm.diagonal() / cm.sum(axis=1)
    
    # 打印每個類別的準確率
    print("\n各類別準確率:")
    for i, acc in enumerate(class_accuracy):
        class_name = class_names[i] if class_names else f"Gesture {i}"
        print(f"{class_name}: {acc:.4f} ({acc*100:.2f}%)")
    
    plt.savefig("confusion_matrix.png")
    plt.tight_layout()
    
    # 避免在Jupyter notebook中顯示圖形而導致警告
    try:
        plt.show()
    except:
        plt.close()
    
    return cm

# 定義類別名稱（依據您的資料集調整）
class_names = [f"Gesture {i}" for i in np.unique(y_test)]

# 進行網格搜索調優
# 使用多類別的 F1 評分方式，避免 pos_label 警告
scorer = make_scorer(f1_score, average='macro', zero_division=0)

c_gamma_range = [0.01, 0.1, 1.0, 10.0]

param_grid = [{'svc__C': c_gamma_range,
               'svc__kernel': ['linear']},
              {'svc__C': c_gamma_range,
               'svc__gamma': c_gamma_range,
               'svc__kernel': ['rbf']}]

# 使用 StratifiedKFold 確保每個折疊都有所有類別的樣本
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

gs = GridSearchCV(estimator=pipe_svc,
                  param_grid=param_grid,
                  scoring=scorer,
                  cv=skf,  # 使用分層交叉驗證
                  n_jobs=-1,
                  verbose=0)  # 減少輸出的訊息
gs = gs.fit(X_train, y_train)
print("\n網格搜索最佳分數:", gs.best_score_)
print("最佳參數:", gs.best_params_)

# 使用最佳模型進行預測
SVC_model = gs.best_estimator_
best_y_pred = SVC_model.predict(X_test)

n_clusters = 1
scaler = SVC_model.named_steps['standardscaler']

LoadSave.save_model(SVC_model, f"SVC_{n_clusters}")
LoadSave.save_scaler(scaler, f"SVC_{n_clusters}")

# 顯示最佳模型的準確率和分類報告
best_accuracy = accuracy_score(y_test, best_y_pred)
print(f"\n最佳模型準確率: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
print("\n最佳模型分類報告:")
print(classification_report(y_test, best_y_pred))

# 繪製最佳模型的混淆矩陣
print("\n最佳模型混淆矩陣:")
best_cm = plot_confusion_matrix(y_test, best_y_pred, class_names)