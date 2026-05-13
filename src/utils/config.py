import json
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """
    Manages application configuration
    """
    
    DEFAULT_CONFIG = {
        'recording': {
            'mode': 'fullscreen',  # fullscreen, region, window
            'fps': 30,
            'format': 'mp4',
            'quality': 85,
            'resolution': (1920, 1080),
        },
        'audio': {
            'system_audio': True,
            'microphone': False,
            'volume': 100,
        },
        'ui': {
            'theme': 'light',
            'window_size': (600, 400),
        },
        'output': {
            'directory': str(Path.home() / 'Videos'),
        }
    }
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path.home() / '.luping' / 'config.json'
        
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> None:
        """
        Save configuration to file
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation: 'recording.fps')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation: 'recording.fps')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
