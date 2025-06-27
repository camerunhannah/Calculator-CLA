
import pytest
from unittest.mock import Mock
from app.observer import Subject, Observer

class ConcreteObserver(Observer):
    def update(self, subject: Subject):
        # Simply call the mock object to record the update
        self.mock_update(subject)

    def __init__(self, mock_update):
        self.mock_update = mock_update

class ConcreteSubject(Subject):
    def __init__(self):
        super().__init__()
        self.state = 0

    def change_state(self, new_state):
        self.state = new_state
        self.notify_observers()

def test_observer_attach_detach():
    """Test attaching and detaching observers."""
    subject = ConcreteSubject()
    observer1 = ConcreteObserver(Mock())
    observer2 = ConcreteObserver(Mock())

    subject.attach(observer1)
    assert observer1 in subject._observers
    assert len(subject._observers) == 1

    subject.attach(observer2)
    assert observer2 in subject._observers
    assert len(subject._observers) == 2

    subject.attach(observer1) # Attaching same observer again should not add duplicate
    assert len(subject._observers) == 2

    subject.detach(observer1)
    assert observer1 not in subject._observers
    assert len(subject._observers) == 1

    subject.detach(observer2)
    assert observer2 not in subject._observers
    assert len(subject._observers) == 0

    subject.detach(ConcreteObserver(Mock())) # Detaching non-attached observer should not error
    assert len(subject._observers) == 0

def test_observer_notification():
    """Test that observers are notified when subject changes state."""
    subject = ConcreteSubject()
    mock_update1 = Mock()
    mock_update2 = Mock()
    observer1 = ConcreteObserver(mock_update1)
    observer2 = ConcreteObserver(mock_update2)

    subject.attach(observer1)
    subject.attach(observer2)

    subject.change_state(10)

    # Check if update method was called once for each observer, with the subject instance
    mock_update1.assert_called_once_with(subject)
    mock_update2.assert_called_once_with(subject)

    subject.change_state(20) # Change state again
    mock_update1.assert_called_with(subject)
    mock_update2.assert_called_with(subject)
    assert mock_update1.call_count == 2
    assert mock_update2.call_count == 2

def test_observer_no_notification_if_detached():
    """Test that detached observers are not notified."""
    subject = ConcreteSubject()
    mock_update = Mock()
    observer = ConcreteObserver(mock_update)

    subject.attach(observer)
    subject.change_state(10)
    mock_update.assert_called_once_with(subject)

    subject.detach(observer)
    subject.change_state(20) 
    mock_update.assert_called_once() 