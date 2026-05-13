import cv2
import numpy as np
from pathlib import Path
import os

class VideoEncoder:
    """
    Encodes frames to video file
    """
    
    CODEC_MAP = {
        'mp4': cv2.VideoWriter_fourcc(*'mp4v'),
        'webm': cv2.VideoWriter_fourcc(*'VP90'),
        'avi': cv2.VideoWriter_fourcc(*'XVID'),
    }
    
    EXT_MAP = {
        'mp4': '.mp4',
        'webm': '.webm',
        'avi': '.avi',
    }
    
    def __init__(self, output_path: str, fps: int = 30, 
                 frame_size: tuple = (1920, 1080), codec: str = 'mp4'):
        """
        Initialize video encoder
        
        Args:
            output_path: Output file path (can be directory)
            fps: Frames per second
            frame_size: Frame size (width, height)
            codec: Video codec ('mp4', 'webm', 'avi')
        """
        self.fps = fps
        self.frame_size = frame_size
        self.codec = codec
        
        # If output_path is a directory, generate filename
        output_path = Path(output_path)
        if output_path.is_dir() or not output_path.suffix:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"luping_{timestamp}{self.EXT_MAP.get(codec, '.mp4')}"
            output_path = output_path / filename
        
        self.output_path = str(output_path)
        
        # Create output directory if it doesn't exist
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize VideoWriter
        fourcc = self.CODEC_MAP.get(codec, cv2.VideoWriter_fourcc(*'mp4v'))
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            fps,
            frame_size
        )
        
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open video writer for {self.output_path}")
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Write a frame to video
        
        Args:
            frame: Frame as numpy array (BGR format)
        
        Returns:
            True if successful, False otherwise
        """
        if frame.shape[:2] != self.frame_size[::-1]:
            # Resize frame if needed
            frame = cv2.resize(frame, self.frame_size)
        
        return self.writer.write(frame)
    
    def release(self) -> None:
        """
        Release video writer and finalize video file
        """
        if self.writer:
            self.writer.release()
    
    def get_file_size(self) -> int:
        """
        Get output file size in bytes
        
        Returns:
            File size, or 0 if file doesn't exist
        """
        if Path(self.output_path).exists():
            return os.path.getsize(self.output_path)
        return 0
    
    def __del__(self):
        """
        Cleanup
        """
        self.release()
