# 再実行: 疑似データとウィンドウ処理（セッションリセット後の再定義）
import numpy as np
import pandas as pd

# 疑似データ設定
sampling_rate = 10  # 10Hz
duration_sec = 180  # 3分
n_samples = sampling_rate * duration_sec
time = np.arange(n_samples) / sampling_rate

# 疑似異常区間（例：60〜75秒、140〜155秒）
anomaly_periods = [(60, 75), (140, 155)]

# 正常な信号（緩やかな周期変動＋ノイズ）
def generate_normal_signal(base, noise=0.05):
    return base + noise * np.random.randn(len(base))

# 異常な信号（スパイク＋ノイズ）
def generate_abnormal_signal(base, noise=0.05):
    signal = base + noise * np.random.randn(len(base))
    for start, end in anomaly_periods:
        idx_start, idx_end = int(start * sampling_rate), int(end * sampling_rate)
        signal[idx_start:idx_end] += np.random.uniform(1.0, 2.0, idx_end - idx_start)
    return signal

# 4変数の疑似時系列データ
base_wave = np.sin(2 * np.pi * 0.1 * time)
data = pd.DataFrame({
    'time': time,
    'current': generate_abnormal_signal(base_wave),
    'rpm': generate_abnormal_signal(base_wave + 0.5),
    'sound': generate_abnormal_signal(base_wave + 1.0),
    'vibration': generate_abnormal_signal(base_wave + 1.5),
})

# ウィンドウ設定（3秒ごと、1秒ステップ）
window_size = 3 * sampling_rate  # 3秒
step_size = 1 * sampling_rate    # 1秒
windows = []
labels = []

for start in range(0, len(data) - window_size + 1, step_size):
    end = start + window_size
    window = data.iloc[start:end]
    
    # ウィンドウ中心時刻が異常区間に含まれていれば「異常」とする
    center_time = window['time'].iloc[len(window) // 2]
    is_anomaly = any(start_sec <= center_time <= end_sec for start_sec, end_sec in anomaly_periods)
    
    # 特徴量抽出
    feature = []
    for col in ['current', 'rpm', 'sound', 'vibration']:
        feature.extend([
            window[col].mean(),
            window[col].std(),
            window[col].min(),
            window[col].max()
        ])
    windows.append(feature)
    labels.append(int(is_anomaly))

# データフレーム化
X_windows = pd.DataFrame(windows, columns=[
    f"{col}_{stat}"
    for col in ['current', 'rpm', 'sound', 'vibration']
    for stat in ['mean', 'std', 'min', 'max']
])
y_windows = pd.Series(labels, name='label')

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# データ分割
X_train, X_test, y_train, y_test = train_test_split(X_windows, y_windows, test_size=0.25, random_state=42)

# スケーリング
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# モデル学習（RandomForest）
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_scaled, y_train)

# 予測
y_pred = clf.predict(X_test_scaled)

# 評価
report = classification_report(y_test, y_pred, output_dict=True)
conf_matrix = confusion_matrix(y_test, y_pred)
report_df = pd.DataFrame(report).T
conf_matrix_df = pd.DataFrame(conf_matrix, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

print(conf_matrix)

from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier

# XGBoost
xgb_model = XGBClassifier(eval_metric='logloss', use_label_encoder=False, verbosity=0, random_state=42)
xgb_model.fit(X_train_scaled, y_train)
y_pred_xgb = xgb_model.predict(X_test_scaled)
report_xgb = classification_report(y_test, y_pred_xgb, output_dict=True)
conf_matrix_xgb = confusion_matrix(y_test, y_pred_xgb)
report_xgb_df = pd.DataFrame(report_xgb).T
conf_matrix_xgb_df = pd.DataFrame(conf_matrix_xgb, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

# MLP
mlp_model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
mlp_model.fit(X_train_scaled, y_train)
y_pred_mlp = mlp_model.predict(X_test_scaled)
report_mlp = classification_report(y_test, y_pred_mlp, output_dict=True)
conf_matrix_mlp = confusion_matrix(y_test, y_pred_mlp)
report_mlp_df = pd.DataFrame(report_mlp).T
conf_matrix_mlp_df = pd.DataFrame(conf_matrix_mlp, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

print(conf_matrix_mlp_df)