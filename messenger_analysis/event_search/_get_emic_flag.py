import numpy as np
from common import display, pytplot


def get_psd_flag(
        psd_x,
        psd_y,
        psd_z,
        threshold_psd=1e2,
        threshold_ratio=10,
        get_support_data=False
):
    psd_xy = (psd_x + psd_y) / 2
    noise = np.nanpercentile(psd_z, 50)
    is_event_psd = (psd_xy > threshold_psd * noise)
    psd_ratio = psd_xy / psd_z
    is_event_ratio = psd_ratio > threshold_ratio
    # flag_psd = np.where(is_event_psd, 1, 0)
    # flag_ratio = np.where(is_event_ratio, 1, 0)
    flag = np.where(is_event_psd & is_event_ratio, 1, 0)

    if get_support_data:
        flag_intensity = np.where(is_event_psd, 1, 0)
        flag_ratio = np.where(is_event_ratio, 1, 0)
        dict_support = {
            'flag_psd_intensity': flag_intensity,
            'flag_psd_ratio': flag_ratio
        }
        return flag, dict_support
    else:
        return flag

def get_polari_flag(
        polari,
        threshold_polari=-.5
):
    flag = np.where((polari < threshold_polari) & (polari >= -1), 1, 0)
    return flag


def get_emic_flag(
        times: np.ndarray,
        freqs: np.ndarray,
        flag_array: np.ndarray,
        max_freq: float = 1.1,
) -> np.ndarray:
    """
    イベントフラグ配列から、max_freqを超えるイベントが発生した時間ステップ全体を排除する。

    Parameters:
    times (np.ndarray): 時間座標配列 [s]. (未使用だがシグネチャ維持)
    freqs (np.ndarray): 周波数座標配列 [MHz].
    flag_array (np.ndarray): 元のイベントフラグ (0, 1) 配列 (N_time, N_freq).
    max_freq (float): イベントを排除する最大周波数閾値 [MHz].

    Returns:
    np.ndarray: 処理後のEMICイベントフラグ配列 (N_time, N_freq).
    """
    processed_flag = flag_array.copy()

    high_freq_mask = freqs > max_freq
    high_freq_events = (flag_array == 1) & high_freq_mask[np.newaxis, :]
    contaminated_time_indices = np.any(high_freq_events, axis=1)
    processed_flag[contaminated_time_indices, :] = 0

    return processed_flag

def get_dense_flag(
        flag_array,
        window_size=(5, 5),
        min_density=0.5,
):
    n_times, n_freqs = flag_array.shape
    n_times_w, n_freqs_w = window_size
    
    pad_times = n_times_w // 2
    pad_freqs = n_freqs_w // 2
    
    padded_array = np.pad(
        flag_array, 
        ((pad_times, pad_times), (pad_freqs, pad_freqs)), 
        mode='edge',
        # constant_values=0
    )
    
    dense_map = np.zeros_like(flag_array, dtype=float)
    total_pixels = n_times_w * n_freqs_w
    
    # パディングされた配列上でループを回し、すべての出力点を計算
    for i in range(n_times):
        for j in range(n_freqs):
            # パディングされた配列上で、元の位置(i, j)の中心に窓を合わせる
            # 例: 窓の中心が(i, j)になるようにスライス
            window_sum = np.sum(
                padded_array[i : i + n_times_w, j : j + n_freqs_w]
            )
            density = window_sum / total_pixels
            
            dense_map[i, j] = density
    
    dense_flag = (dense_map >= min_density).astype(int)
            
    return dense_flag


def _get_continuous_spans(flag_1d, min_span):
    """
    1次元のフラグ配列から、指定された最小幅以上の連続した'1'のスパンを抽出する。

    Parameters:
    flag_1d (np.ndarray): 0または1からなる1次元配列。
    min_span (int): 連続と見なす最小の長さ。

    Returns:
    list[tuple]: (start_index, end_index) のリスト。end_indexは排他的。
    """
    if flag_1d.size == 0:
        return []

    # イベントの開始と終了のインデックスを見つける
    # np.diffを使って、0 -> 1 (開始: 1) と 1 -> 0 (終了: -1) の変化点を検出
    change_points = np.diff(np.concatenate(([0], flag_1d, [0])))
    
    # 開始インデックス (change_points == 1)
    starts = np.where(change_points == 1)[0]
    # 終了インデックス (change_points == -1)
    ends = np.where(change_points == -1)[0]

    spans = []
    if starts.size != ends.size:
        # これは発生しないはずだが、念のため
        print("Error: Start and end counts do not match.")
        return []

    for start, end in zip(starts, ends):
        span_width = end - start
        if span_width >= min_span:
            spans.append((start, end))
            
    return spans


