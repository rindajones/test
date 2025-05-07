
# 1D-CNN による異常検知フルワークフロー（Basic）

---
```python
# Python 3.11.11

# 注意 #
# 無視して良い警告を表示させないため。警告が見たい場合このセルは不要。
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all, 1 = info, 2 = warnings, 3 = errors only

import logging
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import tensorflow as tf
tf.get_logger().setLevel('ERROR')  # TensorFlowの retracing 警告なども抑制
```
---

## 1. 擬似データ生成と可視化

```python
import numpy as np
import matplotlib.pyplot as plt

# 注意 #
# 実行結果（結果の画像等）がそちらの環境での結果と同等になるようにseed を固定。
# 本来なら固定にする必要はない。
seed = 42

timesteps = 100
n_samples = 100

# Normal（sin波 + ノイズ）
X_normal = np.array([
    np.sin(np.linspace(0, 4 * np.pi, timesteps)) + np.random.normal(0, 0.1, timesteps)
    for _ in range(n_samples)
])

# Anomaly（sin波 + スパイク）
X_anomaly = np.array([
    np.sin(np.linspace(0, 4 * np.pi, timesteps)) + np.random.normal(0, 0.1, timesteps) +
    np.where((np.arange(timesteps) > 40) & (np.arange(timesteps) < 50), 3.0, 0.0)
    for _ in range(n_samples)
])

plt.figure(figsize=(12, 4))
for i in range(10):
    plt.plot(X_normal[i], color='blue', alpha=0.3)
    plt.plot(X_anomaly[i], color='red', alpha=0.3)
plt.title("Normal (blue) vs Anomaly (red) - Sample Series")
#plt.savefig("image/wave_plot.png", dpi=300, bbox_inches='tight')  # ← 保存処理
plt.show()
```
![学習データ](./image/wave_plot.png "学習データ")


---

## 2. データ結合と分割（学習/検証）

```python
from sklearn.model_selection import train_test_split

X = np.concatenate([X_normal, X_anomaly])
y = np.array([0]*n_samples + [1]*n_samples)

X = X[..., np.newaxis]  # CNN入力形式（3D）

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

---

## 3. 1D-CNN モデル構築と学習

```python
import tensorflow as tf
from tensorflow.keras import layers, models, Input

model = models.Sequential([
    Input(shape=(timesteps, 1)),  # ここで入力形状を定義
    layers.Conv1D(32, 3, activation='relu'),
    layers.MaxPooling1D(2),
    layers.Conv1D(64, 3, activation='relu'),
    layers.GlobalMaxPooling1D(),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_val, y_val))
model.save("cnn_anomaly_model.h5")
```

---

## 4. 学習済みモデルによる評価

```python
from sklearn.metrics import classification_report, confusion_matrix

y_pred_prob = model.predict(X_val)
y_pred = (y_pred_prob > 0.5).astype(int).flatten()

print(classification_report(y_val, y_pred))
print(confusion_matrix(y_val, y_pred))
```
```text
              precision    recall  f1-score   support

           0       1.00      1.00      1.00        20
           1       1.00      1.00      1.00        20

    accuracy                           1.00        40
   macro avg       1.00      1.00      1.00        40
weighted avg       1.00      1.00      1.00        40

[[20  0]
 [ 0 20]]
```

---

## 5. 未知のテストデータで推論

```python
model = tf.keras.models.load_model("cnn_anomaly_model.h5")

# テストデータ生成（Normal + Anomaly）
X_normal_test = np.array([
    np.sin(np.linspace(0, 4 * np.pi, timesteps)) + np.random.normal(0, 0.1, timesteps)
    for _ in range(10)
])

X_anomaly_test = np.array([
    np.sin(np.linspace(0, 4 * np.pi, timesteps)) + np.random.normal(0, 0.1, timesteps) +
    np.where((np.arange(timesteps) > 40) & (np.arange(timesteps) < 50), 3.0, 0.0)
    for _ in range(10)
])

X_test = np.concatenate([X_normal_test, X_anomaly_test])
y_test = np.array([0]*10 + [1]*10)
X_test = X_test[..., np.newaxis]

y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype(int).flatten()

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```
```text

              precision    recall  f1-score   support

           0       1.00      1.00      1.00        10
           1       1.00      1.00      1.00        10

    accuracy                           1.00        20
   macro avg       1.00      1.00      1.00        20
weighted avg       1.00      1.00      1.00        20

[[10  0]
 [ 0 10]]
```
# 最後に（重要）
```text
今回はモデルにとって非常に“優しい”条件下での検証です。現実のデータではこのような完璧な結果が出ることは稀（ほぼない）。
今後はデータの多様性やノイズなど現実的な状況も考慮する必要あり。
```

## 今後の取り組み（例）
```text
- 正常データのパターンをもっと豊富にして学習
- 異常のパターンのバリエーションを増やす
- より長い系列データでの学習／推論
```

---
