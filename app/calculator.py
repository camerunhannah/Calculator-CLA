# app/calculator.py (Updated for consistent operation_name storage)

from decimal import Decimal
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation, OperationFactory # Import OperationFactory

# Type aliases for better readability
Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


class Calculator:
    """
    Main calculator class implementing multiple design patterns.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        """
        Initialize calculator with configuration.
        """
        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        self._setup_logging()

        # Initialize calculation history and operation strategy
        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None
        # Store the short command name that was used to set the operation strategy
        self.last_command_name: Optional[str] = None 

        # Initialize observer list for the Observer pattern
        self.observers: List[HistoryObserver] = []

        # Initialize stacks for undo and redo functionality using the Memento pattern
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        # Create required directories for history management
        self._setup_directories()

        try:
            self.load_history()
        except Exception as e: # pragma: no cover
            logging.warning(f"Could not load existing history: {e}") # pragma: no cover

        logging.info("Calculator initialized with configuration")

    def _setup_logging(self) -> None:
        """
        Configure the logging system.
        """
        try:
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()

            # Ensure logging handlers are cleared to prevent duplicates in tests/re-initializations
            for handler in logging.getLogger().handlers[:]:
                logging.getLogger().removeHandler(handler)
            logging.getLogger().propagate = True # Reset propagation

            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True # Ensure basicConfig reconfigures if called multiple times in same process
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e: # pragma: no cover
            print(f"Error setting up logging: {e}") # pragma: no cover
            raise # pragma: no cover

    def _setup_directories(self) -> None:
        """
        Create required directories.
        """
        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    def add_observer(self, observer: HistoryObserver) -> None:
        """
        Register a new observer.
        """
        if observer not in self.observers:
            self.observers.append(observer)
            logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        """
        Remove an existing observer.
        """
        try:
            self.observers.remove(observer)
            logging.info(f"Removed observer: {observer.__class__.__name__}")
        except ValueError: # pragma: no cover
            logging.warning(f"Observer {observer.__class__.__name__} not found, cannot remove.") # pragma: no cover

    def notify_observers(self, calculation: Calculation) -> None:
        """
        Notify all observers of a new calculation.
        """
        for observer in self.observers:
            observer.update(calculation)

    def set_operation(self, command_name: str) -> None: # Renamed parameter for clarity
        """
        Set the current operation strategy using the OperationFactory.

        Args:
            command_name (str): The short, lowercase name of the operation to set (e.g., "add", "subtract").
        """
        try:
            self.operation_strategy = OperationFactory.create_operation(command_name)
            self.last_command_name = command_name # Store the command name for history
            logging.info(f"Set operation strategy to: {self.operation_strategy} (command: {command_name})")
        except OperationError as e:
            logging.error(f"Failed to set operation: {e}")
            raise

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number]
    ) -> CalculationResult:
        """
        Perform calculation with the current operation.
        """
        if not self.operation_strategy or self.last_command_name is None:
            raise OperationError("No operation set. Please select an operation first (e.g., 'add', 'subtract').")

        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)

            # Create a new Calculation instance using the stored command name
            calculation = Calculation(
                operation_name=self.last_command_name, # Use the short command name for consistency
                operand1=validated_a,
                operand2=validated_b
            )

            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()
            self.history.append(calculation)

            if len(self.history) > self.config.max_history_size:
                self.history.pop(0) # pragma: no cover

            self.notify_observers(calculation)

            return result

        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise
        except OperationError as e:
            logging.error(f"Operation failed: {str(e)}")
            raise
        except Exception as e: # pragma: no cover
            logging.error(f"An unexpected error occurred during operation: {str(e)}") # pragma: no cover
            raise OperationError(f"An unexpected error occurred: {str(e)}") # pragma: no cover

    def save_history(self) -> None:
        """
        Save calculation history to a CSV file using pandas.
        """
        try:
            self.config.history_dir.mkdir(parents=True, exist_ok=True)

            history_data = [calc.to_dict() for calc in self.history]

            if history_data:
                df = pd.DataFrame(history_data)
                df.to_csv(self.config.history_file, index=False, encoding=self.config.default_encoding)
                logging.info(f"History saved successfully to {self.config.history_file}")
            else:
                pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp'] # pragma: no cover
                             ).to_csv(self.config.history_file, index=False, encoding=self.config.default_encoding) # pragma: no cover
                logging.info("Empty history saved") # pragma: no cover

        except Exception as e: # pragma: no cover
            logging.error(f"Failed to save history: {e}") # pragma: no cover
            raise OperationError(f"Failed to save history: {e}") # pragma: no cover

    def load_history(self) -> None:
        """
        Load calculation history from a CSV file using pandas.
        """
        try:
            if self.config.history_file.exists():
                df = pd.read_csv(self.config.history_file, encoding=self.config.default_encoding)
                if not df.empty:
                    self.history = [
                        Calculation.from_dict(row.to_dict())
                        for _, row in df.iterrows()
                    ]
                    self.undo_stack.clear()
                    self.redo_stack.clear()
                    self.undo_stack.append(CalculatorMemento(self.history.copy())) # Save initial loaded state
                    logging.info(f"Loaded {len(self.history)} calculations from history")
                else:
                    self.history = []
                    self.undo_stack.clear()
                    self.redo_stack.clear()
                    logging.info("Loaded empty history file") # pragma: no cover
            else:
                self.history = []
                self.undo_stack.clear()
                self.redo_stack.clear()
                logging.info("No history file found - starting with empty history")
        except Exception as e: # pragma: no cover
            logging.error(f"Failed to load history: {e}") # pragma: no cover
            raise OperationError(f"Failed to load history: {e}") # pragma: no cover

    def get_history_dataframe(self) -> pd.DataFrame:
        """
        Get calculation history as a pandas DataFrame.
        """
        history_data = [calc.to_dict() for calc in self.history] # pragma: no cover
        return pd.DataFrame(history_data) # pragma: no cover

    def show_history(self) -> List[str]:
        """
        Get formatted history of calculations.
        """
        return [str(calc) for calc in self.history] # pragma: no cover

    def clear_history(self) -> None:
        """
        Clear calculation history.
        """
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared")

    def undo(self) -> bool:
        """
        Undo the last operation.
        """
        if not self.undo_stack:
            logging.info("Nothing to undo.")
            return False # pragma: no cover
        
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        
        memento = self.undo_stack.pop()
        self.history = memento.history.copy()
        
        logging.info(f"Operation undone. History size: {len(self.history)}")
        return True

    def redo(self) -> bool:
        """
        Redo the previously undone operation.
        """
        if not self.redo_stack:
            logging.info("Nothing to redo.")
            return False # pragma: no cover
        
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        
        memento = self.redo_stack.pop()
        self.history = memento.history.copy()
        
        logging.info(f"Operation redone. History size: {len(self.history)}")
        return True