import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_logger

if __name__ == "__main__":
    # 初始化日志系统
    logger = setup_logger()
    logger.info("Starting Luping Screen Recorder...")
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    logger.info("UI loaded successfully")
    sys.exit(app.exec())
