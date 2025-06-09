##################################################################
# 目的：これら三つの手法で、同じデータに対して「可能な限り同じ結果にする」
#
# 狙い：教師なし異常検知を、教師ありのように“合わせ込む"
# だがしかし：原理的には「近づける」ことは可能
#	　　完全に同じ出力にはならない（内部の異常の定義が異なるため）
#
# **「合わせ込み」の技術ポイント（＝調整可能なパラメータ）**
# |項目|調整内容|共通化による効果|
# |---|---|---|
# |ウィンドウサイズ|時系列ベクトルの長さ（例：10）|全手法で同一にする|
# |スケーリング|StandardScaler（Z-score正規化）|データ形状の一致|
# |スムージング幅|uniform_filter1d(size=n)|スパイク vs 区間を揃える|
# |異常スコアの反転|-score で「高いほど異常」に統一|可視化・判定整合性UP|
# |しきい値の方法|percentileベース（例：95%）|モデル間で“異常率”を揃える|
# |連続性のフィルタ|2連続以上のみ採用など|ノイズ除去で出力安定化|
#
#
# 結論：「異常の定義を後工程で揃えれば、異常区間の一致はかなり可能」
# 完全な一致は無理でも、運用上「見た目上は同じ」くらいにはできる
# 

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from scipy.ndimage import uniform_filter1d

# 再現性のための乱数固定
np.random.seed(42)

# 仮想時系列データの作成（5変数 × 1000ステップ）
length = 1000
anomaly_range = (600, 700)
t = np.linspace(0, 20 * np.pi, length)
df = pd.DataFrame({
    '電流値': np.sin(t) + 0.1 * np.random.randn(length),
    '回転数': np.cos(t) + 0.1 * np.random.randn(length),
    '音': 0.5 * np.sin(2 * t) + 0.1 * np.random.randn(length),
    '振動': 0.5 * np.cos(0.5 * t) + 0.1 * np.random.randn(length),
    '温度': 25 + 0.2 * np.sin(0.1 * t) + 0.1 * np.random.randn(length),
})

# 異常データ挿入
for col in df.columns:
    df.loc[anomaly_range[0]:anomaly_range[1], col] += np.random.normal(0, 3, anomaly_range[1] - anomaly_range[0] + 1)

# スライディングウィンドウ（共通処理）
window_size = 10
X = [df.iloc[i:i + window_size].values.flatten() for i in range(len(df) - window_size)]
X = np.array(X)

# スケーリング
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# モデルたちの構築
models = {
    'IsolationForest': IsolationForest(contamination=0.1, random_state=42),
    'OneClassSVM': OneClassSVM(kernel='rbf', gamma='auto', nu=0.1),
    'LOF': LocalOutlierFactor(n_neighbors=20, contamination=0.1)
}

# スコアを収集（すべて「高いほど異常」に統一）
scores_dict = {}

# Isolation Forest
iso_model = models['IsolationForest']
iso_model.fit(X_scaled)
scores_dict['IsolationForest'] = -iso_model.decision_function(X_scaled)

# One-Class SVM
svm_model = models['OneClassSVM']
svm_model.fit(X_scaled)
scores_dict['OneClassSVM'] = -svm_model.decision_function(X_scaled)

# LOF（fit_predictの後にスコア取得）
lof_model = models['LOF']
_ = lof_model.fit_predict(X_scaled)
scores_dict['LOF'] = -lof_model.negative_outlier_factor_

# 各スコアを 0〜1 に正規化、中心位置にマッピング、スムージング
score_df = pd.DataFrame({'time': np.arange(len(df))})

for key, scores in scores_dict.items():
    score_series = np.zeros(len(df))
    for i in range(len(scores)):
        center = i + window_size // 2
        score_series[center] = max(score_series[center], scores[i])
    # 0〜1に正規化
    norm_score = (score_series - np.min(score_series)) / (np.max(score_series) - np.min(score_series))
    # スムージング
    smoothed = uniform_filter1d(norm_score, size=5)
    score_df[key] = smoothed

# 共通しきい値（上位5%）を使って異常フラグを立てる
thresholds = {
    key: np.percentile(score_df[key], 95)
    for key in ['IsolationForest', 'OneClassSVM', 'LOF']
}

# 異常フラグ（bool配列）
for key in thresholds:
    score_df[f'{key}_anomaly'] = score_df[key] > thresholds[key]

# 異常区間の一致度評価（IoU）
true_range = set(range(600, 701))
iou_results = {}

for key in ['IsolationForest', 'OneClassSVM', 'LOF']:
    pred_range = set(score_df.index[score_df[f'{key}_anomaly']])
    intersection = len(true_range & pred_range)
    union = len(true_range | pred_range)
    iou = intersection / union
    iou_results[key] = iou

print(iou_results)

import matplotlib.pyplot as plt

# TypeError 対応：fill_between の引数を float にキャスト
plt.figure(figsize=(14, 8))

# 各スコアラインを描画
plt.plot(score_df['time'], score_df['IsolationForest'], label='Isolation Forest', alpha=0.7)
plt.plot(score_df['time'], score_df['OneClassSVM'], label='One-Class SVM', alpha=0.7)
plt.plot(score_df['time'], score_df['LOF'], label='LOF', alpha=0.7)

# Ground Truth 異常区間の影
plt.axvspan(600, 700, color='gray', alpha=0.2, label='True Anomaly Range')

# 各モデルの異常区間を半透明で塗る
for key, color in zip(['IsolationForest', 'OneClassSVM', 'LOF'], ['blue', 'green', 'orange']):
    anomaly_flags = score_df[f'{key}_anomaly'].astype(bool).values
    plt.fill_between(score_df['time'].values.astype(float), 0, 1, where=anomaly_flags,
                     color=color, alpha=0.1, transform=plt.gca().get_xaxis_transform(),
                     label=f'{key} Detected')

#plt.title("異常スコアと検出区間の可視化（共通正規化・しきい値）")
plt.title("Common Normalization & Threshold: Time Series Anomaly Scores and Detection Intervals")
plt.xlabel("Time")
plt.ylabel("Normalized Anomaly Score")
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()