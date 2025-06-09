###############################################
#
# Isolation Forest
#
# 実装：scikit-learn
# |メソッド|値の意味|備考|
# |---|---|---
# |predict(X)|1=正常, -1=異常|2値分類のみ|
# |decision_function(X)|小さいほど異常|正常なら 0.1～0.5前後|
# |-decision_function(X)（推奨）|大きいほど異常|可視化に便利|
#
###############################################

###
## 1：仮想データの作成（5変数 × 時系列）

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# パラメータ
np.random.seed(42)
length = 1000  # タイムステップ数
anomaly_range = (600, 700)  # 異常期間

# 正常データ：sin波＋ノイズ
t = np.linspace(0, 20*np.pi, length)
data = {
    '電流値': np.sin(t) + 0.1*np.random.randn(length),
    '回転数': np.cos(t) + 0.1*np.random.randn(length),
    '音': 0.5*np.sin(2*t) + 0.1*np.random.randn(length),
    '振動': 0.5*np.cos(0.5*t) + 0.1*np.random.randn(length),
    '温度': 25 + 0.2*np.sin(0.1*t) + 0.1*np.random.randn(length),
}
df = pd.DataFrame(data)

# 異常挿入：ノイズを加える
for col in df.columns:
    df.loc[anomaly_range[0]:anomaly_range[1], col] += np.random.normal(0, 3, anomaly_range[1] - anomaly_range[0] + 1)

###
## 2：スライディングウィンドウで特徴ベクトル化

from sklearn.preprocessing import StandardScaler

# パラメータ
window_size = 10
X = []

# ウィンドウごとのベクトル化（flatten）
for i in range(len(df) - window_size):
    window = df.iloc[i:i+window_size].values.flatten()
    X.append(window)

X = np.array(X)

# スケーリング
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

###
## 3：Isolation Forest による異常スコア
from sklearn.ensemble import IsolationForest

# 学習＆スコア出力
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_scaled)
scores = -model.decision_function(X_scaled)  # 高いほど異常
                                             # 「大きいほど異常」に変換、解釈や可視化が直感的.

# スコアを元の時系列長に戻す（中央位置にマッピング）
score_series = np.zeros(len(df))
for i in range(len(scores)):
    center = i + window_size // 2
    score_series[center] = max(score_series[center], scores[i])


###
## 4：しきい値で異常区間を抽出＆可視化
# スコアのしきい値
threshold = np.percentile(score_series, 95)  # 上位5%を異常と定義
anomalies = score_series > threshold

# 可視化
plt.figure(figsize=(12, 6))
plt.plot(score_series, label='Anomaly Score')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.fill_between(range(len(score_series)), 0, 1, where=anomalies, transform=plt.gca().get_xaxis_transform(), color='red', alpha=0.2, label='Detected Anomaly')
#plt.title("時系列異常スコアと検出区間 (Isolation Forest)")
plt.title("Isolation Forest: Time Series Anomaly Scores and Detection Intervals")
plt.xlabel("Time")
plt.ylabel("Anomaly Score")
plt.legend()
plt.tight_layout()
plt.show()

# 可視化して確認しながら、段階的に最適なthresholdを調整。
# 「異常スコアの分布」と「何個が異常になるか」を数値で見て調整。
for p in [90, 95, 97, 99]:
    threshold = np.percentile(scores, p)
    print(f"Percentile {p}: threshold={threshold:.3f}, Anomalies={np.sum(scores > threshold)}")


###############################################
#
# One-class SVM
#
# チューニングポイント
# |パラメータ|意味|よくある設定|
# |---|---|---
# |nu|異常とみなす最大割合|0.01 ~ 0.1|
# |gamma|RBFカーネルのスケール|auto or 1/n_features|
#
###############################################

###
## 1. データ準備

# 既に df（1000ステップ, 5変数）と anomaly_range がある前提
# スライディングウィンドウ
window_size = 10
X = []

for i in range(len(df) - window_size):
    window = df.iloc[i:i+window_size].values.flatten()
    X.append(window)

X = np.array(X)

# 標準化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

###
## 2：One-Class SVM モデル構築・スコア計算
from sklearn.svm import OneClassSVM

# モデル定義：RBFカーネル、νは異常とする割合の上限（デフォルトは0.5）
model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)
model.fit(X_scaled)

# decision_function: 正常ほど大きく、異常は小さくなる
scores = -model.decision_function(X_scaled)  # 高いほど異常に変換

###
## 3：スコアを時系列に復元（中央マッピング）
score_series = np.zeros(len(df))
for i in range(len(scores)):
    center = i + window_size // 2
    score_series[center] = max(score_series[center], scores[i])

###
## 4：しきい値で異常検出＋プロット
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d

# スムージング
smoothed = uniform_filter1d(score_series, size=5)

