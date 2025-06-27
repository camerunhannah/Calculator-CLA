# app/logger.py

import logging
import os
from app.calculator_config import config

# --- MAKE APP_LOGGER_NAME A TOP-LEVEL GLOBAL CONSTANT ---
LOG_FILE_NAME = "calculator.log"
APP_LOGGER_NAME = "calculator_app" # <--- THIS IS NOW A GLOBAL CONSTANT


def setup_logging():
    """
    Sets up the application's logging configuration for the named 'calculator_app' logger.
    Logs messages to a file specified by CALCULATOR_LOG_DIR in config.
    """
    log_directory = config.LOG_DIR
    os.makedirs(log_directory, exist_ok=True) # Ensure the log directory exists

    log_file_path = os.path.join(log_directory, LOG_FILE_NAME)

    # Get the specific logger instance for our application
    app_logger = logging.getLogger(APP_LOGGER_NAME) # Use the global constant
    app_logger.setLevel(logging.INFO) # Set default logging level for this logger

    # Clear existing handlers from this specific logger to prevent duplicate logs on re-setup
    for handler in app_logger.handlers[:]:
        app_logger.removeHandler(handler)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path, encoding=config.DEFAULT_ENCODING)
    file_handler.setLevel(logging.INFO) # Handler's level

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to our application logger
    app_logger.addHandler(file_handler)

    # Prevent messages from propagating to the root logger, which might have other handlers
    app_logger.propagate = False

    app_logger.info(f"Logging started. Log file: {log_file_path}")
    return app_logger

# Initialize the logger instance when this module is imported
logger = setup_logging()