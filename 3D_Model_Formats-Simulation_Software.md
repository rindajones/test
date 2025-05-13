
#### 注意：これは2025年5月13現在、ネット等より収集した情報に基づき正確性を欠く場合あり。

### 3Dモデル形式と対応ソフトウェア 一覧

| ファイル形式 | 形式の種類 | 説明 | 主な対応ソフトウェア |
|--------------|-------------|------|------------------|
| `.sldprt`, `.sldasm` | ネイティブ形式 | SolidWorks専用のパーツ・アセンブリ | SolidWorks,　△ Ansys（中間変換必要） |
| `.ipt`, `.iam` | ネイティブ形式 | Autodesk Inventor専用形式 | Inventor,　△ Fusion 360（インポート） |
| `.CATPart`, `.CATProduct` | ネイティブ形式 | CATIA形式（大規模機械で多用） | CATIA,　△ 3DEXPERIENCE |
| `.step`, `.stp` | 中間形式（標準） | 標準中立フォーマット。汎用性高い！ | SolidWorks, Fusion 360, Ansys, RecurDyn |
| `.iges`, `.igs` | 中間形式（旧標準） | 古めの中立形式。曲面多いと不安定 | SolidWorks, Fusion 360, △ Ansys |
| `.x_t`, `.x_b` | Parasolid | Siemens NX系列などで使用 | NX, SolidWorks（内部でParasolid使用） |
| `.f3d` | ネイティブ形式 | Fusion 360のローカル保存形式 | Fusion 360 のみ |
| `.obj`, `.stl` | メッシュ形式 | 3DプリンタやAR用。解析には不向き | △ Blender, Unity（可視化） × 物理シミュレーションには不適 |

#### △, x 無し：公式サポートあり。実運用でも問題なく使われている
#### △: 読み込みはできるが、変換が必要・動作が不安定・一部機能しか使えない可能性あり
#### x: シミュレーションに使えない、もしくは読めない形式
---

### シミュレーションソフトとのマッチング

| ソフト | 対応形式 | 用途 | 特徴 |
|--------|----------|------|------|
| **SolidWorks** | `.sldprt`, `.sldasm`, `.step`, `.iges` | CAD設計＋モーション解析 | モータ回転や干渉チェックに強い |
| **Fusion 360** | `.f3d`, `.step`, `.iges`, `.sldprt` | CAD + CAE + CAM | 手軽。小規模機械に最適 |
| **Ansys** | `.step`, `.iges`, `.x_t`, `.sldprt` | FEM, 構造・振動・熱解析 | 応力解析や振動数シミュに強い |
| **RecurDyn** | `.step`, `.iges`, `.sldasm` など | 動的機構解析（マルチボディ） | ギア伝達・剛体連成のリアル性高い |
| **Simulink + Simscape** | MATLAB内部形式 + `.step` | 電気-機構連成（デジタルツイン） | モータ・制御系との融合に最適 |
| **Unity / Unreal Engine** | `.fbx`, `.obj`, `.stl` | 可視化・VR/AR用途 | 実機の見せ方、デモに向くが物理精度は限定的 |