# def get_emic_flag(
#         times: np.ndarray,
#         freqs: np.ndarray,
#         flag_array: np.ndarray,
#         max_freq: float = 1.1,
#         min_span_time: int = 2,
#         merge_span: float = 60.0, # span to merge [s]
# ):
#     n_times, n_freqs = flag_array.shape
    
#     flag_emic = np.zeros_like(flag_array)
#     processed_flag = flag_array.copy()
#     # ----------------------------------------------------
#     # ステップ 1: 初期周波数フィルタリング
#     # ----------------------------------------------------
#     # max_freq (例: 1.0 MHz) を超える周波数ビンを0にする
#     for i, t in enumerate(times):
#         for j, f in enumerate(freqs):
#             if flag_array[i, j] == 1 and f > max_freq:
#                 processed_flag[i, :] = 0

#     # freqs_mask_to_zero = np.where(freqs > max_freq)
    
#     # # フィルタリングされた一時的なフラグ配列を作成
    
#     # processed_flag[:, freqs_mask_to_zero] = 0

#     pytplot.store_data('test_flag', {'x': times, 'y': processed_flag, 'v': freqs})
#     pytplot.options('test_flag', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

#     # ----------------------------------------------------
#     # ステップ 2: 時間軸イベント抽出と最小時間幅フィルタリング
#     # ----------------------------------------------------
#     # 任意の周波数でフラグが立っている時間ステップを見つける
#     time_events_1d = np.any(processed_flag, axis=1).astype(int)
    
#     # min_span_time 未満のイベントを除去
#     # time_widths_indices: [(start, end), ...]
#     time_widths_indices = _get_continuous_spans(time_events_1d, min_span_time)

#     # ----------------------------------------------------
#     # ステップ 3: 時間軸マージ (merge_span)
#     # ----------------------------------------------------
#     merged_indices = []
#     if time_widths_indices:
#         current_start, current_end = time_widths_indices[0]
        
#         for next_start, next_end in time_widths_indices[1:]:
#             # 現在のイベントの終了時間 (排他的インデックス current_end - 1)
#             # 次のイベントの開始時間
#             gap_start_time = times[current_end - 1]
#             gap_end_time = times[next_start]
            
#             time_gap = gap_end_time - gap_start_time

#             # ギャップがマージ閾値以下の場合はマージ
#             if time_gap <= merge_span:
#                 current_end = next_end
#             else:
#                 # ギャップが大きい場合、現在の塊を確定し、次の塊を開始
#                 merged_indices.append((current_start, current_end))
#                 current_start, current_end = next_start, next_end
        
#         merged_indices.append((current_start, current_end)) # 最後の塊を追加

#     # ----------------------------------------------------
#     # ステップ 4: マージ後の塊の最大周波数チェックと最終フラグ生成
#     # ----------------------------------------------------
#     # ユーザー要求: mergeした後の塊が max_freq を超えるものはイベントとして排除する。
    
#     for start, end in merged_indices:
#         # この塊の時間スパン [start:end] における元のフラグ配列 (周波数制限前)
#         original_span_data = flag_array[start:end, :]
        
#         # この塊全体でフラグが立っている周波数ビンのインデックス
#         # 周波数が低い順にソートされていることを前提とする
#         active_freq_indices = np.where(np.any(original_span_data, axis=0))[0] 
        
#         is_max_freq_exceeded = False
        
#         if active_freq_indices.size > 0:
#             # 塊全体の最大周波数 (元のフラグ配列に基づく)
#             # active_freq_indicesは周波数順に並んでいるので、最後のインデックスが最大周波数に対応
#             actual_max_freq_in_span = freqs[active_freq_indices[-1]] 
            
#             # max_freq (例: 1.0 MHz) を超えているかチェック
#             if actual_max_freq_in_span > max_freq:
#                 is_max_freq_exceeded = True # 排除フラグを立てる

#         # 排除フラグが立っていない場合のみ、結果配列に反映する
#         if not is_max_freq_exceeded:
#             # processed_flag (ステップ1で周波数フィルタリング済みのフラグ) をコピー
#             flag_emic[start:end, :] = processed_flag[start:end, :]
            
#     return flag_emic