# app/calculator_config.py

import os
from dotenv import load_dotenv

class AppConfig:
    """
    Manages application configuration settings loaded from environment variables
    or .env file, providing default values and basic validation.
    """
    def __init__(self):
        # Loads environment variables from .env file
        
        self.load_config()

    def load_config(self):
        """Loads configuration from environment variables."""
        # Base Directories
        self.LOG_DIR = os.getenv("CALCULATOR_LOG_DIR", "logs")
        self.HISTORY_DIR = os.getenv("CALCULATOR_HISTORY_DIR", "history")

        #History Settings
        self.MAX_HISTORY_SIZE = int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100"))
        self.AUTO_SAVE = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() == "true"

        # Calculation Settings
        self.PRECISION = int(os.getenv("CALCULATOR_PRECISION", "4"))
        self.MAX_INPUT_VALUE = float(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e12")) # Default to 1 trillion
        self.DEFAULT_ENCODING = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

        self._validate_config()

    def _validate_config(self):
        """Validates loaded configuration values."""
        if not isinstance(self.MAX_HISTORY_SIZE, int) or self.MAX_HISTORY_SIZE < 0:
            raise ValueError("CALCULATOR_MAX_HISTORY_SIZE must be a non-negative integer.")
        if not isinstance(self.PRECISION, int) or self.PRECISION < 0:
            raise ValueError("CALCULATOR_PRECISION must be a non-negative integer.")
        if not isinstance(self.MAX_INPUT_VALUE, (int, float)) or self.MAX_INPUT_VALUE < 0:
            raise ValueError("CALCULATOR_MAX_INPUT_VALUE must be a non-negative number.")
        if not isinstance(self.LOG_DIR, str) or not self.LOG_DIR:
            raise ValueError("CALCULATOR_LOG_DIR cannot be empty.")
        if not isinstance(self.HISTORY_DIR, str) or not self.HISTORY_DIR:
            raise ValueError("CALCULATOR_HISTORY_DIR cannot be empty.")


config = AppConfig()