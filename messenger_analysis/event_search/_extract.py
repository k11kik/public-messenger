import numpy as np
from common import display, time

def _get_continuous_spans(binary_array, min_span):
    """
    1次元バイナリ配列から連続する「1」のインデックス範囲 [(start, end), ...] を抽出する。
    endは排他的（そのインデックス自体は含まない）。
    """
    diff = np.diff(binary_array.astype(int), prepend=0, append=0)
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]
    
    spans = []
    for start, end in zip(starts, ends):
        if end - start >= min_span: # 最小幅のチェック
            spans.append((start, end))
            
    return spans


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



def get_event_time_from_dense_flag(
        times,
        freqs,
        dense_flag,
        max_freq=1,
        min_span_time=2,
        merge_span=60, # span to merge [s]
):
    n_times, n_freqs = dense_flag.shape
    
    freqs_mask = (freqs > max_freq)
    full_freq_mask = np.tile(freqs_mask[np.newaxis, :], (n_times, 1))
    processed_flag = dense_flag.copy()
    processed_flag[full_freq_mask] = 0

    # 2. 時間軸でのイベント幅の抽出
    # 任意の周波数でフラグが立っていれば、その時間ステップをイベントと見なす
    time_events = np.any(processed_flag, axis=1).astype(int)
    time_widths_indices = _get_continuous_spans(time_events, min_span_time)

    # # 3. 周波数軸でのイベント幅の抽出
    # # 任意の時間でフラグが立っていれば、その周波数ビンをイベントと見なす
    # freq_events = np.any(processed_flag, axis=0).astype(int)
    # freq_widths_indices = _get_continuous_spans(freq_events, min_span_freq)
    
    # merge
    merged_indices = []
    
    if not time_widths_indices:
        # イベントがない場合は空のリストを返す
        pass
    else:
        # 最初のイベントからマージを開始
        current_start, current_end = time_widths_indices[0]
        
        for next_start, next_end in time_widths_indices[1:]:
            
            # 前のイベントの終了時間と次のイベントの開始時間
            # current_end は排他的インデックスなので、実際の最後の時間ステップは current_end - 1
            gap_start_time = times[current_end - 1]
            gap_end_time = times[next_start]

            # イベント間の時間間隔を計算
            # ギャップは次のイベントの開始時間と前のイベントの終了時間の間隔
            time_gap = gap_end_time - gap_start_time

            # ギャップの時間が merge_span よりも小さい場合、マージする
            if time_gap <= merge_span:
                # 終了インデックスを次のイベントの終了インデックスに更新
                current_end = next_end
            else:
                # ギャップが大きい場合、現在のイベントを確定し、次のイベントを開始する
                merged_indices.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        
        # 最後のイベントをリストに追加
        merged_indices.append((current_start, current_end))

    # 4. インデックスを実際の時間値に変換
    # event_time_widths: [(times[start], times[end-1]), ...]
    event_time_widths = [(times[s], times[e - 1]) for s, e in merged_indices]
    
    return merged_indices, event_time_widths


