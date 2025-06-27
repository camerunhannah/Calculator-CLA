# app/calculator.py

from app.operation_factory import OperationFactory
from app.calculation import Calculation
from app.logger import logger # <--- ADD THIS IMPORT

class Calculator:
    """
    Manages calculator operations, using a factory to create operation instances.
    """
    def execute_operation(self, operation_name: str, operand_a: float, operand_b: float) -> Calculation:
        """
        Executes a specified operation and returns a Calculation object.

        Args:
            operation_name (str): The name of the operation to perform.
            operand_a (float): The first operand.
            operand_b (float): The second operand.

        Returns:
            Calculation: A Calculation object containing operation details and result.

        Raises:
            ValueError: If the operation is unsupported or calculation fails (e.g., division by zero).
        """
        logger.info(f"Attempting to execute operation: {operation_name} with inputs {operand_a}, {operand_b}")
        try:
            # Use the Factory to create the operation instance
            operation = OperationFactory.create_operation(operation_name, operand_a, operand_b)
            result = operation.execute()
            # Create a Calculation object to record the details
            calculation = Calculation(operation.get_name(), operand_a, operand_b, result)
            logger.info(f"Operation '{operation_name}' executed successfully. Result: {result}")
            return calculation
        except ValueError as e:
            logger.error(f"Error executing operation '{operation_name}': {e}")
            raise e
        except Exception as e:
            logger.critical(f"An unexpected critical error occurred during operation '{operation_name}': {e}")
            raise ValueError(f"An unexpected error occurred during operation '{operation_name}': {e}")