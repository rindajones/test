import numpy as np
import pandas as pd

# 仕様
sampling_rate = 10  # 10 Hz
duration_sec = 180  # 3 minutes
n_samples = sampling_rate * duration_sec

# 時間軸
time = np.arange(n_samples) / sampling_rate  # seconds

# 正常データ生成
def generate_normal_signal(base, noise_level=0.05):
    return base + noise_level * np.random.randn(n_samples)

# 異常データ生成（高周波ノイズ追加 or シフト orスパイク）
def generate_abnormal_signal(base, noise_level=0.05):
    signal = base + noise_level * np.random.randn(n_samples)
    spike_indices = np.random.choice(n_samples, size=int(n_samples * 0.02), replace=False)
    signal[spike_indices] += np.random.uniform(1.0, 2.0, size=spike_indices.shape)
    return signal

# 4変数 × 2クラス（正常・異常）
def generate_dataset():
    datasets = []
    labels = []
    for _ in range(50):  # 50個の正常サンプル
        base = np.sin(2 * np.pi * 0.1 * time)  # 緩やかな周期変動
        sample = {
            'current': generate_normal_signal(base),
            'rpm': generate_normal_signal(base + 0.5),
            'sound': generate_normal_signal(base + 1.0),
            'vibration': generate_normal_signal(base + 1.5)
        }
        datasets.append(pd.DataFrame(sample))
        labels.append(0)
    for _ in range(50):  # 50個の異常サンプル
        base = np.sin(2 * np.pi * 0.1 * time)
        sample = {
            'current': generate_abnormal_signal(base),
            'rpm': generate_abnormal_signal(base + 0.5),
            'sound': generate_abnormal_signal(base + 1.0),
            'vibration': generate_abnormal_signal(base + 1.5)
        }
        datasets.append(pd.DataFrame(sample))
        labels.append(1)
    return datasets, labels

datasets, labels = generate_dataset()

# 1つのサンプルの構造確認用
sample_df = datasets[0].copy()
sample_df['time_sec'] = time


# ラベル配列も作成（あとでウィンドウ集計に使用）
label_series = pd.Series(labels, name="label")

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

# 時系列をウィンドウ単位で特徴量要約（平均・分散・最大値・最小値）
def extract_features_from_df(df, window_size=30):  # 3秒ウィンドウ（10Hz×3）
    features = []
    for start in range(0, len(df), window_size):
        end = start + window_size
        window = df.iloc[start:end]
        if len(window) < window_size:
            continue
        stats = []
        for col in ['current', 'rpm', 'sound', 'vibration']:
            stats.extend([
                window[col].mean(),
                window[col].std(),
                window[col].min(),
                window[col].max()
            ])
        features.append(stats)
    return np.array(features).mean(axis=0)  # 各ウィンドウの統計量を平均して1ベクトルに要約

# 特徴量抽出
X = np.array([extract_features_from_df(df) for df in datasets])
y = np.array(labels)

# スケーリング
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 教師あり分類（RandomForest）
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
report = classification_report(y_test, y_pred, output_dict=True)
conf_matrix = confusion_matrix(y_test, y_pred)

# 結果を整形
report_df = pd.DataFrame(report).T
conf_matrix_df = pd.DataFrame(conf_matrix, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

print(report_df)
print(conf_matrix_df)


from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier

# XGBoost
#xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_model = XGBClassifier(eval_metric='logloss', random_state=42)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)

report_xgb = classification_report(y_test, y_pred_xgb, output_dict=True)
conf_matrix_xgb = confusion_matrix(y_test, y_pred_xgb)
report_xgb_df = pd.DataFrame(report_xgb).T
conf_matrix_xgb_df = pd.DataFrame(conf_matrix_xgb, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

# MLP
mlp_model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
mlp_model.fit(X_train, y_train)
y_pred_mlp = mlp_model.predict(X_test)

report_mlp = classification_report(y_test, y_pred_mlp, output_dict=True)
conf_matrix_mlp = confusion_matrix(y_test, y_pred_mlp)
report_mlp_df = pd.DataFrame(report_mlp).T
conf_matrix_mlp_df = pd.DataFrame(conf_matrix_mlp, index=["True Normal", "True Anomaly"], columns=["Pred Normal", "Pred Anomaly"])

print(conf_matrix_xgb_df)
print(conf_matrix_mlp_df)


print()
print('#######################################################')
print('## Under Review')
print('#######################################################')

from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import pandas as pd
import numpy as np

models = {
    'RandomForest': RandomForestClassifier(random_state=42),
    'XGBoost': XGBClassifier(eval_metric='logloss', use_label_encoder=False, verbosity=0, random_state=42),
    'MLP': MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
}

results = []
for name, model in models.items():
    f1_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='f1')
    results.append({
        'Model': name,
        'F1 Mean': np.mean(f1_scores),
        'F1 Std': np.std(f1_scores)
    })

print(pd.DataFrame(results))
