# app/calculator_config.py (Full Code)

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation # Import InvalidOperation
from numbers import Number
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

# Load environment variables from a .env file into the program's environment
load_dotenv()


def get_project_root() -> Path:
    """
    Get the project root directory.
    """
    current_file = Path(__file__)
    return current_file.parent.parent

# Helper for robust Decimal parsing from environment
def _parse_decimal_from_env(env_var: str, default_value: str) -> Decimal:
    value_str = os.getenv(env_var, default_value)
    try:
        return Decimal(value_str)
    except InvalidOperation as e:
        raise ConfigurationError(f"Environment variable '{env_var}' has an invalid number format: '{value_str}'") from e

# Helper for robust boolean parsing from environment
def _parse_bool_from_env(env_var: str, default_value: str) -> bool:
    value_str = os.getenv(env_var, default_value).lower()
    # Define a set of "truthy" strings
    true_strings = {'true', '1', 'yes', 'on'}
    return value_str in true_strings


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.
    """
    base_dir: Path = field(
        default_factory=lambda: Path(os.getenv('CALCULATOR_BASE_DIR', str(get_project_root()))).resolve()
    )

    log_dir_name: str = field(default_factory=lambda: os.getenv('CALCULATOR_LOG_DIR', 'logs'))
    log_file_name: str = field(default_factory=lambda: os.getenv('CALCULATOR_LOG_FILE', 'calculator.log'))
    
    history_dir_name: str = field(default_factory=lambda: os.getenv('CALCULATOR_HISTORY_DIR', 'history'))
    history_file_name: str = field(default_factory=lambda: os.getenv('CALCULATOR_HISTORY_FILE', 'calculator_history.csv'))

    max_history_size: int = field(default_factory=lambda: int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', '1000')))
    auto_save: bool = field(default_factory=lambda: _parse_bool_from_env('CALCULATOR_AUTO_SAVE', 'true'))

    precision: int = field(default_factory=lambda: int(os.getenv('CALCULATOR_PRECISION', '10')))
    max_input_value: Decimal = field(default_factory=lambda: _parse_decimal_from_env('CALCULATOR_MAX_INPUT_VALUE', '1e999'))
    
    default_encoding: str = field(default_factory=lambda: os.getenv('CALCULATOR_DEFAULT_ENCODING', 'utf-8'))

    log_dir: Path = field(init=False, repr=False)
    log_file: Path = field(init=False, repr=False)
    history_dir: Path = field(init=False, repr=False)
    history_file: Path = field(init=False, repr=False)

    def __post_init__(self):
        """
        Post-initialization processing to resolve paths and perform initial validation.
        """
        self.log_dir = self.base_dir / self.log_dir_name
        self.log_file = self.log_dir / self.log_file_name
        self.history_dir = self.base_dir / self.history_dir_name
        self.history_file = self.history_dir / self.history_file_name
        
        self.validate()

    def validate(self):
        """
        Validate configuration parameters.
        """
        if not isinstance(self.max_history_size, int) or self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be a positive integer.")
        if not isinstance(self.precision, int) or self.precision < 0:
            raise ConfigurationError("precision must be a non-negative integer.")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive.")
        
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.history_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e: # pragma: no cover
            raise ConfigurationError(f"Failed to create directory specified in config: {e}") # pragma: no cover