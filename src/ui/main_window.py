from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSlider, QCheckBox,
    QSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import time

from core.screen_capture import ScreenCapture
from core.video_encoder import VideoEncoder
from utils.config import ConfigManager
from utils.logger import setup_logger

class RecordingWorker(QThread):
    """录制工作线程"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    frame_count = pyqtSignal(int)
    
    def __init__(self, fps: int, format_type: str, output_dir: str):
        super().__init__()
        self.fps = fps
        self.format_type = format_type
        self.output_dir = output_dir
        self.is_running = False
        self.screen_capture = None
        self.encoder = None
    
    def run(self):
        try:
            self.is_running = True
            self.screen_capture = ScreenCapture(fps=self.fps)
            
            # 获取分辨率
            resolution = self.screen_capture.get_resolution()
            
            # 创建编码器
            self.encoder = VideoEncoder(
                output_path=self.output_dir,
                fps=self.fps,
                frame_size=resolution,
                codec=self.format_type
            )
            
            # 开始捕获
            self.screen_capture.start()
            
            frame_count = 0
            while self.is_running:
                frame = self.screen_capture.get_frame(timeout=1.0)
                if frame is not None:
                    self.encoder.write_frame(frame)
                    frame_count += 1
                    self.frame_count.emit(frame_count)
            
            # 清理资源
            self.screen_capture.stop()
            self.encoder.release()
            self.finished.emit()
        
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    """
    主应用窗口
    """
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.logger = setup_logger()
        self.recording_worker = None
        self.is_recording = False
        self.record_start_time = None
        
        self.setWindowTitle('Luping - 屏幕录制工具')
        self.setGeometry(100, 100, 600, 450)
        
        self.init_ui()
        self.setup_timers()
    
    def init_ui(self):
        """
        初始化 UI 组件
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel('屏幕录制工具')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # 录制模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('录制模式:'))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['全屏', '区域', '窗口'])
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)
        
        # 帧率（FPS）
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel('帧率 (FPS):'))
        self.fps_spin = QSpinBox()
        self.fps_spin.setValue(self.config.get('recording.fps', 30))
        self.fps_spin.setRange(15, 60)
        fps_layout.addWidget(self.fps_spin)
        main_layout.addLayout(fps_layout)
        
        # 质量
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('质量:'))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setValue(self.config.get('recording.quality', 85))
        self.quality_slider.setRange(1, 100)
        self.quality_label = QLabel('85')
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(str(v))
        )
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        main_layout.addLayout(quality_layout)
        
        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('输出格式:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP4', 'WebM', 'AVI'])
        format_layout.addWidget(self.format_combo)
        main_layout.addLayout(format_layout)
        
        # 音频选项
        audio_layout = QHBoxLayout()
        self.system_audio_check = QCheckBox('系统音频')
        self.system_audio_check.setChecked(self.config.get('audio.system_audio', True))
        self.microphone_check = QCheckBox('麦克风')
        self.microphone_check.setChecked(self.config.get('audio.microphone', False))
        audio_layout.addWidget(self.system_audio_check)
        audio_layout.addWidget(self.microphone_check)
        main_layout.addLayout(audio_layout)
        
        # 计时器显示
        self.timer_label = QLabel('00:00:00')
        timer_font = QFont()
        timer_font.setPointSize(14)
        timer_font.setBold(True)
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.timer_label)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton('开始录制')
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setMinimumHeight(40)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('停止录制')
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        # 保存位置按钮
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('保存位置:'))
        self.output_label = QLabel(self.config.get('output.directory', str(Path.home() / 'Videos')))
        output_layout.addWidget(self.output_label, 1)
        self.browse_btn = QPushButton('浏览...')
        self.browse_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.browse_btn)
        main_layout.addLayout(output_layout)
        
        # 状态标签
        self.status_label = QLabel('就绪')
        status_font = QFont()
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        main_widget.setLayout(main_layout)
    
    def setup_timers(self):
        """
        ���置应用计时器
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
    
    def select_output_dir(self):
        """
        选择输出目录
        """
        current_dir = self.config.get('output.directory', str(Path.home() / 'Videos'))
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            '选择保存位置',
            current_dir
        )
        
        if selected_dir:
            self.config.set('output.directory', selected_dir)
            self.output_label.setText(selected_dir)
            self.logger.info(f"输出目录已设置为: {selected_dir}")
    
    def start_recording(self):
        """
        开始录制
        """
        self.logger.info("开始录制...")
        
        # 获取输出目录
        output_dir = self.config.get('output.directory', str(Path.home() / 'Videos'))
        format_map = {'MP4': 'mp4', 'WebM': 'webm', 'AVI': 'avi'}
        format_type = format_map[self.format_combo.currentText()]
        
        # 启动工作线程
        self.recording_worker = RecordingWorker(
            fps=self.fps_spin.value(),
            format_type=format_type,
            output_dir=output_dir
        )
        self.recording_worker.finished.connect(self.on_recording_finished)
        self.recording_worker.error.connect(self.on_recording_error)
        self.recording_worker.start()
        
        # 更新 UI
        self.is_recording = True
        self.record_start_time = time.time()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.mode_combo.setEnabled(False)
        self.fps_spin.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.status_label.setText('录制中...')
        self.timer.start(1000)  # 每秒更新一次
        self.logger.info("录制已启动")
    
    def stop_recording(self):
        """
        停止录制
        """
        self.logger.info("停止录制...")
        self.is_recording = False
        self.timer.stop()
        
        if self.recording_worker:
            self.recording_worker.stop()
            self.recording_worker.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.mode_combo.setEnabled(True)
        self.fps_spin.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.status_label.setText('录制已停止')
        self.logger.info("录制已停止")
    
    def update_timer(self):
        """
        更新计时器显示
        """
        if self.is_recording and self.record_start_time:
            elapsed = int(time.time() - self.record_start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def on_recording_finished(self):
        """
        处理录制完成信号
        """
        self.status_label.setText('✓ 录制完成！')
        self.logger.info("录制成功完成")
    
    def on_recording_error(self, error_msg: str):
        """
        处理录制错误信号
        """
        self.status_label.setText(f'✗ 错误: {error_msg}')
        self.logger.error(f"录制错误: {error_msg}")
        self.stop_recording()
    
    def closeEvent(self, event):
        """
        处理窗口关闭事件
        """
        if self.is_recording:
            self.stop_recording()
        
        # 保存配置
        self.config.set('recording.fps', self.fps_spin.value())
        self.config.set('recording.quality', self.quality_slider.value())
        self.config.set('audio.system_audio', self.system_audio_check.isChecked())
        self.config.set('audio.microphone', self.microphone_check.isChecked())
        
        event.accept()
