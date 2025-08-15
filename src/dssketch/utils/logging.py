"""
Logging configuration for DSSketch.

Provides centralized logging that outputs to files in the conversion directory
with filename format: {dssketch_name}_{timestamp}.log
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class DSSketchLogger:
    """Centralized logger for DSSketch operations."""

    _logger: Optional[logging.Logger] = None
    _current_log_file: Optional[Path] = None

    @classmethod
    def setup_logger(cls, file_path: str, log_level: int = logging.INFO) -> logging.Logger:
        """
        Setup logger for a conversion operation.

        Args:
            file_path: Path to the file being converted (DSSketch or DesignSpace)
            log_level: Logging level (default: INFO)

        Returns:
            Configured logger instance
        """
        # Get base filename without extension
        input_path = Path(file_path)
        base_name = input_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create log filename
        log_filename = f"{base_name}_{timestamp}.log"
        log_path = input_path.parent / log_filename

        # Remove existing handlers if logger already exists
        if cls._logger:
            for handler in cls._logger.handlers[:]:
                cls._logger.removeHandler(handler)
                handler.close()

        # Create logger
        cls._logger = logging.getLogger('dssketch')
        cls._logger.setLevel(log_level)

        # Create file handler
        file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        file_handler.setLevel(log_level)

        # Create console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        cls._current_log_file = log_path

        # Log startup message
        cls._logger.info(f"DSSketch logging started for file: {file_path}")
        cls._logger.info(f"Log file: {log_path}")

        return cls._logger

    @classmethod
    def get_logger(cls) -> Optional[logging.Logger]:
        """Get the current logger instance."""
        return cls._logger

    @classmethod
    def get_log_file_path(cls) -> Optional[Path]:
        """Get the current log file path."""
        return cls._current_log_file

    @classmethod
    def info(cls, message: str) -> None:
        """Log info message."""
        if cls._logger:
            cls._logger.info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """Log warning message."""
        if cls._logger:
            cls._logger.warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        """Log error message."""
        if cls._logger:
            cls._logger.error(message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Log debug message."""
        if cls._logger:
            cls._logger.debug(message)

    @classmethod
    def success(cls, message: str) -> None:
        """Log success message (using info level)."""
        if cls._logger:
            cls._logger.info(f"✅ {message}")

    @classmethod
    def cleanup(cls) -> None:
        """Clean up logger resources."""
        if cls._logger:
            for handler in cls._logger.handlers[:]:
                cls._logger.removeHandler(handler)
                handler.close()
            cls._logger = None
            cls._current_log_file = None


# Convenience functions for backward compatibility
def setup_logging(file_path: str, log_level: int = logging.INFO) -> logging.Logger:
    """Setup logging for a conversion operation."""
    return DSSketchLogger.setup_logger(file_path, log_level)


def get_logger() -> Optional[logging.Logger]:
    """Get the current logger instance."""
    return DSSketchLogger.get_logger()


def log_info(message: str) -> None:
    """Log info message."""
    DSSketchLogger.info(message)


def log_warning(message: str) -> None:
    """Log warning message."""
    DSSketchLogger.warning(message)


def log_error(message: str) -> None:
    """Log error message."""
    DSSketchLogger.error(message)


def log_debug(message: str) -> None:
    """Log debug message."""
    DSSketchLogger.debug(message)


def log_success(message: str) -> None:
    """Log success message."""
    DSSketchLogger.success(message)