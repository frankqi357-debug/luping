import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name='luping', log_level=logging.INFO):
    """
    Setup logger for the application
    
    Args:
        name: Logger name
        log_level: Logging level (default: INFO)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / '.luping' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file handler
    log_file = log_dir / f"luping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
