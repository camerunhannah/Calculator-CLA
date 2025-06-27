

from app.operation_factory import OperationFactory
from app.calculation import Calculation
from app.logger import logger
from app.exceptions import ValidationError, OperationError, HistoryError
from app.input_validators import (
    validate_numerical_input,
    validate_operands_within_range,
    validate_division_by_zero,
    validate_nth_root_inputs
)
from app.history import CalculationHistory
from app.calculator_memento import CalculatorHistoryManager
from app.calculator_config import config # Import the global config singleton
from app.observer import Subject
from typing import List, Optional

class Calculator(Subject):
    """
    Manages calculator operations, using a factory to create operation instances.
    Also handles input validation, logs operations, and manages calculation history
    with undo/redo functionality using the Memento pattern, and notifies observers.
    """
    def __init__(self):
        super().__init__() # Call parent constructor (Subject)
        self.history = CalculationHistory(config)
        self._history_manager = CalculatorHistoryManager(self.history)
        self._memento_stack = []
        self._redo_memento_stack = []
        logger.info("Calculator initialized with history and memento support.")
        self._is_undo_redo_in_progress = False # Initialize the flag
        self._save_current_history_state() # Save initial state


    def _save_current_history_state(self):
        """Saves the current state of the history to the memento stack."""
        memento = self._history_manager.save_state()
        self._memento_stack.append(memento)
        # Clear redo memento stack on new operations/states, but not on undo/redo actions
        if not self._is_undo_redo_in_progress:
             self._redo_memento_stack.clear()
        self._is_undo_redo_in_progress = False # Reset flag


    def execute_operation(self, operation_name: str, operand_a_str: str, operand_b_str: str) -> Calculation:
        """
        Executes a specified operation after validating inputs and returns a Calculation object.
        Adds the calculation to history and notifies observers.
        """
        #INPUT VALIDATION
        validate_numerical_input(operand_a_str, "first operand")
        validate_numerical_input(operand_b_str, "second operand")

        operand_a = float(operand_a_str)
        operand_b = float(operand_b_str)

        validate_operands_within_range(operand_a, operand_b)

        if operation_name == "divide":
            validate_division_by_zero(operand_b)
        elif operation_name == "root":
            validate_nth_root_inputs(operand_a, operand_b)

        logger.info(f"Attempting to execute operation: {operation_name} with inputs {operand_a}, {operand_b}")
        try:
            operation = OperationFactory.create_operation(operation_name, operand_a, operand_b)
            result = operation.execute()
            calculation = Calculation(operation.get_name(), operand_a, operand_b, result)

            self.history.add_calculation(calculation)
            self._save_current_history_state()

            self.notify_observers() # NOTIFY OBSERVERS AFTER EACH NEW CALCULATION

            logger.info(f"Operation '{operation_name}' executed successfully. Result: {result}")
            return calculation
        except (ValidationError, OperationError) as e:
            logger.error(f"Operation failed due to validation or operation error: {e}")
            raise e
        except Exception as e:
            logger.critical(f"An unexpected critical error occurred during operation '{operation_name}': {e}")
            raise OperationError(f"An unexpected error occurred during operation '{operation_name}': {e}")


    def get_history(self) -> List[Calculation]:
        """Returns the current calculation history."""
        return self.history.get_history()

    
    def save_history(self):
        """
        Placeholder method for saving history.
        Actual implementation will be in Phase 4, Step 10.
        """
        logger.debug("save_history method called (placeholder).")
        # Actual saving logic will go here later
        pass # pragma: no cover 


    def clear_history(self):
        """Clears all calculation history and the redo stack."""
        self.history.clear_history()
        self._memento_stack.clear()
        self._redo_memento_stack.clear()
        self._save_current_history_state() # Save an empty state
        self.notify_observers() # NOTIFY OBSERVERS AFTER HISTORY IS CLEARED
        logger.info("Calculation history cleared.")

    def undo(self) -> Optional[Calculation]:
        """
        Undoes the last calculation.
        Restores previous history state from memento stack.
        """
        if len(self._memento_stack) < 2:
            raise HistoryError("Nothing to undo.")

        self._is_undo_redo_in_progress = True

        self._redo_memento_stack.append(self._memento_stack.pop())
        previous_memento = self._memento_stack[-1]
        self._history_manager.restore_state(previous_memento)
        self.notify_observers() # NOTIFY OBSERVERS AFTER UNDO
        logger.info("Last calculation undone.")
        return self.history.get_latest_calculation()


    def redo(self) -> Optional[Calculation]:
        """
        Redoes the last undone calculation.
        Restores state from redo memento stack.
        """
        if not self._redo_memento_stack:
            raise HistoryError("Nothing to redo.")

        self._is_undo_redo_in_progress = True
        redone_memento = self._redo_memento_stack.pop()
        self._memento_stack.append(redone_memento)
        self._history_manager.restore_state(redone_memento)
        self.notify_observers() 
        logger.info("Last calculation redone.")
        return self.history.get_latest_calculation()