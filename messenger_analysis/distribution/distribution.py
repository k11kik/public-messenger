import matplotlib.pyplot as plt
import numpy as np
from common import path


def plot_bar_ions(
        vals, 
        labels, 
        suptitle=None, 
        ylog=False,
        savefig=None,
        annotate=True,
        xlabel=None,
        ylabel=None,
        yrange=None
    ):
    """
    イオン種ごとの合計時間を棒グラフで表示します。
    """
    # カラーマップの設定（各棒に異なる色を適用）
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(labels)))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle(suptitle)
    
    # 棒グラフの描画
    bars = ax.bar(labels, vals, color=colors, edgecolor='black', alpha=0.8)


    # 対数スケールの設定（値の差が大きいため有効）
    if ylog:
        ax.set_yscale('log')

    ax.set_ylim(yrange)

    # 各棒の上に数値を表示（対数スケールでない場合に見やすい）
    if annotate:
        for bar in bars:
            height = bar.get_height()
            # 0より大きい場合のみ描画（特に対数スケールの際の不具合防止）
            if height > 0:
                ax.annotate(f'{height:.2e}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3ポイント上にオフセット
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)
                
    ax.grid(axis='y', ls='--', alpha=0.7)

    # label
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)

    plt.tight_layout()

    path.savefig(savefig)
    return