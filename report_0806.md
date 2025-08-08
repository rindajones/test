## 追記
YOLOモデルを断念（理由：主には、ラズパイでの動作が困難）。
複数のセグメンテーションモデルを試して、あるモデルを学習させてラズパイで実行した結果。**400枚の画像を推論、クラス数「８」**

**Mac OS**
```
🟢 全体で検出されたクラスID: [0, 1, 2, 3, 4, 5, 6, 7]

クラスIDごとの検出回数（画素単位ではなく画像単位）:
  ID 0: 400 枚
  ID 1: 400 枚
  ID 2: 303 枚
  ID 3: 393 枚
  ID 4: 400 枚
  ID 5: 400 枚
  ID 6: 208 枚
  ID 7: 400 枚

⏱ 平均推論時間: 0.117 秒/枚 （8.58 FPS）
```

**Raspberry Pi 5**
```
🟢 全体で検出されたクラスID: [0, 1, 2, 3, 4, 5, 6, 7]

クラスIDごとの検出回数（画素単位ではなく画像単位）:
  ID 0: 400 枚
  ID 1: 400 枚
  ID 2: 303 枚
  ID 3: 393 枚
  ID 4: 400 枚
  ID 5: 400 枚
  ID 6: 208 枚
  ID 7: 400 枚

⏱ 平均推論時間: 0.831 秒/枚 （1.20 FPS）
```

**注意**
ラズパイでの推論は「プロセス数を１に制限」など、最小限のリソースで実行。一方 Mac ではリソース制限なし。


|指標|Mac (M3)|Raspberry Pi 5|
|---|---|---
|検出ID一覧|[0, 1, 2, 3, 4, 5, 6, 7]|✅ 同じ|
|推論サイズ|512x512|✅ 同じ|
|枚数|400枚|✅ 同じ|
|平均推論時間|0.117 秒/枚（8.58 FPS）|0.831 秒/枚（1.20 FPS）|
|温度上昇|-|48°C以下（冷却効果あり）|

**課題**
ラズパイでの推論速度を 2, 3 FPS（現在の2,3倍の速度）にしたい。モデルの量子化 INT8 を検討。

---
<div style="page-break-before:always"></div>

## Raspberry Pi 5 設定

### 1. 確認済み事項

- **モニター(MDMI)**
  OS初期設定時に、モニターへの出力確認。

- **カメラ**
  静止画、動画の撮影確認。
  ただし、Python コードからのカメラ操作未確認。

- **WiFi**
  ラップトップ端末からリモート接続して作業可能。

- **Pythonプログラム稼働環境**
 調査継続中：主にAIモデルの軽量化、高速化の環境調査。


### 2. 課題

### SDカードスロット故障

SDカードが読み込めない＝OSが起動しない。

**調べたところ**
SDカードスロットの使用は避けた方が良い、壊れやすい。
代わりにUSBスロット使用(USB3.0にすべき)。つまり USBリーダーが必要。

<div style="page-break-before:always"></div>

### 冷却ファン必須

Pi5になって高性能化しているが、発熱への配慮が必要。
冷却ファンは必須で、かつケースの「風通し」への配慮も必要。

**昔と今と...**
|比較対象|性能イメージ|コメント|
|---|---|---|
|昔のインテルノートPC|ほぼ同等|2013年頃のi7と同程度のCPU性能|
|Raspberry Pi 4|約2倍の性能向上|体感でも明らかに速い|

**Raspberry Pi 5 vs Sun Workstation（UltraSPARCシリーズ）**
|項目|Raspberry Pi 5|UltraSPARC II (400MHz)|
|---|---|---|
|発売年|2023年|約1997年|
|アーキテクチャ|Arm Cortex-A76 (64bit RISC)|SPARC V9 (64bit RISC)|
|コア数|4コア|1コア|
|クロック周波数|2.4GHz|400MHz|
|メモリ|4GB / 8GB LPDDR4X|最大2GB ECC SDRAM|
|GPU|VideoCore VII|なし（別チップ）|
|消費電力（ピーク）|約8W（全体）|約25〜35W（CPU単体）|
|発熱傾向|高負荷時に80°C超（要冷却）|発熱大・ファン必須|
|サイズ|名刺サイズ（85.6×56.5mm）|フルサイズサーバー基板|
|価格帯|約1万円|当時数十万円以上|
|OS|Linux, Raspberry Pi OS ほか|Solaris,  Linux (SPARC版)|

個人的にRaspberry Pi 5と冷却ファンを購入して実験中、SDカードも高速版。

<table>
<tr>
<td><img src='./images/mine.JPG' width=250></td>
<td><img src='./images/heat_sink.png' width=250></td>
</tr>
</table>

