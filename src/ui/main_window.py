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
    """Worker thread for recording"""
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
            
            # Get resolution
            resolution = self.screen_capture.get_resolution()
            
            # Create encoder
            self.encoder = VideoEncoder(
                output_path=self.output_dir,
                fps=self.fps,
                frame_size=resolution,
                codec=self.format_type
            )
            
            # Start capture
            self.screen_capture.start()
            
            frame_count = 0
            while self.is_running:
                frame = self.screen_capture.get_frame(timeout=1.0)
                if frame is not None:
                    self.encoder.write_frame(frame)
                    frame_count += 1
                    self.frame_count.emit(frame_count)
            
            # Cleanup
            self.screen_capture.stop()
            self.encoder.release()
            self.finished.emit()
        
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    """
    Main application window
    """
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.logger = setup_logger()
        self.recording_worker = None
        self.is_recording = False
        self.record_start_time = None
        
        self.setWindowTitle('Luping - Screen Recorder')
        self.setGeometry(100, 100, 600, 400)
        
        self.init_ui()
        self.setup_timers()
    
    def init_ui(self):
        """
        Initialize UI components
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('Screen Recorder')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Recording Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('Recording Mode:'))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Fullscreen', 'Region', 'Window'])
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)
        
        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel('FPS:'))
        self.fps_spin = QSpinBox()
        self.fps_spin.setValue(self.config.get('recording.fps', 30))
        self.fps_spin.setRange(15, 60)
        fps_layout.addWidget(self.fps_spin)
        main_layout.addLayout(fps_layout)
        
        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('Quality:'))
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
        
        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Format:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP4', 'WebM', 'AVI'])
        format_layout.addWidget(self.format_combo)
        main_layout.addLayout(format_layout)
        
        # Audio options
        audio_layout = QHBoxLayout()
        self.system_audio_check = QCheckBox('System Audio')
        self.system_audio_check.setChecked(self.config.get('audio.system_audio', True))
        self.microphone_check = QCheckBox('Microphone')
        self.microphone_check.setChecked(self.config.get('audio.microphone', False))
        audio_layout.addWidget(self.system_audio_check)
        audio_layout.addWidget(self.microphone_check)
        main_layout.addLayout(audio_layout)
        
        # Timer display
        self.timer_label = QLabel('00:00:00')
        timer_font = QFont()
        timer_font.setPointSize(12)
        self.timer_label.setFont(timer_font)
        main_layout.addWidget(self.timer_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start Recording')
        self.start_btn.clicked.connect(self.start_recording)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('Stop Recording')
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel('Ready')
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        main_widget.setLayout(main_layout)
    
    def setup_timers(self):
        """
        Setup application timers
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
    
    def start_recording(self):
        """
        Start recording
        """
        self.logger.info("Starting recording...")
        
        # Get output directory
        output_dir = self.config.get('output.directory', str(Path.home() / 'Videos'))
        format_map = {'MP4': 'mp4', 'WebM': 'webm', 'AVI': 'avi'}
        format_type = format_map[self.format_combo.currentText()]
        
        # Start worker thread
        self.recording_worker = RecordingWorker(
            fps=self.fps_spin.value(),
            format_type=format_type,
            output_dir=output_dir
        )
        self.recording_worker.finished.connect(self.on_recording_finished)
        self.recording_worker.error.connect(self.on_recording_error)
        self.recording_worker.start()
        
        # Update UI
        self.is_recording = True
        self.record_start_time = time.time()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText('Recording...')
        self.timer.start(1000)  # Update every second
        self.logger.info("Recording started")
    
    def stop_recording(self):
        """
        Stop recording
        """
        self.logger.info("Stopping recording...")
        self.is_recording = False
        self.timer.stop()
        
        if self.recording_worker:
            self.recording_worker.stop()
            self.recording_worker.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText('Recording stopped')
        self.logger.info("Recording stopped")
    
    def update_timer(self):
        """
        Update timer display
        """
        if self.is_recording and self.record_start_time:
            elapsed = int(time.time() - self.record_start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def on_recording_finished(self):
        """
        Handle recording finished signal
        """
        self.status_label.setText('Recording completed!')
        self.logger.info("Recording completed successfully")
    
    def on_recording_error(self, error_msg: str):
        """
        Handle recording error signal
        """
        self.status_label.setText(f'Error: {error_msg}')
        self.logger.error(f"Recording error: {error_msg}")
        self.stop_recording()
    
    def closeEvent(self, event):
        """
        Handle window close event
        """
        if self.is_recording:
            self.stop_recording()
        
        # Save configuration
        self.config.set('recording.fps', self.fps_spin.value())
        self.config.set('recording.quality', self.quality_slider.value())
        self.config.set('audio.system_audio', self.system_audio_check.isChecked())
        self.config.set('audio.microphone', self.microphone_check.isChecked())
        
        event.accept()
