from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QSlider, QCheckBox, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    """
    设置对话框窗口
    """
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle('设置')
        self.setGeometry(200, 200, 400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """
        初始化 UI
        """
        layout = QVBoxLayout()
        
        # 帧率（FPS）设置
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel('帧率 (FPS):'))
        self.fps_spin = QSpinBox()
        self.fps_spin.setValue(self.config.get('recording.fps', 30))
        self.fps_spin.setRange(15, 60)
        fps_layout.addWidget(self.fps_spin)
        layout.addLayout(fps_layout)
        
        # 质量设置
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('质量:'))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setValue(self.config.get('recording.quality', 85))
        self.quality_slider.setRange(1, 100)
        quality_layout.addWidget(self.quality_slider)
        layout.addLayout(quality_layout)
        
        # 格式设置
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('输出格式:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP4', 'WebM', 'AVI'])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # 音频设置
        self.system_audio_check = QCheckBox('系统音频')
        self.system_audio_check.setChecked(self.config.get('audio.system_audio', True))
        layout.addWidget(self.system_audio_check)
        
        self.microphone_check = QCheckBox('麦克风')
        self.microphone_check.setChecked(self.config.get('audio.microphone', False))
        layout.addWidget(self.microphone_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
