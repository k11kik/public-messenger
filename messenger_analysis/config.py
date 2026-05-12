import platform

system = platform.system()

# mac
if system == 'Darwin':
    CONFIG = {
        'root': '/Volumes/SSD4T',
        'data': '/Volumes/SSD4T',
        'main_dir': '/Volumes/SSD4T/messenger'
    }
# win
elif system == 'Windows':
    CONFIG = {
        'root': r"D:/",
        'data': r"E:/",
        'main_dir': r"E:\messenger"
    }
else:
    CONFIG = {
        ''
    }

