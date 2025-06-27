
from app.observer import Observer
from app.logger import logger
from app.calculator import Calculator # To access history and trigger save
from app.calculator_config import config as app_config_singleton # Import the global config singleton

class AutoSaveObserver(Observer):
    """
    An observer that automatically saves the calculation history.
    """
    def __init__(self, config_instance=None): 
        # Use provided config_instance or fallback to the app's global singleton
        self.config = config_instance if config_instance is not None else app_config_singleton

    def update(self, subject: 'Calculator'): # Subject is expected to be a Calculator instance
        """
        Automatically saves the calculator history if auto-save is enabled.
        """
        if not self.config.AUTO_SAVE:
            logger.info("OBSERVER: Auto-save is disabled in configuration.")
            return

        if isinstance(subject, Calculator):
            logger.info("OBSERVER: Auto-saving calculation history...")
            subject.save_history()
        else:
            logger.warning(f"AutoSaveObserver received update from unexpected subject type: {type(subject)}")