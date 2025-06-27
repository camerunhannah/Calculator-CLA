
import pytest
from app.calculator_memento import CalculatorMemento, CalculatorHistoryManager
from app.history import CalculationHistory
from app.calculation import Calculation
from app.exceptions import HistoryError # Import HistoryError for tests
import sys # For sys.modules
import os # For os.environ
from app.calculator_config import AppConfig # Import AppConfig class for mocking


# Fixture to manage config for tests and ensure isolation
@pytest.fixture(autouse=True)
def manage_config_for_memento_tests(monkeypatch):
    # Capture original state
    original_max_history_size_env = os.environ.get("CALCULATOR_MAX_HISTORY_SIZE")
    original_global_config_instance = sys.modules['app.calculator_config'].config

    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "5") # Set a small history size for testing

    # Replace the global config with a new instance that picked up the env var
    sys.modules['app.calculator_config'].config = AppConfig()
    temp_config = sys.modules['app.calculator_config'].config # Get the new instance reference

    yield temp_config # Yield the temporary config instance for use in tests

    # Cleanup
    if original_max_history_size_env is not None:
        monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", original_max_history_size_env)
    else:
        monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    sys.modules['app.calculator_config'].config = original_global_config_instance


@pytest.fixture
def history_with_data(manage_config_for_memento_tests): # Pass fixture to this fixture
    """Provides a CalculationHistory instance with some data."""
    history = CalculationHistory(manage_config_for_memento_tests) # Pass the config
    history.add_calculation(Calculation("add", 1, 1, 2))
    history.add_calculation(Calculation("subtract", 5, 2, 3))
    return history

def test_memento_captures_state(history_with_data):
    """Test that Memento correctly captures history and redo stack states."""
    # Manipulate redo stack for a more comprehensive test
    history_with_data.undo()
    history_with_data.undo()

    memento = CalculatorMemento(
        history_with_data.get_history(),
        history_with_data._redo_stack # Access internal for direct capture
    )
    assert len(memento.get_history_state()) == len(history_with_data.get_history())
    assert len(memento.get_redo_stack_state()) == len(history_with_data._redo_stack)
    assert memento.get_history_state() == history_with_data.get_history()
    assert memento.get_redo_stack_state() == history_with_data._redo_stack

def test_history_manager_save_and_restore_state(manage_config_for_memento_tests): # Pass fixture
    """Test that CalculatorHistoryManager saves and restores state correctly."""
    initial_history = CalculationHistory(manage_config_for_memento_tests) # Pass the config
    initial_history.add_calculation(Calculation("add", 1, 1, 2))
    initial_history.add_calculation(Calculation("subtract", 5, 2, 3))

    history_manager = CalculatorHistoryManager(initial_history)
    memento = history_manager.save_state()

    # Change history after saving
    initial_history.add_calculation(Calculation("multiply", 2, 2, 4))
    assert len(initial_history.get_history()) == 3

    # Restore state from memento
    history_manager.restore_state(memento)
    assert len(initial_history.get_history()) == 2
    assert initial_history.get_history()[0].operation_name == "add"
    assert initial_history.get_history()[1].operation_name == "subtract"

    # Test redo stack is also restored
    initial_history.undo()
    initial_history.undo() # Two undos
    memento_after_undos = history_manager.save_state()
    assert len(memento_after_undos.get_history_state()) == 0
    assert len(memento_after_undos.get_redo_stack_state()) == 2

    history_manager.restore_state(memento) # Restore original state again
    assert len(initial_history.get_history()) == 2
    assert len(initial_history._redo_stack) == 0 # Should be empty as original state was clean