製品説明：[Amazon.co.jp](https://www.amazon.co.jp/dp/B0CNT5G91H?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)


<div style="page-break-before:always"></div>


### 電源ケーブルの間違い

購入間違い（両方ともUSB-Cが必要）で買い直し。ケーブルの長さは？

## 総合的に

ドローン搭載に向けた Raspberry Pi の格納方法を要確認。
特に、運用を想定した格納になっているか要確認。
例えば、開発初期は頻繁にモニター接続する可能性あり（WiFiが使えると楽）。

## 案
Amazonで「冷却ファン付き」「通気穴あり」「USB/CSIアクセス可」なやつを購入。**ドローン取り付けの部分だけを設計＆製造**する。


例えば：[Amazon.co.jp](https://www.amazon.co.jp/dp/B0CMZ9PCXZ/ref=sspa_dk_detail_1?psc=1&pd_rd_i=B0CMZ9PCXZ&pd_rd_w=wPeK7&content-id=amzn1.sym.f293be60-50b7-49bc-95e8-931faf86ed1e&pf_rd_p=f293be60-50b7-49bc-95e8-931faf86ed1e&pf_rd_r=MBFKTVJR0F52N1JG0YG2&pd_rd_wg=ebBrl&pd_rd_r=8e2ca401-1c40-44e9-b977-07d8ede439d5&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw)

<img src='./images/case.png' width=400>

<div style="page-break-before:always"></div>

## Raspberry Pi とは
|年|出来事|
|---|---|
|2012年|初代Raspberry Pi Model B発売（価格は約35ドル）英国ケンブリッジのRaspberry Pi Foundationが「子どもたちにプログラミングを！」の理念で設立|
|2014年|Model B+ や A+ など改良版が登場、GPIOピンが40本に|
|2015年|Pi 2発売（クアッドコア化）、より多くのOSが対応可能に|
|2016年|Pi 3発売（Wi-Fi & Bluetooth搭載）→「完全な小型PC」へ|
|2019年|Pi 4発売（USB 3.0搭載、RAM最大8GB）→デスクトップ用途にも|
|2023年|Pi 5登場（PCIe対応、さらに高性能GPU）→AIにも本気！|
|今（2025年）|世界中で「教育」「IoT」「AI」など幅広く活用中！|

以下、ChatGPT調べ（笑）

🌍 少年少女たちの Raspberry Pi 発明 💡

1. 🎒 学校の出席管理システム（インド・14歳）
	•	顔認証とカードスキャンを組み合わせて、自動で出席を記録
	•	学校の先生が「点呼しなくていい！」と歓喜
	•	使用：Raspberry Pi + カメラ + Python + OpenCV

---

2. 🐱 猫自動給餌ロボット（アメリカ・13歳）
	•	ネコが近づくとセンサーで反応し、ごはんを出す！
	•	時間ごとのスケジュール管理付き
	•	使用：Raspberry Pi + サーボモーター + 超音波センサー

---

3. 🌡 火山地帯のセンサーネットワーク（インドネシア・15歳）
	•	地元の火山活動を監視するために、温度・ガス・振動センサーを搭載したネットワークを構築
	•	ラズパイでデータ収集し、ネット経由で警報を送信！

---

4. 🏠 スマートホーム管理パネル（フィリピン・12歳）
	•	家の照明やエアコン、カーテンをスマホや音声で操作可能
	•	自作GUIまで開発、両親が感激！
	•	使用：Raspberry Pi + Home Assistant + MQTT

---

5. 🚲 自転車盗難防止アラーム（フランス・14歳）
	•	ジャイロセンサーで異常検知→GPSで場所を通知
	•	SMSでオーナーに通知、近所にもアラーム音を鳴らす！
	•	使用：Raspberry Pi Zero + GSMモジュール + GPS

---
ChatGPT調べ、ここまで。

個人的には「当時のBASIC使うマイコン趣味」は「オタクの隠れ趣味」と思う。今の Raspberry Pi はネットの力も借りて「世界を変える開発環境」と言えるだろう、大袈裟じゃなくてね。😆


<div style="page-break-before:always"></div>

### 最新構成

**冷えピタシート**

<img src='./images/heat_seal.JPG' width=400>

このシートだけで通常 35度（通常60度）、AIモデルを実行しても「高々48度」（前掲）。

**ほぼ全部の構成**

<img src='./images/full.JPG' width=400>

**未設置**

- リアル無線通信 USBユニット
- データ保存用 USBユニット
- WiFi通信 USBユニット（内蔵 WiFi が屋外ふかの場合）