# tests/test_config.py (Full Code)

import os
from pathlib import Path
import pytest
from decimal import Decimal
from tempfile import TemporaryDirectory # Import TemporaryDirectory

from app.calculator_config import CalculatorConfig, get_project_root # Import get_project_root
from app.exceptions import ConfigurationError

# Helper to clear environment variables for clean tests
@pytest.fixture(autouse=True)
def clean_env():
    # Save original environment variables
    original_env = os.environ.copy()
    yield
    # Restore original environment variables after test
    os.environ.clear()
    os.environ.update(original_env)

# Helper function to clear specific environment variables
def clear_env_vars(*args):
    for var in args:
        if var in os.environ:
            del os.environ[var]

# Test default configuration values
def test_default_configuration():
    clear_env_vars(
        'CALCULATOR_MAX_HISTORY_SIZE', 'CALCULATOR_AUTO_SAVE', 'CALCULATOR_PRECISION',
        'CALCULATOR_MAX_INPUT_VALUE', 'CALCULATOR_DEFAULT_ENCODING',
        'CALCULATOR_LOG_DIR', 'CALCULATOR_LOG_FILE', 'CALCULATOR_HISTORY_DIR', 'CALCULATOR_HISTORY_FILE',
        'CALCULATOR_BASE_DIR' # Clear base_dir as well for default_factory to kick in
    )
    config = CalculatorConfig()
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1e999")
    assert config.default_encoding == 'utf-8'
    # Path assertions should be relative to get_project_root()
    project_root = get_project_root()
    assert config.log_dir == project_root / "logs"
    assert config.log_file == project_root / "logs" / "calculator.log"
    assert config.history_dir == project_root / "history"
    assert config.history_file == project_root / "history" / "calculator_history.csv"


# Test validation of configuration parameters
def test_invalid_max_history_size():
    with pytest.raises(ConfigurationError, match="max_history_size must be a positive integer."):
        CalculatorConfig(max_history_size=-1)
    with pytest.raises(ConfigurationError, match="max_history_size must be a positive integer."):
        CalculatorConfig(max_history_size=0)

def test_invalid_precision():
    with pytest.raises(ConfigurationError, match="precision must be a non-negative integer."):
        CalculatorConfig(precision=-1)

def test_invalid_max_input_value():
    # Test with negative/zero
    with pytest.raises(ConfigurationError, match="max_input_value must be positive."):
        CalculatorConfig(max_input_value=Decimal("-1"))
    with pytest.raises(ConfigurationError, match="max_input_value must be positive."):
        CalculatorConfig(max_input_value=Decimal("0"))
    # Test with invalid string from env var
    with pytest.raises(ConfigurationError, match="has an invalid number format"):
        os.environ['CALCULATOR_MAX_INPUT_VALUE'] = 'not_a_number'
        CalculatorConfig()


# Test environment variable overrides
def test_env_var_override():
    os.environ['CALCULATOR_MAX_HISTORY_SIZE'] = '500'
    os.environ['CALCULATOR_PRECISION'] = '8'
    os.environ['CALCULATOR_MAX_INPUT_VALUE'] = '1000'
    os.environ['CALCULATOR_DEFAULT_ENCODING'] = 'utf-16'
    os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
    
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'

# Test boolean auto_save parsing from environment variables
def test_auto_save_env_var_true():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'true'
    config = CalculatorConfig()
    assert config.auto_save is True

def test_auto_save_env_var_one():
    os.environ['CALCULATOR_AUTO_SAVE'] = '1'
    config = CalculatorConfig()
    assert config.auto_save is True

def test_auto_save_env_var_false():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
    config = CalculatorConfig()
    assert config.auto_save is False

def test_auto_save_env_var_zero():
    os.environ['CALCULATOR_AUTO_SAVE'] = '0'
    config = CalculatorConfig()
    assert config.auto_save is False

