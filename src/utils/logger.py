"""
Loguru Telemetry Stream Setup
Configures highly readable, multi-colored execution traces for console logs and files.
"""

import sys
from loguru import logger
from pathlib import Path

def setup_logger(log_file: str = "./logs/workspace_agent.log", log_level: str = "INFO"):
    """Binds structured outputs to active stdout streams and file handles cleanly."""
    logger.remove()  # Strip default raw format handler
    
    # 1. Vibrant, scannable terminal format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # 2. Permanent production trace files for telemetry audits
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        backtrace=True,
        diagnose=True
    )

def get_logger():
    """Fetches global active logging instance cleanly."""
    return logger