def test_calculator_integration_undo_redo(mocker, manage_config_for_memento_tests): # Add fixture
    """
    Test Calculator's undo/redo functionality and memento management.
    Mocks _is_undo_redo_in_progress to control redo stack clearing.
    """
    from app.calculator import Calculator # Import Calculator here to avoid circular dependencies if any

    calculator = Calculator()
    
   
    mocker.patch.object(calculator, '_is_undo_redo_in_progress', False)


    calc1 = calculator.execute_operation("add", "1", "1") # 1+1=2
    calc2 = calculator.execute_operation("subtract", "5", "2") # 5-2=3
    calc3 = calculator.execute_operation("multiply", "3", "4") # 3*4=12

    assert len(calculator.get_history()) == 3
    assert calculator.get_history()[-1].result == 12
    assert len(calculator._memento_stack) == 4 # Initial state + 3 operations

    # Test undo
    calculator._is_undo_redo_in_progress = True # Indicate undo is in progress
    undone_calc = calculator.undo()
    assert len(calculator.get_history()) == 2
    assert calculator.get_history()[-1].result == 3 # Last calculation should be 5-2=3
    assert len(calculator._memento_stack) == 3 # Memento stack reduced
    assert len(calculator._redo_memento_stack) == 1 # Redo memento stack has 1 entry
    assert undone_calc.result == 3 # Check returned calc

    calculator._is_undo_redo_in_progress = True # Still True for undo
    undone_calc2 = calculator.undo()
    assert len(calculator.get_history()) == 1
    assert calculator.get_history()[-1].result == 2 # Last calculation should be 1+1=2
    assert len(calculator._memento_stack) == 2
    assert len(calculator._redo_memento_stack) == 2
    assert undone_calc2.result == 2

    # Test redo
    calculator._is_undo_redo_in_progress = True # Still True for redo
    redone_calc = calculator.redo()
    assert len(calculator.get_history()) == 2
    assert calculator.get_history()[-1].result == 3 # Should be 5-2=3 again
    assert len(calculator._memento_stack) == 3
    assert len(calculator._redo_memento_stack) == 1 # Redo stack reduced
    assert redone_calc.result == 3

    calculator._is_undo_redo_in_progress = True # Still True for redo
    redone_calc2 = calculator.redo()
    assert len(calculator.get_history()) == 3
    assert calculator.get_history()[-1].result == 12 # Should be 3*4=12 again
    assert len(calculator._memento_stack) == 4
    assert len(calculator._redo_memento_stack) == 0 # Redo stack empty
    assert redone_calc2.result == 12

    # Test nothing to undo/redo errors
    calculator_for_error_test = Calculator() # Fresh calculator
    calculator_for_error_test._is_undo_redo_in_progress = True # Set flag for this new instance

    with pytest.raises(HistoryError, match="Nothing to undo."):
        calculator_for_error_test.undo() # Tries to undo initial empty state

    calculator_for_error_test._is_undo_redo_in_progress = False # Reset for new op
    calculator_for_error_test.execute_operation("add", "1", "1") # Add an operation
    assert len(calculator_for_error_test.get_history()) == 1
    calculator_for_error_test._is_undo_redo_in_progress = True # Set flag for undo
    calculator_for_error_test.undo() # Undoes the operation
    assert len(calculator_for_error_test.get_history()) == 0
    assert len(calculator_for_error_test._redo_memento_stack) == 1 # Now something to redo

    with pytest.raises(HistoryError, match="Nothing to redo."):
        calculator_for_error_test._is_undo_redo_in_progress = True # Set flag for redo
        calculator_for_error_test.redo() # Redoes the operation
        calculator_for_error_test._is_undo_redo_in_progress = True # Set flag for next redo
        calculator_for_error_test.redo() # Should raise error here as redo stack is now empty


    # Test that new operations clear redo stack
    calculator_for_redo_clear = Calculator()
    # Initial state, _is_undo_redo_in_progress is False
    calculator_for_redo_clear.execute_operation("add", "1", "1")
    calculator_for_redo_clear.execute_operation("subtract", "2", "1")
    calculator_for_redo_clear._is_undo_redo_in_progress = True # Set flag for undo
    calculator_for_redo_clear.undo() # Now redo stack has one entry
    assert len(calculator_for_redo_clear._redo_memento_stack) == 1
    # Performing a new operation should clear redo stack, so reset flag to False
    calculator_for_redo_clear._is_undo_redo_in_progress = False
    calculator_for_redo_clear.execute_operation("multiply", "3", "3")
    assert len(calculator_for_redo_clear._redo_memento_stack) == 0 # Redo stack should be clear