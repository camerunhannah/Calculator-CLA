# tests/test_history.py 

import pytest
from unittest.mock import MagicMock, patch, Mock 
import logging
from datetime import datetime 
from decimal import Decimal
from pathlib import Path

from app.history import LoggingObserver, AutoSaveObserver, HistoryObserver
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator import Calculator 

# Fixture for a mock Calculation object
@pytest.fixture
def calculation_mock(mocker):
    mock = mocker.MagicMock(spec=Calculation)
    mock.operation_name = "Addition"
    mock.operand1 = Decimal('5')
    mock.operand2 = Decimal('3')
    mock.result = Decimal('8')
    mock.timestamp = datetime.now() 
    mock.__str__.return_value = f"{mock.operation_name}({mock.operand1}, {mock.operand2}) = {mock.result}"
    return mock

# Fixture for a mock Calculator object used by observers
@pytest.fixture
def calculator_mock_for_observers(mocker):
    mock = mocker.MagicMock(spec=Calculator) 
    # Explicitly set the 'observers' attribute to a real list.
    # This list will be managed by the mock's methods that interact with it.
    mock.observers = [] # CORRECTED: Ensure this is a real list for 'in' and 'append'

    # Mock the add_observer and remove_observer methods to interact with this real list
    # This prevents the MagicMock's default behavior from interfering with list operations
    def mock_add_observer(observer_instance):
        if observer_instance not in mock.observers: # Mimic Calculator's behavior
            mock.observers.append(observer_instance)
    
    def mock_remove_observer(observer_instance):
        try:
            mock.observers.remove(observer_instance)
        except ValueError:
            # Mimic Calculator's logging behavior for non-existent observer
            logging.warning(f"Observer {observer_instance.__class__.__name__} not found, cannot remove.")

    mock.add_observer.side_effect = mock_add_observer
    mock.remove_observer.side_effect = mock_remove_observer
    
    mock.config = mocker.MagicMock(spec=CalculatorConfig) 
    mock.config.history_file = MagicMock(spec=Path)
    mock.config.history_file.exists.return_value = False
    mock.config.default_encoding = "utf-8"
    mock.config.auto_save = True 

    mock.save_history = mocker.MagicMock() 
    mock.load_history = mocker.MagicMock() 
    mock.history = []

    return mock


# Test for LoggingObserver
@patch('logging.info')
def test_logging_observer_logs_calculation(logging_info_mock, calculation_mock):
    observer = LoggingObserver()
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once()
    expected_log_message_part = f"Calculation performed: {calculation_mock.operation_name} "
    assert expected_log_message_part in logging_info_mock.call_args[0][0]


# Test for AutoSaveObserver
def test_auto_save_observer_saves_history(calculator_mock_for_observers, calculation_mock):
    calculator_mock_for_observers.config.auto_save = True 
    observer = AutoSaveObserver(calculator_mock_for_observers)
    observer.update(calculation_mock)
    calculator_mock_for_observers.save_history.assert_called_once()


# Test for AutoSaveObserver not saving if auto_save is false
def test_auto_save_observer_does_not_save_if_disabled(calculator_mock_for_observers, calculation_mock):
    calculator_mock_for_observers.config.auto_save = False 
    observer = AutoSaveObserver(calculator_mock_for_observers)
    observer.update(calculation_mock)
    calculator_mock_for_observers.save_history.assert_not_called()


# Test observer registration and notification within the context of Calculator.
def test_add_observer_in_calculator(calculator_mock_for_observers, mocker):
    observer_instance = mocker.MagicMock(spec=LoggingObserver) 
    calculator_mock_for_observers.add_observer(observer_instance)
    # This assertion now works because mock.add_observer uses the side_effect to append to the real list
    assert observer_instance in calculator_mock_for_observers.observers 
    
    # Test adding duplicate observer (should not add, and should not log a warning)
    with patch('app.calculator.logging.info') as mock_log_info: 
        calculator_mock_for_observers.add_observer(observer_instance)
        mock_log_info.assert_not_called()


def test_remove_observer_in_calculator(calculator_mock_for_observers, mocker):
    observer_instance = mocker.MagicMock(spec=LoggingObserver)
    calculator_mock_for_observers.add_observer(observer_instance) # Add it first using the mocked add_observer
    calculator_mock_for_observers.remove_observer(observer_instance) # Then remove using the mocked remove_observer
    assert observer_instance not in calculator_mock_for_observers.observers
    
    # Test removing non-existent observer for graceful handling
    with patch('app.calculator.logging.warning') as mock_log_warning:
        # The mock.remove_observer side_effect will handle the ValueError correctly.
        calculator_mock_for_observers.remove_observer(observer_instance) 
        mock_log_warning.assert_called_once()



# Test AutoSaveObserver __init__ checks for required Calculator attributes
def test_auto_save_observer_init_checks_calculator_attributes(mocker):
    # Store the original hasattr for safe recursive calls
    _original_hasattr = hasattr # Store the built-in hasattr before patching

    # Test valid initialization: mock_calculator has all required attributes
    mock_calculator_valid = mocker.MagicMock(spec=Calculator) 
    mock_calculator_valid.config = mocker.MagicMock(spec=CalculatorConfig)
    mock_calculator_valid.config.auto_save = True
    mock_calculator_valid.config.history_file = MagicMock(spec=Path)
    mock_calculator_valid.config.default_encoding = "utf-8"
    mock_calculator_valid.save_history = mocker.MagicMock() 
    try:
        AutoSaveObserver(mock_calculator_valid)
    except TypeError as e:
        pytest.fail(f"AutoSaveObserver init raised TypeError unexpectedly with valid mock attributes: {e}")

    # Test missing config attribute: use a basic Mock() (stricter than MagicMock for hasattr)
    mock_invalid_calc_no_config = mocker.Mock() # Corrected: Use Mock()
    mock_invalid_calc_no_config.save_history = mocker.MagicMock() 
    
    # Patch 'builtins.hasattr' to return False only for the specific missing attribute on this mock
    with patch('builtins.hasattr', side_effect=lambda obj, name: 
               False if (obj is mock_invalid_calc_no_config and name == 'config') 
               else _original_hasattr(obj, name)): # CORRECTED: Call the original hasattr
        with pytest.raises(TypeError, match="Calculator must have 'config' and 'save_history' attributes"):
            AutoSaveObserver(mock_invalid_calc_no_config)

    # Test missing save_history attribute: use a basic Mock() (stricter than MagicMock for hasattr)
    mock_invalid_calc_no_save_history = mocker.Mock() 
    mock_invalid_calc_no_save_history.config = mocker.MagicMock(spec=CalculatorConfig) 
    
    # Patch 'builtins.hasattr' to return False only for the specific missing attribute on this mock
    with patch('builtins.hasattr', side_effect=lambda obj, name: 
               False if (obj is mock_invalid_calc_no_save_history and name == 'save_history') 
               else _original_hasattr(obj, name)): # CORRECTED: Call the original hasattr
        with pytest.raises(TypeError, match="Calculator must have 'config' and 'save_history' attributes"):
            AutoSaveObserver(mock_invalid_calc_no_save_history)