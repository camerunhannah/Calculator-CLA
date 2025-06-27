
import pytest
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.calculator_config import AppConfig

# IMPORTANT: Import CalculationHistory (and Calculation) after the path setup
from app.history import CalculationHistory
from app.calculation import Calculation


# Fixture to manage config for tests and ensure isolation
@pytest.fixture(autouse=True)
def manage_config_for_history_tests(monkeypatch):
  
    original_max_history_size_env = os.environ.get("CALCULATOR_MAX_HISTORY_SIZE")
    original_global_config_instance = sys.modules['app.calculator_config'].config

  
    temp_config = AppConfig()
    temp_config.MAX_HISTORY_SIZE = 5 # Manually set the value for testing

    # Replace the global config with our temporary one
    sys.modules['app.calculator_config'].config = temp_config

    yield temp_config # Yield the temporary config instance for use in tests

    
    if original_max_history_size_env is not None:
        monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", original_max_history_size_env)
    else:
        monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    sys.modules['app.calculator_config'].config = original_global_config_instance


@pytest.fixture
def sample_calculations():
    """Provides a list of sample Calculation objects."""
    return [
        Calculation("add", 1, 1, 2),
        Calculation("subtract", 5, 2, 3),
        Calculation("multiply", 3, 4, 12),
        Calculation("divide", 10, 2, 5),
        Calculation("power", 2, 3, 8),
    ]

def test_add_calculation_to_history(sample_calculations, manage_config_for_history_tests): # Add fixture
    """Test adding a single calculation to history."""
    history = CalculationHistory(manage_config_for_history_tests) # Pass the config
    history.add_calculation(sample_calculations[0])
    assert len(history.get_history()) == 1
    assert history.get_history()[0].result == 2

def test_add_multiple_calculations(sample_calculations, manage_config_for_history_tests): # Add fixture
    """Test adding multiple calculations to history."""
    history = CalculationHistory(manage_config_for_history_tests) # Pass the config
    for calc in sample_calculations:
        history.add_calculation(calc)
    assert len(history.get_history()) == len(sample_calculations)
    assert history.get_history()[-1].result == 8 # Last added was power 2^3=8

def test_clear_history(manage_config_for_history_tests): # Add fixture
    """Test clearing the calculation history."""
    history = CalculationHistory(manage_config_for_history_tests) # Pass the config
    history.add_calculation(Calculation("add", 1, 1, 2))
    history.clear_history()
    assert len(history.get_history()) == 0

def test_history_enforces_max_size(sample_calculations, manage_config_for_history_tests): # Add fixture
    """Test that history maintains maximum size."""
    # Get the temporary config from the fixture
    temp_config = manage_config_for_history_tests
    history = CalculationHistory(temp_config) # Pass the temporary config instance

    # Verify the history instance correctly sees the MAX_HISTORY_SIZE from the passed config
    assert history.config.MAX_HISTORY_SIZE == 5, f"Expected 5, got {history.config.MAX_HISTORY_SIZE}"

    for i in range(10): # Add more than max size (5)
        history.add_calculation(Calculation("add", i, 1, i + 1))
    assert len(history.get_history()) == 5 # Should now keep only the last 5
    # The first item in history should now be the 6th item added (index 5)
    assert history.get_history()[0].operand_a == 5 # Added 0,1,2,3,4,5,6,7,8,9. After trimming, it should be 5,6,7,8,9.

def test_get_latest_calculation(manage_config_for_history_tests): # Add fixture
    """Test getting the latest calculation."""
    history = CalculationHistory(manage_config_for_history_tests) # Pass the config
    assert history.get_latest_calculation() is None
    calc1 = Calculation("add", 1, 1, 2)
    calc2 = Calculation("subtract", 5, 2, 3)
    history.add_calculation(calc1)
    assert history.get_latest_calculation() == calc1
    history.add_calculation(calc2)
    assert history.get_latest_calculation() == calc2

def test_get_history_returns_copy(manage_config_for_history_tests): # Add fixture
    """Test that get_history returns a copy, not the original list."""
    history = CalculationHistory(manage_config_for_history_tests) # Pass the config
    calc = Calculation("add", 1, 1, 2)
    history.add_calculation(calc)
    retrieved_history = history.get_history()
    assert retrieved_history[0] == calc
    retrieved_history.append(Calculation("multiply", 2, 2, 4)) 
    assert len(history.get_history()) == 1 # Original history should be unchanged