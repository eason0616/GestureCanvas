import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from ModelTraining import LoadSave

dir_path = os.path.dirname(os.path.abspath(__file__))
np.set_printoptions(suppress=True)

X, y = LoadSave.load_dataset(1)
X_flatten = X.reshape(X.shape[0], -1)
print(X_flatten.shape)
# print(data_flatten)

# 標準化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flatten)
print(X_scaled.shape)

n_clusters = 2
kmeans = KMeans(n_clusters= n_clusters, random_state= 0)
y_pred = kmeans.fit_predict(X_scaled)

print(y_pred)
print(kmeans.cluster_centers_)

LoadSave.save_model(kmeans, f"KMeans_{n_clusters}")
LoadSave.save_scaler(scaler, f"KMeans_{n_clusters}")

# 使用 PCA 將數據降至 2D 進行可視化
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
print(X_pca.shape)

plt.figure(figsize=(6, 5))

# 繪製聚類結果
plt.subplot(111)
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c= y_pred, cmap= 'viridis')
plt.title('K-Means cluster centers')
plt.colorbar(scatter)

# 繪製實際標籤
# plt.subplot(122)
# scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], cmap= 'viridis')
# plt.title('實際標籤')
# plt.colorbar(scatter)

plt.tight_layout()
plt.show()
