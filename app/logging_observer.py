

from app.observer import Observer
from app.logger import logger
from app.calculator import Calculator # To access calculation history from subject
from app.calculation import Calculation # For type hinting

class LoggingObserver(Observer):
    """
    An observer that logs details of new calculations.
    """
    def update(self, subject: 'Calculator'): # Subject is expected to be a Calculator instance
        """
        Logs the latest calculation performed by the calculator.
        """
        if isinstance(subject, Calculator):
            latest_calculation = subject.history.get_latest_calculation()
            if latest_calculation:
                logger.info(f"OBSERVER: Logged Calculation - Operation: {latest_calculation.operation_name}, "
                            f"Operands: {latest_calculation.operand_a}, {latest_calculation.operand_b}, "
                            f"Result: {latest_calculation.result}")
            else:
                logger.info("OBSERVER: Calculation history cleared or no new calculation found.")
        else:
            logger.warning(f"LoggingObserver received update from unexpected subject type: {type(subject)}")