def test_auto_save_env_var_invalid_string():
    # 'yEs' lowercases to 'yes', which is now in `true_strings` in _parse_bool_from_env
    os.environ['CALCULATOR_AUTO_SAVE'] = 'yEs' 
    config = CalculatorConfig()
    assert config.auto_save is True 
    
    os.environ['CALCULATOR_AUTO_SAVE'] = 'no' 
    config = CalculatorConfig()
    assert config.auto_save is False # 'no' is not in true_strings, so it evaluates to False

# Test path properties using temporary directories
@pytest.mark.parametrize("dir_env_var, file_env_var, expected_dir_name, expected_file_name", [
    ('CALCULATOR_LOG_DIR', 'CALCULATOR_LOG_FILE', 'logs', 'calculator.log'),
    ('CALCULATOR_HISTORY_DIR', 'CALCULATOR_HISTORY_FILE', 'history', 'calculator_history.csv'),
])
def test_path_properties_from_env(dir_env_var, file_env_var, expected_dir_name, expected_file_name):
    with TemporaryDirectory() as tmp_dir_str:
        tmp_base_dir = Path(tmp_dir_str)
        # Set specific environment variables for this test
        os.environ[dir_env_var] = "custom_dir"
        os.environ[file_env_var] = "custom_file.txt"
        os.environ['CALCULATOR_BASE_DIR'] = str(tmp_base_dir) # Ensure base_dir is also env var controlled
        
        config = CalculatorConfig() # Instantiate without passing base_dir directly

        # Assert resolved paths
        if "LOG" in dir_env_var: # Check if it's log path
            assert config.log_dir == tmp_base_dir / "custom_dir"
            assert config.log_file == (tmp_base_dir / "custom_dir" / "custom_file.txt")
        else: # Otherwise, it's history path
            assert config.history_dir == tmp_base_dir / "custom_dir"
            assert config.history_file == (tmp_base_dir / "custom_dir" / "custom_file.txt")
        
        # Ensure directories are created by config.validate()
        assert (tmp_base_dir / "custom_dir").is_dir()

@pytest.mark.parametrize("dir_attr_name, file_attr_name, default_dir_name, default_file_name", [
    ('log_dir', 'log_file', 'logs', 'calculator.log'),
    ('history_dir', 'history_file', 'history', 'calculator_history.csv'),
])
def test_path_properties_default(dir_attr_name, file_attr_name, default_dir_name, default_file_name):
    with TemporaryDirectory() as tmp_dir_str:
        tmp_base_dir = Path(tmp_dir_str)
        # Clear environment variables to ensure defaults are used
        clear_env_vars('CALCULATOR_LOG_DIR', 'CALCULATOR_LOG_FILE', 'CALCULATOR_HISTORY_DIR', 'CALCULATOR_HISTORY_FILE', 'CALCULATOR_BASE_DIR')
        
        config = CalculatorConfig(base_dir=tmp_base_dir) # Pass base_dir directly to override default_factory for test

        # Assert resolved paths
        if dir_attr_name == "log_dir":
            assert config.log_dir == tmp_base_dir / default_dir_name
            assert config.log_file == (tmp_base_dir / default_dir_name / default_file_name)
        else:
            assert config.history_dir == tmp_base_dir / default_dir_name
            assert config.history_file == (tmp_base_dir / default_dir_name / default_file_name)
        
        # Ensure directories are created by config.validate()
        assert (tmp_base_dir / default_dir_name).is_dir()

def test_config_base_dir_from_env():
    with TemporaryDirectory() as tmp_dir_str:
        tmp_base_dir = Path(tmp_dir_str)
        os.environ['CALCULATOR_BASE_DIR'] = str(tmp_base_dir)
        config = CalculatorConfig() # Instantiate without passing base_dir directly
        assert config.base_dir == tmp_base_dir
        # Ensure default sub-directories are created relative to this base_dir
        assert (tmp_base_dir / "logs").is_dir()
        assert (tmp_base_dir / "history").is_dir()