# 社員ペアリング生成ツール

社員情報とチーム情報から、指定された条件を満たすペアを自動生成するPythonツールです。

## 概要

このツールは2つのCSVファイル（社員所属リスト、チーム別）を入力として、全対象者を重複なく2人1組のペアに分けます。ペアリングは以下の条件を満たすように生成されます：

- **グループが異なる**社員同士でペアを組む
- **チームが異なる**社員同士でペアを組む
- 除外対象者を指定可能
- 結果をテキストファイルに自動保存

## 前提条件

- Python 3.7以上
- pandasライブラリ

## セットアップ

### 1. 仮想環境の作成と有効化

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install pandas
```

## CSVファイルの準備

### 社員所属リスト（例：社員_所属リスト.csv）

```csv
人数,名前,部署,グループ,チーム,役職,入社日
1,田中太郎,営業部,営業1G,-,主任,2022/4/1
2,佐藤花子,開発部,開発1G,-,SE,2023/4/1
```

**必須カラム**: `名前`, `グループ`

### チーム別（例：チーム別.csv）

```csv
チーム 1,チーム 2,チーム 3,チーム 4
田中太郎,佐藤花子,山田次郎,鈴木美咲
高橋一郎,渡辺直美,中村健太,小林優子
```

各列がチーム名、各行がそのチームのメンバーを表します。

## 使用方法

### 基本的な使用

```python
from group_generator import generate_complete_pairing

# CSVファイルのパスを指定
employee_csv = '社員_所属リスト.csv'
team_csv = 'チーム別.csv'

# ペアリング生成を実行
result = generate_complete_pairing(
    employee_info_csv=employee_csv,
    team_info_csv=team_csv
)

if result:
    print(f"ペアリングに成功しました ({len(result)}組)")
    for i, (p1, p2) in enumerate(result, 1):
        print(f"ペア{i}: {p1}, {p2}")
else:
    print("条件を満たすペアの組み合わせは見つかりませんでした。")
```

### 除外対象者を指定する場合

```python
# 特定の社員をペアリングから除外
exclude_names = ['田中太郎', '佐藤花子']

result = generate_complete_pairing(
    employee_info_csv=employee_csv,
    team_info_csv=team_csv,
    exclusion_list=exclude_names
)
```

### 出力ファイル名を指定する場合

```python
result = generate_complete_pairing(
    employee_info_csv=employee_csv,
    team_info_csv=team_csv,
    output_file='my_pairing_result.txt'
)
```

### コマンドライン実行

```bash
source venv/bin/activate
python group_generator.py
```

## 出力

### コンソール出力

```
結果をファイルに保存しました: pairing_result_20250625_162044.txt
ペアリングに成功しました (26組):
  ペア1: 田中太郎, 佐藤花子
  ペア2: 山田次郎, 鈴木美咲
  ...
```

### ファイル出力

実行時に自動的に`pairing_result_YYYYMMDD_HHMMSS.txt`形式のファイルが生成されます：

```
ペアリング結果 - 2025年06月25日 16:20:44
==================================================

生成されたペア数: 26組

ペア1: 田中太郎, 佐藤花子
ペア2: 山田次郎, 鈴木美咲
...
```

## ペアリング条件

1. **グループ条件**: ペアの2人は異なるグループに所属している必要があります
2. **チーム条件**: ペアの2人は異なるチームに所属している必要があります
3. **重複なし**: 各社員は1つのペアにのみ所属します
4. **偶数人数**: 除外対象者を除いた後の人数が偶数である必要があります

## アルゴリズム

- **ランダム探索**: 条件を満たすペアが見つかるまで最大1000回試行
- **発見的探索**: 各試行でランダムにシャッフルした順序でペアを探索
- **制約充足**: グループとチームの制約を同時に満たすペアのみを選択

## エラーハンドリング

- `FileNotFoundError`: 指定されたCSVファイルが存在しない
- `KeyError`: CSVファイルに必須カラムが存在しない
- `ValueError`: 対象人数が奇数の場合

## ライセンス

MIT License

## 作成者

Generated with Claude Code
