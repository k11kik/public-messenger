import matplotlib.pyplot as plt
import numpy as np

def plot_orbit_xy(df, save_plot=True):
    """
    x-y平面での軌道プロット（水星中心）
    
    Parameters:
    df (pandas.DataFrame): データフレーム
    save_plot (bool): プロットを保存するかどうか
    """
    plt.figure(figsize=(12, 10))
    
    # 水星の半径（km）
    mercury_radius = 2439.7
    
    # データの範囲を取得して軸の範囲を設定
    x_min, x_max = df['X_MSO'].min(), df['X_MSO'].max()
    y_min, y_max = df['Y_MSO'].min(), df['Y_MSO'].max()
    
    # 軸の範囲を少し拡張して水星が見えるようにする
    margin = max(mercury_radius * 0.5, 1000)  # 少なくとも1000kmのマージン
    x_min_plot = min(x_min - margin, -mercury_radius * 1.2)
    x_max_plot = max(x_max + margin, mercury_radius * 1.2)
    y_min_plot = min(y_min - margin, -mercury_radius * 1.2)
    y_max_plot = max(y_max + margin, mercury_radius * 1.2)
    
    # 水星を黒く塗りつぶされた円で表示（最初に描画）
    theta = np.linspace(0, 2*np.pi, 100)
    x_mercury = mercury_radius * np.cos(theta)
    y_mercury = mercury_radius * np.sin(theta)
    plt.fill(x_mercury, y_mercury, 'black', alpha=0.8, label='Mercury')
    plt.plot(x_mercury, y_mercury, 'k-', linewidth=1)
    
    # 軌道プロット（水星の上に描画）
    plt.plot(df['X_MSO'], df['Y_MSO'], 'b-', linewidth=0.5, alpha=0.7, label='MESSENGER Orbit')
    
    # 軌道の開始点と終了点をマーク
    plt.plot(df['X_MSO'].iloc[0], df['Y_MSO'].iloc[0], 'go', markersize=6, label='Start Point')
    plt.plot(df['X_MSO'].iloc[-1], df['Y_MSO'].iloc[-1], 'mo', markersize=6, label='End Point')
    
    # 原点（水星中心）をマーク
    plt.plot(0, 0, 'ko', markersize=3, alpha=0.5)
    
    # Generate title based on data period
    start_date = df['datetime'].min().strftime('%Y-%m-%d')
    end_date = df['datetime'].max().strftime('%Y-%m-%d')
    if start_date == end_date:
        title_date = start_date
    else:
        title_date = f"{start_date} to {end_date}"
    
    plt.xlabel('X_MSO (km)')
    plt.ylabel('Y_MSO (km)')
    plt.title(f'MESSENGER Orbit - X-Y Plane (Mercury Centered)\n{title_date}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Set axis limits
    plt.xlim(x_min_plot, x_max_plot)
    plt.ylim(y_min_plot, y_max_plot)
    plt.axis('equal')
    
    if save_plot:
        plt.savefig('messenger_orbit_xy.png', dpi=300, bbox_inches='tight')
        print("Orbit plot (X-Y plane) saved as 'messenger_orbit_xy.png'")
    
    # plt.show()

def plot_orbit_xz(df, save_plot=True):
    """
    x-z平面での軌道プロット（水星中心）
    
    Parameters:
    df (pandas.DataFrame): データフレーム
    save_plot (bool): プロットを保存するかどうか
    """
    plt.figure(figsize=(12, 10))
    
    # 水星の半径（km）
    mercury_radius = 2439.7
    
    # データの範囲を取得して軸の範囲を設定
    x_min, x_max = df['X_MSO'].min(), df['X_MSO'].max()
    z_min, z_max = df['Z_MSO'].min(), df['Z_MSO'].max()
    
    # 軸の範囲を少し拡張して水星が見えるようにする
    margin = max(mercury_radius * 0.5, 1000)  # 少なくとも1000kmのマージン
    x_min_plot = min(x_min - margin, -mercury_radius * 1.2)
    x_max_plot = max(x_max + margin, mercury_radius * 1.2)
    z_min_plot = min(z_min - margin, -mercury_radius * 1.2)
    z_max_plot = max(z_max + margin, mercury_radius * 1.2)
    
    # 水星を黒く塗りつぶされた円で表示（最初に描画）
    theta = np.linspace(0, 2*np.pi, 100)
    x_mercury = mercury_radius * np.cos(theta)
    z_mercury = mercury_radius * np.sin(theta)
    plt.fill(x_mercury, z_mercury, 'black', alpha=0.8, label='Mercury')
    plt.plot(x_mercury, z_mercury, 'k-', linewidth=1)
    
    # 軌道プロット（水星の上に描画）
    plt.plot(df['X_MSO'], df['Z_MSO'], 'g-', linewidth=0.5, alpha=0.7, label='MESSENGER Orbit')
    
    # 軌道の開始点と終了点をマーク
    plt.plot(df['X_MSO'].iloc[0], df['Z_MSO'].iloc[0], 'go', markersize=6, label='Start Point')
    plt.plot(df['X_MSO'].iloc[-1], df['Z_MSO'].iloc[-1], 'mo', markersize=6, label='End Point')
    
    # 原点（水星中心）をマーク
    plt.plot(0, 0, 'ko', markersize=3, alpha=0.5)
    
    # Generate title based on data period
    start_date = df['datetime'].min().strftime('%Y-%m-%d')
    end_date = df['datetime'].max().strftime('%Y-%m-%d')
    if start_date == end_date:
        title_date = start_date
    else:
        title_date = f"{start_date} to {end_date}"
    
    plt.xlabel('X_MSO (km)')
    plt.ylabel('Z_MSO (km)')
    plt.title(f'MESSENGER Orbit - X-Z Plane (Mercury Centered)\n{title_date}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Set axis limits
    plt.xlim(x_min_plot, x_max_plot)
    plt.ylim(z_min_plot, z_max_plot)
    plt.axis('equal')
    
    if save_plot:
        plt.savefig('messenger_orbit_xz.png', dpi=300, bbox_inches='tight')
        print("Orbit plot (X-Z plane) saved as 'messenger_orbit_xz.png'")
    
    # plt.show()