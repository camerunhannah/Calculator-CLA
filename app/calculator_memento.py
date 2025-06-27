
from typing import List
from app.calculation import Calculation # Memento needs to store Calculation objects

class CalculatorMemento:
    """
    A Memento class that stores the internal state of the CalculationHistory.
    """
    def __init__(self, history_state: List[Calculation], redo_stack_state: List[Calculation]):
        # Store copies to ensure the memento is truly immutable
        self._history_state = history_state[:]
        self._redo_stack_state = redo_stack_state[:]

    def get_history_state(self) -> List[Calculation]:
        """Returns the captured history state."""
        return self._history_state[:]

    def get_redo_stack_state(self) -> List[Calculation]:
        """Returns the captured redo stack state."""
        return self._redo_stack_state[:]

class CalculatorHistoryManager:
    """
    Manages the creation and restoration of CalculatorMemento objects.
    Acts as part of the Originator (creating Mementos) and Caretaker (restoring from Mementos).
    """
    def __init__(self, history_instance):
        self._history_instance = history_instance # Reference to the CalculationHistory object

    def save_state(self) -> CalculatorMemento:
        """
        Saves the current state of the CalculationHistory into a Memento.
        """
        return CalculatorMemento(
            self._history_instance.get_history(),
            self._history_instance._redo_stack[:] # Directly access for saving redo stack
        )

    def restore_state(self, memento: CalculatorMemento):
        """
        Restores the CalculationHistory to a state captured by the given Memento.
        """
        self._history_instance._history = memento.get_history_state()
        self._history_instance._redo_stack = memento.get_redo_stack_state()