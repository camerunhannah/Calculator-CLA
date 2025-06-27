
import pytest
from unittest.mock import Mock
from app.autosave_observer import AutoSaveObserver
from app.calculator import Calculator # Subject
import sys # For sys.modules
import os # For os.environ
import logging # Needed for logging.INFO/WARNING
from app.logger import APP_LOGGER_NAME # Import APP_LOGGER_NAME
from app.calculator_config import AppConfig # For mocking config


# Fixture to manage config for auto-save tests
@pytest.fixture(autouse=True)
def manage_config_for_autosave_tests(monkeypatch):
    original_auto_save_env = os.environ.get("CALCULATOR_AUTO_SAVE")
    original_global_config_instance = sys.modules['app.calculator_config'].config

    #Capture and save original logger propagation state
    app_logger = logging.getLogger(APP_LOGGER_NAME)
    original_propagate_setting = app_logger.propagate
    
    # Temporarily set propagate to True so caplog can capture messages
    app_logger.propagate = True 

    # Ensure config is reloaded to pick up env var (this new instance will be used by Calculator)
    sys.modules['app.calculator_config'].config = AppConfig()
    current_global_config_instance = sys.modules['app.calculator_config'].config # Get its reference

    yield current_global_config_instance # Yield the config instance for tests to use

    # Cleanup
    if original_auto_save_env is not None:
        monkeypatch.setenv("CALCULATOR_AUTO_SAVE", original_auto_save_env)
    else:
        monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)
    sys.modules['app.calculator_config'].config = original_global_config_instance

    #Restore original logger propagation state
    app_logger.propagate = original_propagate_setting


def test_autosave_observer_saves_when_enabled(mocker, manage_config_for_autosave_tests, caplog):
    """Test AutoSaveObserver calls save_history when auto-save is enabled."""
    mock_save_history = mocker.patch.object(Calculator, 'save_history')
    
    # Get config from fixture and set AUTO_SAVE for this test
    current_test_config = manage_config_for_autosave_tests # This IS the yielded config
    current_test_config.AUTO_SAVE = True

    with caplog.at_level(logging.INFO, logger=APP_LOGGER_NAME):
        caplog.clear() # Clear logs captured before this specific test block
        calculator = Calculator() # Instantiate AFTER config is set
        observer = AutoSaveObserver(current_test_config) # Pass the config
        
        observer.update(calculator) # Manually trigger update

        mock_save_history.assert_called_once()
        assert "OBSERVER: Auto-saving calculation history..." in caplog.text

def test_autosave_observer_does_not_save_when_disabled(mocker, manage_config_for_autosave_tests, caplog):
    """Test AutoSaveObserver does not call save_history when auto-save is disabled."""
    mock_save_history = mocker.patch.object(Calculator, 'save_history')

    # Get config from fixture and set AUTO_SAVE for this test
    current_test_config = manage_config_for_autosave_tests # This IS the yielded config
    current_test_config.AUTO_SAVE = False

    with caplog.at_level(logging.INFO, logger=APP_LOGGER_NAME):
        caplog.clear() # Clear logs captured before this specific test block
        calculator = Calculator() # Instantiate AFTER config is set
        observer = AutoSaveObserver(current_test_config) # Pass the config
        
        observer.update(calculator) # Manually trigger update

        mock_save_history.assert_not_called()
        assert "OBSERVER: Auto-save is disabled in configuration." in caplog.text

def test_autosave_observer_handles_unexpected_subject_type(mocker, caplog, manage_config_for_autosave_tests): # <--- ADD FIXTURE HERE
    """Test AutoSaveObserver logs a warning for unexpected subject types."""
    mock_save_history = mocker.patch.object(Calculator, 'save_history')

    # Get config from fixture (value doesn't matter for this test's logic)
    current_test_config = manage_config_for_autosave_tests # This IS the yielded config

    with caplog.at_level(logging.WARNING, logger=APP_LOGGER_NAME):
        caplog.clear() # Clear logs captured before this specific test block
        observer = AutoSaveObserver(current_test_config) # Pass the config
        observer.update("not_a_calculator_subject") # Pass an invalid subject type

        mock_save_history.assert_not_called()
        assert "AutoSaveObserver received update from unexpected subject type" in caplog.text
        assert "not_a_calculator_subject" not in caplog.text

# Test integration with Calculator (will be covered by app/calculator tests primarily)
def test_calculator_notifies_autosave_observer(mocker):
    """Test Calculator notifies AutoSaveObserver on new calculation."""
    mocker.patch.object(AutoSaveObserver, 'update')
    
    calculator = Calculator() # This test doesn't explicitly modify config, so default applies
    
    # AutoSaveObserver will use the globally imported config in app/autosave_observer.py
    # which is managed by manage_config_for_autosave_tests implicitly via sys.modules.
    # No explicit config passing needed for THIS specific test.
    mock_autosave_observer = AutoSaveObserver()
    calculator.attach(mock_autosave_observer)

    calculator.execute_operation("add", "1", "2")

    mock_autosave_observer.update.assert_called_once_with(calculator)

    calculator.detach(mock_autosave_observer)