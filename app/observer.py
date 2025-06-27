

from abc import ABC, abstractmethod
from typing import List, Any

class Observer(ABC):
    """
    Abstract base class for all observer objects.
    Observers want to be notified of changes in a Subject.
    """
    @abstractmethod
    def update(self, subject: Any):
        """
        Receive update from subject.
        :param subject: The Subject (e.g., Calculator) that notified the observer.
        """
        pass

class Subject(ABC):
    """
    Abstract base class for all subject objects.
    Subjects maintain a list of observers and notify them of state changes.
    """
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all attached observers about a change."""
        for observer in self._observers:
            observer.update(self) # Pass self (the subject) to the observer