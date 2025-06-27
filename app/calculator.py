
from app.operation_factory import OperationFactory
from app.calculation import Calculation
from app.logger import logger
from app.exceptions import ValidationError, OperationError
from app.input_validators import (
    validate_numerical_input,
    validate_operands_within_range,
    validate_division_by_zero,
    validate_nth_root_inputs
)

class Calculator:
    """
    Manages calculator operations, using a factory to create operation instances.
    Also handles input validation and logs operations.
    """
    def execute_operation(self, operation_name: str, operand_a_str: str, operand_b_str: str) -> Calculation:
        """
        Executes a specified operation after validating inputs and returns a Calculation object.

        Args:
            operation_name (str): The name of the operation to perform.
            operand_a_str (str): The first operand as a string (will be validated and converted).
            operand_b_str (str): The second operand as a string (will be validated and converted).

        Returns:
            Calculation: A Calculation object containing operation details and result.

        Raises:
            ValidationError: If inputs are not valid numbers or outside range.
            OperationError: If the operation itself fails (e.g., division by zero, unsupported root).
            Exception: For any unexpected errors.
        """
        # INPUT VALIDATION 
        validate_numerical_input(operand_a_str, "first operand")
        validate_numerical_input(operand_b_str, "second operand")

    
        operand_a = float(operand_a_str)
        operand_b = float(operand_b_str)

        validate_operands_within_range(operand_a, operand_b) 

        # Specific validation based on operation type
        if operation_name == "divide":
            validate_division_by_zero(operand_b)
        elif operation_name == "root":
            validate_nth_root_inputs(operand_a, operand_b)

        logger.info(f"Attempting to execute operation: {operation_name} with inputs {operand_a}, {operand_b}")
        try:
            
            operation = OperationFactory.create_operation(operation_name, operand_a, operand_b)
            result = operation.execute()
            calculation = Calculation(operation.get_name(), operand_a, operand_b, result)
            logger.info(f"Operation '{operation_name}' executed successfully. Result: {result}")
            return calculation
        except (ValidationError, OperationError) as e:
            logger.error(f"Operation failed due to validation or operation error: {e}")
            raise e
        except Exception as e:
            logger.critical(f"An unexpected critical error occurred during operation '{operation_name}': {e}")
            raise OperationError(f"An unexpected error occurred during operation '{operation_name}': {e}")