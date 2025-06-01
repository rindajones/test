
# YOLOv5 再学習用 Docker Compose 実行ガイド

このドキュメントは、Git Bash 上で YOLOv5 モデルを再学習するための `docker compose` 実行手順をまとめたものです。

---

## 📂 ディレクトリ構成（例）

```
raspi-marker-detector/
├── Dockerfile
├── docker-compose.yml
├── data/
│   ├── data.yaml
│   ├── hyp.yaml
│   ├── images/
│   │   └── train/
│   └── labels/
│       └── train/
└── runs/
```

---

## 🔧 1. Dockerfile の内容

```dockerfile
FROM python:3.11-slim

RUN apt-get update &&     apt-get install -y git libgl1-mesa-glx libglib2.0-0 &&     pip install --upgrade pip

WORKDIR /app
RUN git clone https://github.com/ultralytics/yolov5.git --recursive &&     cd yolov5 &&     pip install -r requirements.txt

WORKDIR /app/yolov5
ENTRYPOINT []
```

---

## 📦 2. docker-compose.yml の内容

```yaml
version: "3.9"

services:
  yolo-trainer:
    build: .
    shm_size: '1gb'
    volumes:
      - "./data:/app/yolov5/data"
      - "./runs:/app/yolov5/runs"
    working_dir: /app/yolov5
    command: >
      python train.py
      --img 224
      --batch 16
      --epochs 10
      --data data.yaml
      --weights yolov5n.pt
      --name raspi_run4
      --hyp data/hyp.yaml
```

---

## 📄 3. data.yaml の例

```yaml
train: data/images/train
val: data/images/train
nc: 2
names: ['marker_red', 'marker_yellow']
```

---

## 📄 4. hyp.yaml の例（YOLOv5用ハイパーパラメータ）

```yaml
lr0: 0.01
lrf: 0.1
momentum: 0.937
weight_decay: 0.0005
warmup_epochs: 2.0
warmup_bias_lr: 0.1
warmup_momentum: 0.8
box: 0.05
cls: 0.5
obj: 1.0
iou_t: 0.2
anchor_t: 4.0
```

---

## 🚀 5. 実行コマンド（Git Bash）

```bash
docker compose up --build
```

---

## ✅ 6. 結果確認（出力ファイル）

- `runs/train/raspi_run4/weights/best.pt` : 学習済みモデル
- `results.png` : 精度グラフ
- `labels.jpg` : ラベル分布
- `opt.yaml` : 学習設定の記録
