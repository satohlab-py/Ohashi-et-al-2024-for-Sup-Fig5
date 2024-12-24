import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast  # 安全にリスト形式を解析するために使用

# 必要なフォルダを作成
merged_folder = "MergedCSVs"
output_folder = "Heatmaps"
os.makedirs(merged_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# カレントフォルダにあるCSVファイルをリストアップ
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'cm-' in f]

# ファイル名で分類
groups = {}
for file in csv_files:
    key = file.split('cm-')[0]  # '5cm' のような部分を抽出
    if key not in groups:
        groups[key] = []
    groups[key].append(file)

# 全ファイルのG値の最大値と最小値を求める
global_min = float('inf')
global_max = float('-inf')

for files in groups.values():
    for file in files:
        df = pd.read_csv(file)

        # リスト形式データのみ抽出
        def is_list(x):
            try:
                return isinstance(ast.literal_eval(x), list)
            except (ValueError, SyntaxError):
                return False

        df = df[df['G Values'].apply(is_list)]  # リスト形式のデータのみ抽出
        df['Normalized G Values'] = df['G Values'].apply(lambda x: ast.literal_eval(x))

        for g_values in df['Normalized G Values']:
            global_min = min(global_min, min(g_values))
            global_max = max(global_max, max(g_values))

# グループごとにCSVを統合し、解析を行う
for key, files in groups.items():
    # 各グループのCSVを統合
    merged_filename = f"Merged{key}cm.csv"
    merged_path = os.path.join(merged_folder, merged_filename)

    dfs = []
    for file in files:
        df = pd.read_csv(file)

        # Distance列のクリーニング
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')  # 数値以外をNaNに変換
        df = df.dropna(subset=['Distance'])  # NaNを削除

        # リスト形式データのみ抽出
        df = df[df['G Values'].apply(is_list)]  # リスト形式のデータのみ抽出
        df['Normalized G Values'] = df['G Values'].apply(lambda x: ast.literal_eval(x))

        dfs.append(df)

    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_csv(merged_path, index=False)

    # 1) Distanceの平均を算出
    mean_distance = int(merged_df['Distance'].mean())

    # 2) 線分を作成（BGR=[0, G Value, 0]）
    fixed_length = mean_distance  # ヒートマップの横幅を平均距離に設定
    num_lines = len(merged_df)  # CSVの行数が線分の本数
    lines = np.zeros((num_lines, fixed_length, 3), dtype=np.uint8)  # BGR画像の配列

    for idx, g_values in enumerate(merged_df['Normalized G Values']):
        interpolated = np.interp(
            np.linspace(0, len(g_values) - 1, fixed_length),  # 指定された長さに補間
            range(len(g_values)),
            g_values
        )
        lines[idx, :, 1] = np.clip(interpolated, 0, 255)  # 緑 (G チャンネル) に値を代入

    # 3) ヒートマップの生成
    avg_g_values = np.mean(lines[:, :, 1], axis=0)  # 各列方向の平均を計算
    heatmap = np.tile(avg_g_values, (10, 1))  # 幅10ピクセルで複製

    # 描画
    fig, axes = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1, num_lines / 10]})

    # ヒートマップ部分（グローバルスケール）
    axes[0].imshow(
        heatmap, cmap='hot', aspect='auto',
        extent=[0, fixed_length, 0, 10],
        vmin=global_min, vmax=global_max  # グローバルスケールを適用
    )
    axes[0].set_title(f"Heatmap for {key} (Global Scale)")
    axes[0].set_xlabel("Distance (pixels)")
    axes[0].set_ylabel("Height (pixels)")

    # 線分部分 (BGR 緑の表現)
    axes[1].imshow(lines, aspect='auto', extent=[0, fixed_length, 0, num_lines])
    axes[1].set_title(f"Lines from CSV Data (BGR Representation) for {key}")
    axes[1].set_xlabel("Distance (pixels)")
    axes[1].set_ylabel("Number of Lines (CSV count)")

    # 保存
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"Heatmap_with_Lines_BGR_Global_{key}.png"))
    plt.close()
