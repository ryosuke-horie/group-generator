import pandas as pd
import random
from typing import List, Tuple, Optional
from datetime import datetime


def load_employee_info(employee_info_csv: str) -> pd.DataFrame:
    """
    社員情報CSVファイルを読み込む
    """
    try:
        df = pd.read_csv(employee_info_csv, encoding='utf-8')
        # 必須カラムの存在確認
        required_columns = ['名前', 'グループ']
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"必須カラム '{col}' が見つかりません")
        return df[['名前', 'グループ']]
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {employee_info_csv}")


def load_team_info(team_info_csv: str) -> pd.DataFrame:
    """
    チーム情報CSVファイルを読み込み、名前とチーム情報のペアに変換する
    """
    try:
        df = pd.read_csv(team_info_csv, encoding='utf-8')
        
        # チーム情報を名前とチームのペアに変換
        team_data = []
        for team_idx, team_name in enumerate(df.columns):
            for _, row in df.iterrows():
                name = row[team_name]
                # 空のセルや欠損値をスキップ
                if pd.notna(name) and str(name).strip():
                    team_data.append({
                        '名前': str(name).strip(),
                        'チーム': team_name
                    })
        
        return pd.DataFrame(team_data)
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {team_info_csv}")


def merge_employee_data(employee_df: pd.DataFrame, team_df: pd.DataFrame) -> pd.DataFrame:
    """
    社員情報とチーム情報を名前をキーとして結合する
    """
    merged_df = pd.merge(employee_df, team_df, on='名前', how='inner')
    return merged_df


def filter_exclusion_list(df: pd.DataFrame, exclusion_list: List[str]) -> pd.DataFrame:
    """
    除外リストに含まれる社員を除外する
    """
    return df[~df['名前'].isin(exclusion_list)]


def validate_even_number(df: pd.DataFrame) -> None:
    """
    対象人数が偶数かどうかを検証する
    """
    total_count = len(df)
    if total_count % 2 != 0:
        raise ValueError(f"対象人数が奇数です ({total_count}人)。ペアを作成できません。")


def can_pair(person1: dict, person2: dict) -> bool:
    """
    2人がペアになれるかどうかを判定する
    条件：グループが異なる かつ チームが異なる
    """
    return (person1['グループ'] != person2['グループ'] and 
            person1['チーム'] != person2['チーム'])


def find_pairing_candidates(person: dict, available_people: List[dict]) -> List[dict]:
    """
    指定された人とペアになれる候補者を見つける
    """
    candidates = []
    for candidate in available_people:
        if can_pair(person, candidate):
            candidates.append(candidate)
    return candidates


def generate_single_pairing_attempt(people_list: List[dict]) -> Optional[List[Tuple[str, str]]]:
    """
    1回の試行でペアリングを生成する
    """
    # 対象者リストをランダムにシャッフル
    shuffled_people = people_list.copy()
    random.shuffle(shuffled_people)
    
    # ペア成立済みの人を記録するセット
    paired_people = set()
    # 結果を格納するリスト
    pairs = []
    
    # シャッフルしたリストの先頭から順に処理
    for person1 in shuffled_people:
        # 既にペアになっている場合はスキップ
        if person1['名前'] in paired_people:
            continue
            
        # 未ペアの人から候補者を探す
        available_people = [p for p in shuffled_people 
                          if p['名前'] not in paired_people and p['名前'] != person1['名前']]
        
        # ペアリング条件を満たす候補者を見つける
        candidates = find_pairing_candidates(person1, available_people)
        
        # 候補者がいない場合、この試行は失敗
        if not candidates:
            return None
            
        # 候補者の中からランダムに選択
        person2 = random.choice(candidates)
        
        # ペアを成立させる
        pairs.append((person1['名前'], person2['名前']))
        paired_people.add(person1['名前'])
        paired_people.add(person2['名前'])
    
    return pairs


def save_pairing_to_file(pairs: List[Tuple[str, str]], output_file: str = None) -> str:
    """
    ペアリング結果をテキストファイルに保存する
    
    Args:
        pairs: ペアのリスト
        output_file: 出力ファイル名（指定しない場合は自動生成）
    
    Returns:
        保存されたファイル名
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"pairing_result_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"ペアリング結果 - {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"生成されたペア数: {len(pairs)}組\n\n")
        
        for i, (p1, p2) in enumerate(pairs, 1):
            f.write(f"ペア{i}: {p1}, {p2}\n")
    
    return output_file


def generate_complete_pairing(
    employee_info_csv: str,
    team_info_csv: str,
    exclusion_list: List[str] = [],
    output_file: str = None
) -> Optional[List[Tuple[str, str]]]:
    """
    社員ペアリング生成のメイン関数
    
    Args:
        employee_info_csv: 社員情報CSVファイルのパス
        team_info_csv: チーム情報CSVファイルのパス
        exclusion_list: 除外する社員名のリスト
        output_file: 出力ファイル名（指定しない場合は自動生成）
    
    Returns:
        成功時: ペアのリスト [(名前1, 名前2), ...]
        失敗時: None
    """
    try:
        # 1. データ読み込みと統合
        employee_df = load_employee_info(employee_info_csv)
        team_df = load_team_info(team_info_csv)
        merged_df = merge_employee_data(employee_df, team_df)
        
        # 2. データの前処理
        filtered_df = filter_exclusion_list(merged_df, exclusion_list)
        validate_even_number(filtered_df)
        
        # 3. 辞書形式のリストに変換
        people_list = filtered_df.to_dict('records')
        
        # 4. ペアリング生成（最大1000回試行）
        max_attempts = 1000
        for attempt in range(max_attempts):
            result = generate_single_pairing_attempt(people_list)
            if result is not None:
                # 5. 成功時はファイルに保存
                if output_file is not None or True:  # 常にファイル保存
                    saved_file = save_pairing_to_file(result, output_file)
                    print(f"結果をファイルに保存しました: {saved_file}")
                return result
        
        # 6. 失敗時の処理
        return None
        
    except (FileNotFoundError, KeyError, ValueError) as e:
        raise e


# 使用例とテスト実行
if __name__ == "__main__":
    # CSVファイルのパスを指定
    employee_csv_path = '社員_所属リスト.csv'
    team_csv_path = 'チーム別.csv'
    
    # 除外リストの例
    exclude_names = ['三留秋穂', '志田彩']
    
    try:
        # 関数を実行してペアリング結果を取得
        pairing_result = generate_complete_pairing(
            employee_info_csv=employee_csv_path,
            team_info_csv=team_csv_path,
            exclusion_list=exclude_names
        )
        
        # 結果を出力
        if pairing_result:
            print(f"ペアリングに成功しました ({len(pairing_result)}組):")
            for i, (p1, p2) in enumerate(pairing_result, 1):
                print(f"  ペア{i}: {p1}, {p2}")
        else:
            print("条件を満たすペアの組み合わせは見つかりませんでした。")
            
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"エラーが発生しました: {e}")