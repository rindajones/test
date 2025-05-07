
# 時系列異常検知のための Exploratory Data Analysis (EDA) 

### 本書は補足、なぜなら：
### ** 予測モデルの構築以前に EDA は必須！！ **
本書は時系列データに対して実施した「基本的 EDA」。対象データは適当に作成した(`your_timeseries.csv`)で、"Normal" "Anomaly"のラベル付き。

## 1. データ

```python
import pandas as pd

# Load the CSV file
df = pd.read_csv("your_timeseries.csv")
df.head()
```
```text
  series_id  time    value     label
0  Normal_0    0   -0.127027   Normal
1  Normal_0    1    0.221224   Normal
2  Normal_0    2    0.120171   Normal
3  Normal_0    3    0.628080   Normal
4  Normal_0    4    0.477429   Normal
```

---

## 2. 正常／異常の分布

```python
df['label'].value_counts()
```
```text
label
Normal     500
Anomaly    500
Name: count, dtype: int64
```
```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.countplot(x='label', data=df)
plt.title("Label Distribution")
#plt.savefig("image/label_disribution.png", dpi=300, bbox_inches='tight')
plt.show()
```
![ラベル分布](./image/label_disribution.png "ラベル分布")

```python
df.describe()
```
```text
            time        value
count  1000.000000  1000.000000
mean     49.500000     0.149375
std      28.880514     0.963354
min       0.000000    -1.296246
25%      24.750000    -0.675529
50%      49.500000     0.080199
75%      74.250000     0.781595
max      99.000000     3.597136
```

---

## 3. 正常／異常 信号のサンプル波形

```python
import numpy as np

normal_example = df[df['series_id'] == 'Normal_0']['value'].values
anomaly_example = df[df['series_id'] == 'Anomaly_0']['value'].values

plt.figure(figsize=(10, 4))
plt.plot(normal_example, label='Normal')
plt.title("Example: Normal Signal")
plt.legend()
#plt.savefig("image/signal_normal.png", dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(10, 4))
plt.plot(anomaly_example, label='Anomaly', color='orange')
plt.title("Example: Anomalous Signal")
plt.legend()
#plt.savefig("image/signal_anomaly.png", dpi=300, bbox_inches='tight')
plt.show()
```
![正常シグナル](./image/signal_normal.png "正常シグナル")
![異常シグナル](./image/signal_anomaly.png "異常シグナル")

---

## 4. 信号長の分布（Signal Length Distribution）

```python
df['length'] = df['series_id'].apply(len)

sns.histplot(df['length'], bins=20, kde=False)
plt.title("Signal Length Distribution")
plt.xlabel("Length")
plt.ylabel("Count")
#plt.savefig("image/signal_length_distribution.png", dpi=300, bbox_inches='tight')
plt.show()
```
![信号長の分布](./image/signal_length_distribution.png "信号長の分布")


---

## 5. 要約統計量（Summary Statistics）

```python
import seaborn as sns
import matplotlib.pyplot as plt

df['mean'] = df.groupby('series_id')['value'].transform('mean')
df['std'] = df.groupby('series_id')['value'].transform('std')

# mean（ラベルごとの平均値の分布）
plt.figure(figsize=(6, 4))
sns.boxplot(x='label', y='mean', data=df)
plt.title("Mean by Label")
plt.tight_layout()
#plt.savefig("image/mean_by_label.png", dpi=300, bbox_inches='tight')
plt.show()

# std（ラベルごとの標準偏差の分布）
plt.figure(figsize=(6, 4))
sns.boxplot(x='label', y='std', data=df)
plt.title("Standard Deviation by Label")
plt.tight_layout()
#plt.savefig("image/std_by_label.png", dpi=300, bbox_inches='tight')
plt.show()
```
![ラベル毎の平均値の分布](./image/mean_by_label.png "ラベル毎の平均値の分布")
![ラベル毎の標準偏差の分布](./image/std_by_label.png "ラベル毎の標準偏差の分布")


---

## まとめ
``` text
今回の EDA：
 • ラベルのバランス
 • 信号の構造
 • クラスごとの統計的な傾向

これらの知見は、前処理やモデル設計の方針を決める際の指針となる。
```

### 現状のデータの単純さ

| 特徴           | 現在の内容                                      | コメント                                |
|----------------|--------------------------------------------------|------------------------------------------|
| 平均 (mean)    | Normal:　約 0.0<br>Anomaly: 約 0.3              | ラベルごとに平均が固定で差が大きい      |
| 標準偏差 (std) | Normal:　約 0.7<br>Anomaly: 約 1.15             | 異常の方が明らかにバラツキが大きい      |
| 長さ           | 8 or 9 で固定                                   | 長さによる検出要素はほぼない            |
| ノイズ         | 弱めに制御                                      | 複雑な外乱がない                         |
| 異常の種類     | 1種類のみ（平均と分散が異なる波形）             | 異常の多様性に欠ける                    |


> **補足（重要）**  
> 上記のように今回のデータは、異常と正常の違いが統計的に非常に単純。現実のデータでここまで明確な差が見られることは稀（ほぼ皆無）。
> 本書は、EDA がモデル構築前に不可欠なことの主張したもの。
---

### 参考：擬似データ作成
```python
# import pandas as pd
# import numpy as np

# # データ生成パラメータ
# num_series = 1000
# series_length_choices = [8, 9]
# normal_ratio = 0.5
# num_normal = int(num_series * normal_ratio)
# num_anomaly = num_series - num_normal

# # 1つの信号を生成する関数
# def generate_signal(label):
#     length = np.random.choice(series_length_choices)
#     if label == "Normal":
#         signal = np.random.normal(loc=0.0, scale=0.7, size=length)
#     else:
#         signal = np.random.normal(loc=0.3, scale=1.15, size=length)
#     return signal

# # 各信号をデータフレームに追加
# records = []
# for i in range(num_normal):
#     signal = generate_signal("Normal")
#     for t, value in enumerate(signal):
#         records.append({
#             "series_id": f"Normal_{i}",
#             "time": t,
#             "value": value,
#             "label": "Normal"
#         })

# for i in range(num_anomaly):
#     signal = generate_signal("Anomaly")
#     for t, value in enumerate(signal):
#         records.append({
#             "series_id": f"Anomaly_{i}",
#             "time": t,
#             "value": value,
#             "label": "Anomaly"
#         })

# # DataFrame化
# df = pd.DataFrame(records)

# # CSVとして保存
# csv_path = "./your_timeseries2.csv"
# df.to_csv(csv_path, index=False)
```
---