from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from Models import _LoadSave as LoadSave

X, y = LoadSave.load_dataset(1)

# 數據標準化
X_flatten = X.reshape(X.shape[0], -1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flatten)

# 隨機森林分類器
rfc = RandomForestClassifier(n_estimators=100,          # 隨機森林樹的數量
                             random_state=0,            # 隨機種子
                             max_depth=4,               # 樹的最大深度
                             criterion='gini',          # 分類標準
                             class_weight='balanced',   # 類別權重
                             n_jobs=-1,                 # 使用所有可用的 CPU 核心
                             verbose=1,                 # 輸出詳細信息
                             min_samples_split=5,       # 最小樣本分割數
                             min_samples_leaf=2,        # 最小樣本葉子數
                             max_features='sqrt',       # 最大特徵數
                             oob_score=True,            # 開放袋外評分 (可用._oob_score_來獲取)
                             max_samples=0.8,           # 最大樣本數
                             ccp_alpha=0.01)            # 代價複雜度剪枝參數

# 訓練模型
rfc.fit(X_scaled, y)

# 查看整個森林的特徵重要性
pos = ["x", "y", "z"]
importances = rfc.feature_importances_
for name, importance in zip(range(63), importances):
    print(f"{name//3}_{pos[name%3]}: {importance}")

# 獲取模型的袋外評分
oob_score = rfc.oob_score_
print(f"袋外評分: {oob_score:.4f}")

# 儲存模型和標準化器
n_estimators = 100
LoadSave.save_model(rfc, f"RandomForest_{n_estimators}")
LoadSave.save_scaler(scaler, f"RandomForest_{n_estimators}")