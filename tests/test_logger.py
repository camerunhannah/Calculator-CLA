import pytest
import os
import logging
import re
import sys 


from app.logger import LOG_FILE_NAME, APP_LOGGER_NAME
from app.calculator_config import AppConfig 

@pytest.fixture(autouse=True)
def setup_isolated_logging(tmp_path):
    """
    Sets up a temporary log directory and a fresh, isolated logger specifically for the test.
    This fixture ensures complete isolation of logging configuration for each test run.
    """
    # 1. Capture original global state for cleanup
    original_global_config_instance = sys.modules['app.calculator_config'].config
    original_env_log_dir = os.environ.get("CALCULATOR_LOG_DIR")

 
    root_logger = logging.getLogger()
    app_logger = logging.getLogger(APP_LOGGER_NAME)

    original_root_handlers = root_logger.handlers[:]
    original_app_logger_handlers = app_logger.handlers[:]

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    for handler in app_logger.handlers[:]:
        app_logger.removeHandler(handler)

 
    test_log_dir = tmp_path / "test_logs_isolated"
    test_log_dir.mkdir(exist_ok=True)
    os.environ["CALCULATOR_LOG_DIR"] = str(test_log_dir) 


    sys.modules['app.calculator_config'].config = AppConfig()
    current_test_config = sys.modules['app.calculator_config'].config

    
    test_logger = logging.getLogger(APP_LOGGER_NAME)
    test_logger.setLevel(logging.INFO)
    test_logger.propagate = False 

    file_handler = logging.FileHandler(
        os.path.join(test_log_dir, LOG_FILE_NAME),
        encoding=current_test_config.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.INFO) 

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)


    test_logger.addHandler(file_handler)

   
    yield test_logger, test_log_dir, current_test_config

    
    if original_env_log_dir is not None:
        os.environ["CALCULATOR_LOG_DIR"] = original_env_log_dir
    else:
        if "CALCULATOR_LOG_DIR" in os.environ:
            del os.environ["CALCULATOR_LOG_DIR"]

 
    sys.modules['app.calculator_config'].config = original_global_config_instance

   
    for handler in test_logger.handlers[:]: 
        test_logger.removeHandler(handler)
    for handler in root_logger.handlers[:]: 
        root_logger.removeHandler(handler)

    for handler in original_root_handlers: 
        root_logger.addHandler(handler)
    for handler in original_app_logger_handlers: 
        app_logger.addHandler(handler)


#BEGINNING OF TEST FUNCTIONS

def test_log_directory_created(setup_isolated_logging):
    """Test that the log directory is created."""
    logger_instance, test_log_dir, _ = setup_isolated_logging
    assert os.path.isdir(test_log_dir)
    assert os.path.exists(test_log_dir)

def test_log_file_created_and_written_to(setup_isolated_logging):
    """Test that log file is created and a message is written."""
    logger_instance, test_log_dir, test_config = setup_isolated_logging
    test_message = "This is a test log message."
    logger_instance.info(test_message)
    logger_instance.handlers[0].flush() # Ensure log is written to file immediately

    log_file_path = os.path.join(test_log_dir, LOG_FILE_NAME)
    assert os.path.isfile(log_file_path)

    with open(log_file_path, 'r', encoding=test_config.DEFAULT_ENCODING) as f:
        content = f.read()
    assert test_message in content
    assert "INFO" in content
    assert APP_LOGGER_NAME in content

def test_logging_levels(setup_isolated_logging):
    """Test different logging levels are handled."""
    logger_instance, test_log_dir, test_config = setup_isolated_logging
    logger_instance.debug("Debug message") 
    logger_instance.info("Info message")
    logger_instance.warning("Warning message")
    logger_instance.error("Error message")
    logger_instance.handlers[0].flush() 

    log_file_path = os.path.join(test_log_dir, LOG_FILE_NAME)
    with open(log_file_path, 'r', encoding=test_config.DEFAULT_ENCODING) as f:
        content = f.read()

    assert "Debug message" not in content
    assert "Info message" in content
    assert "Warning message" in content
    assert "Error message" in content

def test_logger_instance_is_named_correctly(setup_isolated_logging):
    """Test that the logger instance has the correct name."""
    logger_instance, _, _ = setup_isolated_logging
    assert logger_instance.name == APP_LOGGER_NAME

def test_logger_format(setup_isolated_logging):
    """Test that the log message adheres to the expected format."""
    logger_instance, test_log_dir, test_config = setup_isolated_logging
    test_message = "Format test message."
    logger_instance.info(test_message)
    logger_instance.handlers[0].flush()

    log_file_path = os.path.join(test_log_dir, LOG_FILE_NAME)
    with open(log_file_path, 'r', encoding=test_config.DEFAULT_ENCODING) as f:
        content = f.read()

    match = re.search(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ' + APP_LOGGER_NAME + r' - INFO - Format test message\.$', content, re.MULTILINE)
    assert match is not None, f"Log content did not match expected format: {content}"