from enum import Enum

class LoggerType(Enum):
    """Logger type."""

    FILE = "file"
    """File logger."""
    CONSOLE = "console"
    """Console logger."""
    PROGRESS = "progress"
    """Progress logger."""
    NONE = "none"
    """No logger."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class LoggerLevel(Enum):
    """Logger level."""

    DEBUG = "DEBUG"
    """Debug level."""
    INFO = "INFO"
    """Info level."""
    WARNING = "WARNING"
    """Warning level."""
    ERROR = "ERROR"
    """Error level."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'
    
    @classmethod
    def from_str(cls, level_str: str) -> "LoggerLevel":
        try:
            return cls[level_str.strip().upper()]
        except KeyError:
            raise ValueError(f"Invalid logger level: {level_str}")


LOG_LEVELS = {
    LoggerLevel.DEBUG: 10,
    LoggerLevel.INFO: 20,
    LoggerLevel.WARNING: 30,
    LoggerLevel.ERROR: 40,
}