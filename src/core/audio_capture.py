import sounddevice as sd
import numpy as np
from threading import Thread, Event
from queue import Queue
import time

class AudioCapture:
    """
    Captures audio from system and/or microphone
    """
    
    def __init__(self, sample_rate: int = 44100, channels: int = 2):
        """
        Initialize audio capture
        
        Args:
            sample_rate: Audio sample rate (default: 44100 Hz)
            channels: Number of channels (default: 2 for stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_queue = Queue(maxsize=100)
        self.is_capturing = False
        self.capture_thread = None
        self.stop_event = Event()
    
    def list_devices(self) -> list:
        """
        List available audio devices
        
        Returns:
            List of device info dictionaries
        """
        return sd.query_devices()
    
    def start(self, device: int = None) -> None:
        """
        Start capturing audio
        
        Args:
            device: Device ID (None for default)
        """
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.stop_event.clear()
        self.capture_thread = Thread(
            target=self._capture_loop,
            args=(device,),
            daemon=True
        )
        self.capture_thread.start()
    
    def stop(self) -> None:
        """
        Stop capturing audio
        """
        self.is_capturing = False
        self.stop_event.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
    
    def _capture_loop(self, device: int = None) -> None:
        """
        Main audio capture loop
        """
        try:
            def audio_callback(indata, frames, time_info, status):
                if status:
                    print(f"Audio error: {status}")
                
                # Put audio data in queue
                if not self.audio_queue.full():
                    self.audio_queue.put(indata.copy())
            
            with sd.InputStream(
                device=device,
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=int(self.sample_rate / 30),  # ~30fps
                latency='low'
            ):
                while self.is_capturing and not self.stop_event.is_set():
                    time.sleep(0.1)
        
        except Exception as e:
            print(f"Error in audio capture: {e}")
    
    def get_audio_chunk(self, timeout: float = 1.0) -> np.ndarray:
        """
        Get next audio chunk
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Audio data as numpy array, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except:
            return None
