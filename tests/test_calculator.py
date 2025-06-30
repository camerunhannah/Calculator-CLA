# tests/test_calculator.py 

import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
import logging

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory, Addition, Subtraction # Import specific operation classes for type checking


# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator(mocker): # ADDED 'mocker' fixture here
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Create a mock config object instead of a real one, to control attributes directly
        mock_config = mocker.Mock(spec=CalculatorConfig) # Use mocker.Mock
        
        # Set all required config attributes on the mock object
        mock_config.base_dir = temp_path
        mock_config.log_dir = temp_path / "logs"
        mock_config.log_file = temp_path / "logs/calculator.log"
        mock_config.history_dir = temp_path / "history"
        mock_config.history_file = temp_path / "history/calculator_history.csv"
        mock_config.max_history_size = 5 # Set a small max history size for testing
        mock_config.default_encoding = "utf-8" # Default encoding
        mock_config.max_input_value = Decimal('1000000') # Default max input value
        # Mock the validate method to do nothing, as we're controlling config attributes directly
        mock_config.validate.return_value = None 

        # Ensure logging handlers are cleared before Calculator init in tests
        # This is critical for tests that instantiate Calculator multiple times.
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        logging.getLogger().propagate = True # Reset propagation to default

        yield Calculator(config=mock_config) # Pass the mock config to Calculator

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None
    assert calculator.last_command_name is None # Assert new attribute is None initially
    # Ensure directories are created by checking if they exist in the mocked paths
    assert calculator.config.log_dir.exists()
    assert calculator.config.history_dir.exists()


