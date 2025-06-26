# app/calculator.py

from app.operation_factory import OperationFactory
from app.calculation import Calculation

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
        try:
            
            operation = OperationFactory.create_operation(operation_name, operand_a, operand_b)
            result = operation.execute()
          
            calculation = Calculation(operation.get_name(), operand_a, operand_b, result)
            return calculation
        except ValueError as e:
            # Re-raise ValueErrors from operations (like division by zero or invalid root)
            raise e
        except Exception as e:
            # Catch any other unexpected errors during execution
            raise ValueError(f"An unexpected error occurred during operation '{operation_name}': {e}")