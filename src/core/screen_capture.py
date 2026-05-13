import cv2
import numpy as np
from mss import mss
from threading import Thread, Event
from queue import Queue
import time

class ScreenCapture:
    """
    Captures screen frames at specified FPS
    """
    
    def __init__(self, fps: int = 30, region: tuple = None):
        """
        Initialize screen capture
        
        Args:
            fps: Frames per second
            region: (x, y, width, height) tuple for region capture. None for fullscreen.
        """
        self.fps = fps
        self.region = region
        self.frame_delay = 1.0 / fps
        self.frame_queue = Queue(maxsize=30)
        self.is_capturing = False
        self.capture_thread = None
        self.stop_event = Event()
        self.sct = mss()
    
    def get_monitor_info(self) -> dict:
        """
        Get monitor information
        
        Returns:
            Monitor info dictionary
        """
        monitors = self.sct.monitors
        return monitors[1] if len(monitors) > 1 else monitors[0]
    
    def start(self) -> None:
        """
        Start capturing frames
        """
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.stop_event.clear()
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def stop(self) -> None:
        """
        Stop capturing frames
        """
        self.is_capturing = False
        self.stop_event.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
    
    def _capture_loop(self) -> None:
        """
        Main capture loop
        """
        while self.is_capturing and not self.stop_event.is_set():
            try:
                start_time = time.time()
                
                # Capture frame
                if self.region:
                    x, y, w, h = self.region
                    frame = self.sct.grab({'top': y, 'left': x, 'width': w, 'height': h})
                else:
                    monitor = self.get_monitor_info()
                    frame = self.sct.grab(monitor)
                
                # Convert to numpy array
                frame_np = np.array(frame)
                # Convert BGRA to BGR
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)
                
                # Put frame in queue (drop if queue is full)
                if not self.frame_queue.full():
                    self.frame_queue.put(frame_bgr)
                
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, self.frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            except Exception as e:
                print(f"Error in capture loop: {e}")
                continue
    
    def get_frame(self, timeout: float = 1.0) -> np.ndarray:
        """
        Get next captured frame
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Frame as numpy array, or None if timeout
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except:
            return None
    
    def get_resolution(self) -> tuple:
        """
        Get capture resolution
        
        Returns:
            (width, height) tuple
        """
        if self.region:
            return (self.region[2], self.region[3])
        else:
            monitor = self.get_monitor_info()
            return (monitor['width'], monitor['height'])