# Test Logging Setup
@patch('app.calculator.logging.info')
@patch('app.calculator.os.makedirs') # Mock makedirs in app.calculator
@patch('app.calculator.logging.basicConfig') # Mock basicConfig itself
def test_logging_setup(mock_basicConfig, mock_makedirs, logging_info_mock, mocker): # ADDED 'mocker' here
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Create a mock config object to pass to Calculator
        mock_config = mocker.Mock(spec=CalculatorConfig) # Use mocker.Mock
        mock_config.log_dir = temp_path / "logs_test"
        mock_config.log_file = temp_path / "logs_test" / "test.log"
        # Ensure all required attributes for Calculator's __init__ are present on the mock config
        mock_config.history_dir = temp_path / "history_test" 
        mock_config.history_file = mock_config.history_dir / "history.csv"
        mock_config.max_history_size = 5
        mock_config.default_encoding = "utf-8"
        mock_config.max_input_value = Decimal('1000000')
        mock_config.validate.return_value = None # Mock validate to do nothing
        
        # Ensure the test target directory for logging is created
        mock_makedirs.return_value = None # os.makedirs should be called

        # Ensure logging handlers are cleared before Calculator init to prevent conflicts
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        logging.getLogger().propagate = True # Reset propagation

        # Instantiate calculator to trigger logging setup within __init__
        calculator = Calculator(mock_config)

        mock_makedirs.assert_called_once_with(mock_config.log_dir, exist_ok=True)
        mock_basicConfig.assert_called_once_with(
            filename=str(mock_config.log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        logging_info_mock.assert_any_call(f"Logging initialized at: {mock_config.log_file}")
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


# Test Adding and Removing Observers

def test_add_observer(calculator, mocker): # ADDED 'mocker' here
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers
    # Test adding duplicate observer - should not add again
    calculator.add_observer(observer)
    assert calculator.observers.count(observer) == 1

def test_remove_observer(calculator, mocker): # ADDED 'mocker' here
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers
    # Test removing non-existent observer (should be handled gracefully)
    with patch('app.calculator.logging.warning') as mock_log_warning:
        calculator.remove_observer(observer)
        mock_log_warning.assert_called_once_with(f"Observer {observer.__class__.__name__} not found, cannot remove.")


# Test Setting Operations

def test_set_operation(calculator):
    # Pass the operation name (string)
    calculator.set_operation('add')
    # Assert that the operation_strategy is an instance of the correct concrete class
    assert isinstance(calculator.operation_strategy, Addition)
    assert calculator.last_command_name == 'add' # Verify stored command name

def test_set_operation_unknown(calculator):
    with pytest.raises(OperationError, match="Unknown operation: invalid_op"):
        calculator.set_operation('invalid_op')
    assert calculator.operation_strategy is None # Ensure strategy remains None
    assert calculator.last_command_name is None # Ensure command name remains None


# Test Performing Operations

def test_perform_operation_addition(calculator):
    calculator.set_operation('add')
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')
    assert len(calculator.history) == 1
    # Check the operation_name in the stored Calculation object (this is the short name)
    assert calculator.history[0].operation_name == "add" 
    assert calculator.history[0].operand1 == Decimal('2')
    assert calculator.history[0].operand2 == Decimal('3')
    assert calculator.history[0].result == Decimal('5')
    # Check undo stack after operation
    assert len(calculator.undo_stack) == 1
    assert calculator.redo_stack == []

def test_perform_operation_subtraction(calculator):
    calculator.set_operation('subtract')
    result = calculator.perform_operation(10, 4)
    assert result == Decimal('6')
    assert calculator.history[0].operation_name == "subtract"

def test_perform_operation_modulus(calculator):
    calculator.set_operation('modulus')
    result = calculator.perform_operation(10, 3)
    assert result == Decimal('1')
    assert calculator.history[0].operation_name == "modulus"

def test_perform_operation_int_divide(calculator):
    calculator.set_operation('int_divide')
    result = calculator.perform_operation(10, 3)
    assert result == Decimal('3')
    assert calculator.history[0].operation_name == "int_divide"

def test_perform_operation_percent(calculator):
    calculator.set_operation('percent')
    result = calculator.perform_operation(50, 200)
    assert result == Decimal('25')
    assert calculator.history[0].operation_name == "percent"

def test_perform_operation_abs_diff(calculator):
    calculator.set_operation('abs_diff')
    result = calculator.perform_operation(5, 10)
    assert result == Decimal('5')
    assert calculator.history[0].operation_name == "abs_diff"


def test_perform_operation_validation_error(calculator):
    calculator.set_operation('add') 
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_no_operation_set(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

def test_perform_operation_operation_specific_error(calculator):
    calculator.set_operation('divide')
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        calculator.perform_operation(10, 0)

# Test Undo/Redo Functionality

def test_undo_successful(calculator):
    calculator.set_operation('add')
    calculator.perform_operation(2, 3) 
    assert len(calculator.history) == 1
    assert len(calculator.undo_stack) == 1
    assert len(calculator.redo_stack) == 0

    assert calculator.undo() is True 
    assert calculator.history == [] # History is empty after undoing the only operation
    assert len(calculator.undo_stack) == 0
    assert len(calculator.redo_stack) == 1 # Redo stack now has the memento of [Calc1]

def test_undo_nothing_to_undo(calculator):
    assert calculator.undo() is False
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

def test_redo_successful(calculator):
    calculator.set_operation('add')
    calculator.perform_operation(2, 3) 
    calculator.undo()                  
    assert calculator.redo() is True   
    assert len(calculator.history) == 1
    assert len(calculator.undo_stack) == 1 # Should contain the memento of [] (state before redo)
    assert len(calculator.redo_stack) == 0
    assert calculator.history[0].operation_name == "add" # Assert short name
    assert calculator.history[0].result == Decimal('5')


def test_redo_nothing_to_redo(calculator):
    assert calculator.redo() is False
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

def test_new_operation_clears_redo_stack(calculator):
    calculator.set_operation('add')
    calculator.perform_operation(1, 1) 
    calculator.perform_operation(2, 2) 
    calculator.undo()                  
    
    # Perform a new operation, this should clear the redo stack
    calculator.set_operation('multiply')
    calculator.perform_operation(3, 3) 
    
    assert len(calculator.history) == 2
    assert calculator.redo_stack == [] 

def test_history_max_size_enforcement(calculator):
    # Max history size is mocked to 5 in the fixture
    calculator.set_operation('add')
    for i in range(1, 10): # Add 9 operations
        calculator.perform_operation(i, 1)
    
    assert len(calculator.history) == 5 # Should only keep the last 5
    assert calculator.history[0].operand1 == Decimal('5') # First element should be 5+1=6 (original 5th calc)
    assert calculator.history[-1].operand1 == Decimal('9') # Last element should be 9+1=10 (original 9th calc)

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
@patch('app.calculator.pd.DataFrame', autospec=True) # Patch DataFrame constructor for inspection
def test_save_history_success(mock_dataframe_constructor, mock_to_csv, calculator):
    # Reset mock_dataframe_constructor calls if it's reused from previous tests
    mock_dataframe_constructor.reset_mock()
    mock_to_csv.reset_mock()

    calculator.set_operation('add')
    calculator.perform_operation(2, 3)
    calculator.save_history()

    # Check that DataFrame was created with the correct data
    mock_dataframe_constructor.assert_called_once()
    args, kwargs = mock_dataframe_constructor.call_args
    history_data = args[0] # The first argument should be the list of dicts

    assert isinstance(history_data, list)
    assert len(history_data) == 1
    assert history_data[0]['operation'] == "add" # Now expects short name
    assert history_data[0]['operand1'] == "2"
    assert history_data[0]['result'] == "5"

    # Check that to_csv was called on the mock DataFrame instance returned by the constructor
    mock_dataframe_constructor.return_value.to_csv.assert_called_once_with(
        calculator.config.history_file, 
        index=False, 
        encoding=calculator.config.default_encoding
    )

@patch('app.calculator.pd.DataFrame.to_csv', side_effect=Exception("Save error!"))
def test_save_history_failure(mock_to_csv, calculator):
    calculator.set_operation('add')
    calculator.perform_operation(2, 3)
    with pytest.raises(OperationError, match="Failed to save history: Save error!"):
        calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_success(mock_exists, mock_read_csv, calculator):
    # Mock CSV data: 'operation' column should contain the short names (e.g., "add")
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['add', 'subtract'],
        'operand1': ['2', '10'],
        'operand2': ['3', '5'],
        'result': ['5', '5'],
        'timestamp': [datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()]
    })
    
    calculator.load_history() 
    
    assert len(calculator.history) == 2
    assert calculator.history[0].operation_name == "add"
    assert calculator.history[0].operand1 == Decimal("2")
    assert calculator.history[0].operand2 == Decimal("3")
    assert calculator.history[0].result == Decimal("5")

    assert calculator.history[1].operation_name == "subtract"
    assert calculator.history[1].operand1 == Decimal("10")
    assert calculator.history[1].operand2 == Decimal("5")
    assert calculator.history[1].result == Decimal("5")

    assert len(calculator.undo_stack) == 1 
    assert calculator.undo_stack[0].history == calculator.history 
    assert calculator.redo_stack == []


@patch('app.calculator.pd.read_csv', side_effect=Exception("Load error!"))
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_failure(mock_exists, mock_read_csv, calculator):
    with pytest.raises(OperationError, match="Failed to load history: Load error!"):
        calculator.load_history()
    mock_read_csv.assert_called_once()
    assert calculator.history == [] 
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

@patch('app.calculator.Path.exists', return_value=False)
def test_load_history_no_file(mock_exists, calculator):
    calculator.load_history()
    assert calculator.history == [] 
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


def test_clear_history(calculator):
    calculator.set_operation('add')
    calculator.perform_operation(2, 3)
    calculator.set_operation('subtract')
    calculator.perform_operation(5, 1)

    assert len(calculator.history) == 2
    assert len(calculator.undo_stack) > 0

    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# REPL tests are handled in tests/test_calculator_repl.py
