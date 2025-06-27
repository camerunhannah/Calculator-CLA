
from typing import List, Optional
from app.calculation import Calculation
from app.calculator_config import config as app_config_singleton # Renamed import to avoid confusion

class CalculationHistory:
    """
    Manages the history of calculations.
    Acts as the Caretaker for the Memento pattern by managing the history stack.
    """
    def __init__(self, config_instance=None):
        self._history: List[Calculation] = []
        self._redo_stack: List[Calculation] = []
        # Use provided config_instance or fallback to the app's global singleton
        self.config = config_instance if config_instance is not None else app_config_singleton
        print(f"DEBUG HISTORY: History initialized. Max History Size: {self.config.MAX_HISTORY_SIZE}") # Temporary debug
        print(f"DEBUG HISTORY: History config instance ID: {id(self.config)}") # Temporary debug

    def add_calculation(self, calculation: Calculation):
        """
        Adds a calculation to the history. Clears the redo stack.
        Enforces maximum history size.
        """
        self._history.append(calculation)
        self._redo_stack.clear() # Any new operation clears the redo stack

        # Enforce maximum history size
        while len(self._history) > self.config.MAX_HISTORY_SIZE: # <--- USE self.config
            self._history.pop(0) # Remove the oldest entry
        print(f"DEBUG HISTORY: After add, history size: {len(self._history)}") # Temporary debug

    def get_history(self) -> List[Calculation]:
        """Returns a copy of the current calculation history."""
        return self._history[:] # Return a slice to prevent external modification

    def clear_history(self):
        """Clears all calculation history and the redo stack."""
        self._history.clear()
        self._redo_stack.clear()

    def undo(self) -> Optional[Calculation]:
        """
        Undoes the last calculation, moving it to the redo stack.
        Returns the undone calculation or None if history is empty.
        """
        if not self._history:
            return None # History is empty, nothing to undo

        undone_calculation = self._history.pop()
        self._redo_stack.append(undone_calculation)
        return undone_calculation

    def redo(self) -> Optional[Calculation]:
        """
        Redoes the last undone calculation, moving it back to history.
        Returns the redone calculation or None if redo stack is empty.
        """
        if not self._redo_stack:
            return None # Redo stack is empty, nothing to redo

        redone_calculation = self._redo_stack.pop()
        self._history.append(redone_calculation)
        return redone_calculation

    def get_latest_calculation(self) -> Optional[Calculation]:
        """Returns the most recent calculation without removing it, or None if history is empty."""
        return self._history[-1] if self._history else None