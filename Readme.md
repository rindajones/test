# 姿勢／位置の推定

### 目的
USB カメラからの画像入力を想定した、画像中の物体の姿勢／位置の推定に向けた実装テスト。

### 手法
推定対象を**Cube**として、**Cubeの一面に貼りつ付けた `ArUco` のマーカー**から推定。画像は Blender にて作成。

**⚠️ 注意**
実務では、推定する前に対象の**物体検知**を実施。推定は**その検知結果の BBox 範囲**で実施。

**補足**
本テストの精度は、実務よりは劣ると想定。その**理由：**
- `solvePnP` はカメラ画像を前提としているため、Blender 作成画像とのギャップは避けられない。
- 本テストでは `ArUco` の評価対象を画像全体としているが、実務では**検知後の BBox の範囲**。

**Blenderオブジェクト**
- カメラ：上空 17 m **Localtion:(0,0,17), Rotation:(0,0,0)**
- Cube：上空 5 m、一辺 1 m **Location:(0,0,5), Dimenstions:(1,1,1)**
<img src='image/Blender.png' width=500>
---
<div style="page-break-before:always"></div>

### Yaw, Pitch, Roll

<table>
<tr>
<td>(0,0,0)<img src='./cube_pose_sample/yaw_00.png' width=180></td>
<td>yaw=30°<img src='./cube_pose_sample/yaw_30.png' width=180></td>
<td>yaw=60°<img src='./cube_pose_sample/yaw_60.png' width=180></td>
</tr>
<tr>
<td></td>
<td>pitch=30°<img src='./cube_pose_sample/pitch_30.png' width=180></td>
<td>pitch=60°<img src='./cube_pose_sample/pitch_60.png' width=180></td>
</tr>
<tr>
<td></td>
<td>roll=30°<img src='./cube_pose_sample/roll_30.png' width=180></td>
<td>roll=60°<img src='./cube_pose_sample/roll_60.png' width=180></td>
</tr>
</table>

<img src='./image/maxresdefault.jpg' width=400>

