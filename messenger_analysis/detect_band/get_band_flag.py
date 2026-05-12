import numpy as np

from common import pytplot, cdf, display
from messenger_analysis.analysis.analysis import analysis
from messenger_analysis.event_search.get_event_flag import get_event_flag



def get_band_flag(
        flag_data, 
        freqs_norm, 
        freqs_band=[0, 0.25, 0.5, 1.0],
        min_continuity=3
    ):
    """
    freqs_norm が (n_times, n_freqs) の 2次元配列である場合に対応したバンドフラグ取得関数。
    指定されたバンド内にフラグが存在し、かつ時間方向に指定点数以上連続している場合のみ 1 とする。
    
    Args:
        flag_data (np.ndarray): (n_times, n_freqs) の 0 or 1 配列
        freqs_norm (np.ndarray): (n_times, n_freqs) の規格化周波数配列
        freqs_band (list): バンド境界のリスト
        min_continuity (int): 最小の連続点数（3点連続なら 3）
        
    Returns:
        np.ndarray: (n_times, n_bands) のフラグ配列
    """
    n_times, n_freqs = flag_data.shape
    n_bands = len(freqs_band) - 1
    
    # 結果を格納する配列 (n_times, n_bands)
    band_flags = np.zeros((n_times, n_bands), dtype=int)

    for i in range(n_bands):
        f_min = freqs_band[i]
        f_max = freqs_band[i+1]
        
        # 1. 各時間・各周波数点において、その点が現在のバンド内にあるかどうかのマスクを作成
        mask_in_band = (freqs_norm >= f_min) & (freqs_norm < f_max)
        
        # 2. 「バンド内であり」かつ「フラグが1である」箇所を特定
        active_in_band = (flag_data == 1) & mask_in_band
        
        # 3. 各時間軸(axis=1)において、一つでも条件を満たすものがあれば 1 とする
        # これが「生のバンドフラグ」
        raw_band_flag = np.any(active_in_band, axis=1).astype(int)

        # 4. 連続性チェック (min_continuity 点以上連続している箇所のみ残す)
        if min_continuity > 1 and len(raw_band_flag) >= min_continuity:
            refined_flag = np.zeros_like(raw_band_flag)
            
            # コンボリューション（移動和）を使って連続性を判定
            # window size = min_continuity
            kernel = np.ones(min_continuity, dtype=int)
            
            # mode='same' で元の長さと同じ結果を得る
            # 各点において、自分を含む周囲 min_continuity 個の和を計算
            counts = np.convolve(raw_band_flag, kernel, mode='same')
            
            # 連続している場所を特定するロジック:
            # 3点連続の場合、中心の点は convolve の結果が 3 になる。
            # しかし、これだけだと端の点が漏れるため、「和が3である点」の周囲も1にする（膨張処理）
            
            # ステップA: 窓内のすべてが 1 である中心点をマーク
            perfect_matches = (counts == min_continuity)
            
            # ステップB: perfect_matches の前後 (min_continuity-1)//2 個を 1 に戻す
            # 3点連続の場合、ある点が perfect_match なら、その前後1点ずつも連続成分の一部
            for offset in range(-(min_continuity // 2), (min_continuity + 1) // 2):
                refined_flag |= np.roll(perfect_matches, offset)
            
            # ロールによる端の回り込みを防止
            if min_continuity // 2 > 0:
                refined_flag[:min_continuity // 2] &= perfect_matches[:min_continuity].any() # 簡易的な端処理
            
            current_band_flag = refined_flag.astype(int)
        else:
            current_band_flag = raw_band_flag

        band_flags[:, i] = current_band_flag
        
    return band_flags


def _get_band_flag(# 20260406
        flag_data, 
        freqs_norm, 
        freqs_band=[0, 0.25, 0.5, 1.0]
    ):
    """
    freqs_norm が (n_times, n_freqs) の 2次元配列である場合に対応したバンドフラグ取得関数。
    各時間点ごとに異なる周波数軸に対して、指定されたバンド内にフラグが存在するかを判定する。
    
    Args:
        flag_data (np.ndarray): (n_times, n_freqs) の 0 or 1 配列
        freqs_norm (np.ndarray): (n_times, n_freqs) の規格化周波数配列
        freqs_band (list): バンド境界のリスト
        
    Returns:
        np.ndarray: (n_times, n_bands) のフラグ配列
    """
    n_times, n_freqs = flag_data.shape
    n_bands = len(freqs_band) - 1
    
    # 結果を格納する配列 (n_times, n_bands)
    band_flags = np.zeros((n_times, n_bands), dtype=int)

    for i in range(n_bands):
        f_min = freqs_band[i]
        f_max = freqs_band[i+1]
        
        # 1. 各時間・各周波数点において、その点が現在のバンド内にあるかどうかのマスクを作成
        # mask shape: (n_times, n_freqs)
        mask_in_band = (freqs_norm >= f_min) & (freqs_norm < f_max)
        
        # 2. 「バンド内であり」かつ「フラグが1である」箇所を特定
        # active_in_band shape: (n_times, n_freqs)
        active_in_band = (flag_data == 1) & mask_in_band
        
        # 3. 各時間軸(axis=1)において、一つでも条件を満たすものがあれば 1 とする
        # .any() は boolean を返すため .astype(int) で変換
        band_flags[:, i] = np.any(active_in_band, axis=1).astype(int)
        
    return band_flags


def _get_band_flag(
        flag_data, 
        freqs_norm, 
        freqs_band=[0, 0.25, 0.5, 1.0]
    ):
    n_times = flag_data.shape[0]
    n_band = len(freqs_band) - 1

    band_flag = np.zeros((n_times, n_band))

    for i in range(len(freqs_band) - 1):
        f_min = freqs_band[i]
        f_max = freqs_band[i+1]

        idx_in_band = np.where((freqs_norm >= f_min) & (freqs_norm < f_max))[0]
        
        if len(idx_in_band) == 0:
            continue
            
        band_flag_i = np.any(flag_data[:, idx_in_band] == 1, axis=1).astype(int)
        
        band_flag[:, i] = band_flag_i
        
    return band_flag


def classify_bands(
        flag_data, 
        freqs_norm, 
        freqs_band=[0, 0.25, 0.5, 1.0]
    ):
    """
    emic_flag を指定された周波数バンドに振り分ける。
    
    Args:
        emic_flag (np.ndarray): (n_times, n_freqs) の 0 or 1 配列
        freqs_norm (np.ndarray): 長さ n_freqs の規格化周波数配列
        freqs_band (list): バンド境界のリスト (例: [0, 0.25, 0.5, 1])
        
    Returns:
        dict: 各バンド名をキーとし、その時間のフラグ (n_times,) を値に持つ辞書
    """
    n_times = flag_data.shape[0]
    results = {}

    for i in range(len(freqs_band) - 1):
        f_min = freqs_band[i]
        f_max = freqs_band[i+1]
        band_name = f'band_{f_min}_{f_max}'.replace('.', 'p')
        
        # 1. 現在のバンドに含まれる周波数インデックスを取得
        # ※ 境界条件(等号)は解析の目的に合わせて調整してください
        idx_in_band = np.where((freqs_norm >= f_min) & (freqs_norm < f_max))[0]
        
        if len(idx_in_band) == 0:
            results[band_name] = np.zeros(n_times)
            continue
            
        # 2. そのバンド内において、いずれかの周波数で emic_flag が 1 であれば 1 とする (Any判定)
        # もし「バンド内の半分以上が1なら」といった条件にする場合は np.mean > 0.5 などに変更可能
        band_flag = np.any(flag_data[:, idx_in_band] == 1, axis=1).astype(int)
        
        results[band_name] = band_flag
        
    return results