def get_event_frequency_bands(
        freqs,
        dense_flag, 
        t_start_idx, 
        t_end_idx, 
        min_freq_gap=.1,
        max_freq=1
    ):
    """
    指定された時間幅におけるdense_flagを分析し、min_freq_gapに基づいて
    複数の周波数バンドを抽出する。

    Parameters:
    flag_array (np.ndarray): 1 または 0 の値を持つ (n_times, n_freqs) 配列。
    freqs (np.ndarray): 周波数軸の値 (n_freqs, )。
    t_start_idx (int): イベントの開始時間インデックス (包括的)。
    t_end_idx (int): イベントの終了時間インデックス (排他的)。
    min_freq_gap (float): バンドを分離するために許容される周波数間隔 [単位は freqs と同じ]。

    Returns:
    list of tuples: 抽出された周波数バンド [(start_freq, end_freq), ...]
    """
    n_times, n_freqs = dense_flag.shape
    freqs_mask = (freqs > max_freq)
    full_freq_mask = np.tile(freqs_mask[np.newaxis, :], (n_times, 1))
    processed_flag = dense_flag.copy()
    processed_flag[full_freq_mask] = 0

    # 1. イベントの時間幅内での周波数フラグを抽出
    # イベント期間 (t_start_idx から t_end_idx-1) において、
    # 任意の時間で「1」が立っている周波数ビンを特定する。
    event_slice = processed_flag[t_start_idx:t_end_idx, :]
    
    # イベント期間内で少なくとも一度でもフラグが立った周波数ビン (1次元ブール配列)
    freq_indicator = np.any(event_slice, axis=0) 
    
    # 2. フラグが立った周波数ビンのインデックスを取得
    flagged_indices = np.where(freq_indicator)[0]
    
    if len(flagged_indices) == 0:
        return []
        
    # 3. 連続するバンドを分離し、マージするロジック
    
    # 周波数値の間隔を計算
    # 連続するフラグ付きインデックスの間の周波数ギャップ
    freq_gaps = freqs[flagged_indices[1:]] - freqs[flagged_indices[:-1]]
    
    # min_freq_gap よりも大きいギャップがある場所を特定
    split_points = np.where(freq_gaps > min_freq_gap)[0]
    
    # 4. バンドを構成
    band_start_indices = [flagged_indices[0]]
    band_end_indices = []
    
    # ギャップの次の点が次のバンドの開始点
    for split_index in split_points:
        band_end_indices.append(flagged_indices[split_index])
        band_start_indices.append(flagged_indices[split_index + 1])
        
    # 最後のバンドの終了インデックスは、全フラグ付きインデックスの最後
    band_end_indices.append(flagged_indices[-1])
    
    
    # 5. 実際の周波数値に変換
    extracted_bands = []
    for start_idx_f, end_idx_f in zip(band_start_indices, band_end_indices):
        # バンドの下端と上端周波数を取得
        start_freq = freqs[start_idx_f]
        end_freq = freqs[end_idx_f]
        
        extracted_bands.append([start_freq, end_freq])
        
    return extracted_bands


def extract_event(
        times,
        freqs,
        flag_array,
        max_freq=1,
        min_span_time=2,
        merge_span=60, # span to merge [s]
        min_freq_gap=.1,
        min_event_delta_time=60,
        min_event_delta_freq=.1
):
    event_times_indices, event_times = get_event_time_from_dense_flag(
        times,
        freqs,
        flag_array,
        max_freq=max_freq,
        min_span_time=min_span_time,
        merge_span=merge_span
    )
    
    event_freqs = []
    for i, event_times_idx in enumerate(event_times_indices):
        freq_bands = get_event_frequency_bands(
            freqs,
            flag_array,
            event_times_idx[0],
            event_times_idx[1],
            min_freq_gap=min_freq_gap
        )
        event_freqs.append(freq_bands)
    
    # event regulation
    event_times_regulated = []
    event_freqs_regulated = []
    for i, (event_time, event_freq) in enumerate(zip(event_times, event_freqs)):
        delta_time = event_time[1] - event_time[0]
        if delta_time >= min_event_delta_time:
            if len(event_freq) == 0:
                continue
            elif len(event_freq) == 1:
                delta_freq = event_freq[0][1] - event_freq[0][0]
                if delta_freq >= min_event_delta_freq:
                    event_times_regulated.append(event_time)
                    event_freqs_regulated.append([event_freq[0][0], event_freq[0][1]])
            else:
                event_freqs_regulated_ = []
                for i in range(len(event_freq)):
                    event_freq_i = event_freq[i]
                    delta_freq = event_freq_i[1] - event_freq_i[0]
                    if delta_freq >= min_event_delta_freq:
                        event_freqs_regulated_.append(event_freq_i)
                if event_freqs_regulated_:
                    event_times_regulated.append(event_time)
                    if len(event_freqs_regulated_) == 1:
                        event_freqs_regulated.append([event_freqs_regulated_[0][0], event_freqs_regulated_[0][1]])
                    else:
                        event_freqs_regulated.append(event_freqs_regulated_)

    return event_times_regulated, event_freqs_regulated