# しきい値：上位5%のスコアを異常とみなす
threshold = np.percentile(smoothed, 95)
anomalies = smoothed > threshold

# 可視化
plt.figure(figsize=(12, 6))
plt.plot(smoothed, label='Anomaly Score (smoothed)')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.fill_between(range(len(score_series)), 0, 1, where=anomalies, transform=plt.gca().get_xaxis_transform(), color='red', alpha=0.2, label='Detected Anomaly')
#plt.title("One-Class SVM による異常スコアと検出区間")
plt.title("One-Class SVM: Time Series Anomaly Scores and Detection Intervals")
plt.xlabel("Time")
plt.ylabel("Anomaly Score")
plt.legend()
plt.tight_layout()
plt.show()

#########
# Isolation Forest と One-Class SVM の出力結果の違いの要因
#
# |要因|内容|
# |---|---|
# |スコアの計算方法|Isolation Forest vs One-Class SVM のスコアの定義・分布が違う|
# |スコアのスケール|Isolation Forestはスコアが0〜0.15程度、SVMは非常に小さいスコア（~0.0004）|
# |しきい値の決め方（percentile）|両方とも percentile 95 を使っていても、スコアの分布形が異なるため、結果的に異常と判定される時間範囲がズレる|
#


###############################################
#
# Local Outlier Factor（LOF）
#
# チューニングポイント
# |パラメータ|説明|よく使う設定|
# |---|---|---|
# |n_neighbors|局所近傍のサイズ。小さすぎるとノイズに敏感、大きすぎると異常をぼかす|10〜50程度|
# |contamination|異常割合の目安（しきい値推定に使用）|0.01〜0.1|
#
###############################################
###
## 1：スライディングウィンドウ
from sklearn.preprocessing import StandardScaler

window_size = 10
X = []
for i in range(len(df) - window_size):
    window = df.iloc[i:i+window_size].values.flatten()
    X.append(window)

X = np.array(X)

# スケーリング
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

###
##  2：LOF モデルで異常スコア算出
from sklearn.neighbors import LocalOutlierFactor

# LOFモデル（novelty=Falseは教師なしモード、スコアを取り出すには fit_predict 後に negative_outlier_factor_ を使用）
model = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
y_pred = model.fit_predict(X_scaled)
scores = -model.negative_outlier_factor_  # スコアを「高いほど異常」に変換


###
## 3：スコアを時系列に復元・スムージング
import numpy as np
from scipy.ndimage import uniform_filter1d

score_series = np.zeros(len(df))
for i in range(len(scores)):
    center = i + window_size // 2
    score_series[center] = max(score_series[center], scores[i])

smoothed = uniform_filter1d(score_series, size=5)

###
## 4：しきい値適用・異常範囲の可視化
import matplotlib.pyplot as plt

threshold = np.percentile(smoothed, 95)
anomalies = smoothed > threshold

plt.figure(figsize=(12, 6))
plt.plot(smoothed, label='Anomaly Score (smoothed)')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.fill_between(range(len(score_series)), 0, 1, where=anomalies, transform=plt.gca().get_xaxis_transform(), color='red', alpha=0.2, label='Detected Anomaly')
#plt.title("LOF による異常スコアと検出区間")
plt.title("LOF: Time Series Anomaly Scores and Detection Intervals")
plt.xlabel("Time")
plt.ylabel("Anomaly Score")
plt.legend()
plt.tight_layout()
plt.show()

####　評価方法 #################################
#
# 1. スコア単体の比較（教師なし的）
# |指標|説明|
# |---|---|
# |スコア分布の分離度|正常と異常でスコア分布がどれだけ分かれているか（ヒストグラムやKLD等）|
# |ROC Curve & AUC|if ground truthがあるならスコア vs 異常/正常ラベルで ROC-AUC を計算|
# |PR Curve & AUC|異常が稀な場合は ROCよりPR曲線が適切|
#
# ＊*異常区間の Ground Truth が部分的でもあると良い**
#
# 2. 区間レベルでの比較（実務向き）
# |指標|説明|
# |---|---|
# |検出率（Recall）|真の異常区間が1つでも検出されていればOKとする|
# |過検知率（False Positive Rate）|正常区間を異常と誤って判定した割合|
# |平均検出遅延|異常発生から検出までの時間|
# |区間IoU (Intersection over Union)|検出区間と真の異常区間のオーバーラップを測定|
# |Anomaly Range-Based Metrics|NAB Score など：連続異常の範囲を考慮したF1的スコア|
#
###############################################

### 結論！！ ###
#
# 「教師なし」のデータに対して、モデル同士の評価は「不自然」。
# ここからも「教師なしモデルの構築の難しさ」が分かる。-> なめんなよ！！(笑)
#

# これら三つの手法で、同じデータに対して「可能な限り同じ結果にする」
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