[Pitch, Roll and Yaw in Orthodontics](https://www.youtube.com/watch?v=0Hl5bCgXsTs)

---
<div style="page-break-before:always"></div>

## 1. データ作成
```
% mkdir output
% blender cube_aruco.blend
```
**⚠️ 注意**
本スクリプト実行後に`.blend`ファイルを保存しないこと。スクリプトによって **Cube の位置情報等が破壊**されるため。

**姿勢・位置のランダム性**
- `yaw, pitch, roll: ±30° = ±np.pi/6`
- `x, y, z = (±3.0, ±3.0, 5.0)` 単位：m

Blender で **Scriping Run** `data_gen.py`

**出力** `./output/img_000.png` - `./output/img_049.png`
<table>
<tr>
<td><img src='./output/img_000.png' width=180></td>
<td><img src='./output/img_001.png' width=180></td>
<td><img src='./output/img_002.png' width=180></td>
</tr>
<tr>
<td><img src='./output/img_003.png' width=180></td>
<td><img src='./output/img_004.png' width=180></td>
<td><img src='./output/img_005.png' width=180></td>
</tr>
</table>

**Ground Truth**
**⚠️ 注意**：ワールド座標系（z=5.0 固定）
```
% head ./output/pose_data.json 
[
  {
    "file": "img_000.png",
    "x": -0.9105222084092857,
    "y": -2.78771332325708,
    "z": 5.0,
    "yaw": 21.74686560320192,
    "pitch": -23.129949019785915,
    "roll": -12.948167681586968
  },
  ```
---
<div style="page-break-before:always"></div>

## 2. 姿勢推定

**⚠️ 注意**
`solvePnP` はカメラ座標系、Ground Truth はワールド座標系のため、**Cube の位置をワールド座標系に変換**。

**⚠️ 注意**
カメラの**向きは真下**が前提。

```
% python estimate.py 
[WARNING] No marker found in output/img_020.png
[WARNING] No marker found in output/img_047.png
```
**推定結果** `estimated_pose.csv`
```
% head estimated_pose.csv 
filename,x_cube,y_cube,z_cube,yaw_cube,pitch_cube,roll_cube,x_ground,y_ground,z_ground,yaw_ground,pitch_ground,roll_ground
img_000.png,-1.2520427654596444,-3.042232395071413,4.218995893298251,18.869127818369638,-26.408398145019667,-3.854925597672519,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_001.png,1.6268321377057793,-3.1129094574657654,4.060095412828423,27.185657945998248,-11.902615578178679,23.2079783337351,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_002.png,-2.132411221628923,1.9534655181481289,5.393366066887898,-22.273800921890608,-1.7264399510517991,-14.708038602449761,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_003.png,2.066215411384061,-2.756730731532451,5.351160328529776,21.011761856973,2.727512914837197,-26.72080131986081,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_004.png,-1.8789329533759587,0.35127490907742287,4.257209342928329,-19.78969116641829,5.870880753258689,35.40078125999858,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_005.png,1.6495877569917106,-1.20664085743512,5.282154720179866,2.191300738032617,-24.42801890967638,6.76431188030179,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_006.png,0.3767313821755751,-1.5304050275576935,5.3117365311050655,22.770873620531574,15.72333482825877,-25.80881660722426,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
img_007.png,1.018755675251802,-0.8910364562016985,5.379071360861385,-15.726987935686983,-18.958310771213114,14.804826555502984,,,,,,
img_008.png,,,,,,,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407137
```

----
<div style="page-break-before:always"></div>

## 3. 評価
```
% mkdir image
% python validate.py
```

```
--- Yaw Error Statistics ---
  Mean   : 0.79°
  StdDev : 4.60°
  Median : 0.81°
  Max    : 10.60°
  Min    : -10.08°
  >10° Error Rate: 2/46 (4.3%)

--- Pitch Error Statistics ---
  Mean   : -1.03°
  StdDev : 5.92°
  Median : -1.95°
  Max    : 15.91°
  Min    : -16.94°
  >10° Error Rate: 5/46 (10.9%)

--- Roll Error Statistics ---
  Mean   : -0.63°
  StdDev : 5.59°
  Median : -1.03°
  Max    : 11.09°
  Min    : -14.64°
  >10° Error Rate: 2/46 (4.3%)

--- X Error Statistics ---
  Mean   : -0.04 m
  StdDev : 0.17 m
  Median : -0.04 m
  Max    : 0.41 m
  Min    : -0.36 m
  >1 m Error Rate: 0/46 (0.0%)

--- Y Error Statistics ---
  Mean   : -0.01 m
  StdDev : 0.16 m
  Median : -0.02 m
  Max    : 0.26 m
  Min    : -0.52 m
  >1 m Error Rate: 0/46 (0.0%)

--- Z Error Statistics ---
  Mean   : 0.02 m
  StdDev : 0.54 m
  Median : 0.32 m
  Max    : 0.71 m
  Min    : -1.08 m
  >1 m Error Rate: 1/46 (2.2%)
```

---

<div style="page-break-before:always"></div>

**yaw, pitch, roll** `.image/*_error_plot.png` `.image/*_error_hist.png`
<table>
<tr>
<td><img src='./image/yaw_error_plot.png' width=300></td>
<td><img src='./image/yaw_error_hist.png' width=300></td>
</tr>
<tr>
<td><img src='./image/pitch_error_plot.png' width=300></td>
<td><img src='./image/pitch_error_hist.png' width=300></td>
</tr>
<tr>
<td><img src='./image/roll_error_plot.png' width=300></td>
<td><img src='./image/roll_error_hist.png' width=300></td>
</tr>
</table>

---

<div style="page-break-before:always"></div>

**x, y, z** `.image/*_error_plot.png` `.image/*_error_hist.png`

<table>
<tr>
<td><img src='./image/x_error_plot.png' width=300></td>
<td><img src='./image/x_error_hist.png' width=300></td>
</tr>
<tr>
<td><img src='./image/y_error_plot.png' width=300></td>
<td><img src='./image/y_error_hist.png' width=300></td>
</tr>
<tr>
<td><img src='./image/z_error_plot.png' width=300></td>
<td><img src='./image/z_error_hist.png' width=300></td>
</tr>
</table>

---

<div style="page-break-before:always"></div>

## 4. 外れ値

```python
# 閾値
ERROR_THRESHOLD = 10.0  # degree
```

```
% python outlier.py 
           file  yaw_error  pitch_error  roll_error
4   img_004.png  -6.703524   -10.521065    5.710123
10  img_010.png  -5.834905    11.803557   -8.367072
18  img_018.png  10.601276    -2.078776   -2.982399
19  img_019.png  -1.294869     0.094455  -14.642794
30  img_030.png   0.791904    11.293494   -1.464644
37  img_037.png  -3.561408    15.905078   -1.723335
38  img_038.png -10.075624   -16.939176   11.086910
```

```
% head outlier_images.csv 
file,x,y,z,yaw,pitch,roll,filename,x_cube,y_cube,z_cube,yaw_cube,pitch_cube,roll_cube,x_ground,y_ground,z_ground,yaw_ground,pitch_ground,roll_ground,yaw_error,pitch_error,roll_error
img_004.png,-1.7665018092582345,0.5895020197263592,5.0,-13.086167149235118,16.391945660472935,29.690658712278093,img_004.png,-1.878932953375959,0.3512749090774228,4.257209342928329,-19.78969116641829,5.870880753258689,35.40078125999858,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407136,-6.703524017183172,-10.521064907214246,5.710122547720488
img_010.png,2.087154559060987,2.943929283671327,5.0,-26.43530310726579,-22.52835761539353,-17.661187446074443,img_010.png,2.0079343530398166,3.199795361799076,5.318809240740313,-32.27020809623126,-10.724800428160144,-26.02825965193983,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407136,-5.834904988965469,11.803557187233388,-8.367072205865387
img_018.png,-0.8535595884708322,0.7330458635879027,5.0,-12.021525779483719,-22.77036595769897,28.876537641712833,img_018.png,-1.211218437613952,0.6076392161158309,3.915015963545835,-1.420249720980405,-24.849142349465964,25.89413839595659,,,,,,,10.601276058503315,-2.0787763917669935,-2.9823992457562447
img_019.png,-1.106023526510647,0.8928073080778276,5.0,28.75353972964017,29.33570617249641,9.325213392440553,img_019.png,-0.8737899166212558,0.9544866858101364,5.2598844998584795,27.458671181204085,29.430161345243413,-5.317580580751553,,,,,,,-1.2948685484360851,0.09445517274700421,-14.642793973192106
img_030.png,-1.5047347285817072,-2.781295982148966,5.0,-26.3515156738438,-0.4124693887737065,-12.225043286807015,img_030.png,-1.4748352296378384,-2.701788419446409,5.394960341574793,-25.55961149826533,10.881024205081136,-13.68968693075081,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407136,0.7919041755784697,11.293493593854842,-1.4646436439437949
img_037.png,-1.5754287579546173,-2.43940523724097,5.0,-28.584497055940588,-17.7507504967722,-21.372183379394393,img_037.png,-1.6479062575202803,-2.2346514690744463,5.28270995950019,-32.14590460630856,-1.8456728234066369,-23.09551848882802,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407136,-3.5614075503679743,15.905077673365561,-1.723335109433627
img_038.png,-2.876874450437672,2.647733907676537,5.0,-23.728915682564523,28.524737024227587,24.091820953683722,img_038.png,-3.0776014354343357,2.637658634976492,4.1252444726257185,-33.804539280481485,11.585561125010972,35.17873081075112,-0.5,0.5,0.0,0.537319415718714,-2.5453032856914506,-9.602403227407136,-10.075623597916962,-16.939175899216615,11.086909857067397
```
---

<div style="page-break-before:always"></div>

## 5. 結果の可視化

```
% mkdir result_vis
% python result_vis.py
```
`./result_vis`

赤：Ground Truth
緑：推定値
<img src='./result_vis/img_011.png'>

<table>
<tr>
<td><img src='./result_vis/img_000.png'> </td>
<td><img src='./result_vis/img_001.png'></td>
</tr>
<tr>
<td><img src='./result_vis/img_002.png'> </td>
<td><img src='./result_vis/img_003.png'></td>
</tr>
</table>

---