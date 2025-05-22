# agv_160_v0.py
# ver0.1 - 定数待ち時間を加味した構造モデル（デバンニング・加工・バンニング）

from ortools.sat.python import cp_model

# === パラメータ設定 ===
TOTAL_TIME = 480  # 総稼働時間（分）
TOTAL_ITEMS = 160  # 目標搬送数

# 各中間工程の定数所要時間（分）
WAIT_TIMES = {
    '005_deban': 5,   # デバンニング
    '009_kako': 10,   # 加工
    '013_ban': 5      # バンニング
}

# 各AGVラインの設定（仮）
agv_lines = {
    '003': {'capacity': 1, 'base_cycle': 6, 'wait': WAIT_TIMES['005_deban']},
    '007': {'capacity': 10, 'base_cycle': 12, 'wait': WAIT_TIMES['009_kako']},
    '011': {'capacity': 10, 'base_cycle': 12, 'wait': WAIT_TIMES['013_ban']},
    '015': {'capacity': 1, 'base_cycle': 6, 'wait': 0},  # 出荷は待ち無しと仮定
}

model = cp_model.CpModel()
agv_vars = {}  # 各ラインのAGV台数

# === AGV台数変数を定義 ===
for agv_id, props in agv_lines.items():
    max_possible = TOTAL_ITEMS
    agv_vars[agv_id] = model.NewIntVar(1, max_possible, f"num_agv_{agv_id}")

# === 各ラインで達成できる搬送数を制約に追加（待機時間込み） ===
for agv_id, props in agv_lines.items():
    cap = props['capacity']
    cycle = props['base_cycle'] + props['wait']
    max_cycles = TOTAL_TIME // cycle
    model.Add(cap * max_cycles * agv_vars[agv_id] >= TOTAL_ITEMS)

# === 合計AGV台数の最小化 ===
model.Minimize(sum(agv_vars.values()))

# === ソルバー実行 ===
solver = cp_model.CpSolver()
#solver.parameters.log_search_progress = True
status = solver.Solve(model)

if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    print("\n=== 最小AGV台数（待機時間含む ver0.1） ===")
    total_agvs = 0
    for agv_id in agv_lines:
        count = solver.Value(agv_vars[agv_id])
        cap = agv_lines[agv_id]['capacity']
        cycle = agv_lines[agv_id]['base_cycle'] + agv_lines[agv_id]['wait']
        max_cycles = TOTAL_TIME // cycle
        total_transfer = cap * max_cycles * count
        total_time_per_cycle = cycle
        print(f"AGV {agv_id}: {count} 台 | 1サイクル {total_time_per_cycle} 分 | 最大搬送 {total_transfer} 個")
        total_agvs += count
    print(f"合計 AGV 台数: {total_agvs}")
else:
    print("解が見つかりませんでした（INFEASIBLE）")