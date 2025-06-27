
from app.operations import (
    Add, Subtract, Multiply, Divide, Power, NthRoot, Hypotenuse,
    Modulus, IntegerDivision, Percentage, AbsoluteDifference 
)

class OperationFactory:
    """
    A factory class for creating instances of Operation based on a string name.
    """
    _operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": NthRoot,
        "hypotenuse": Hypotenuse,
        "modulus": Modulus,
        "int_divide": IntegerDivision,
        "percent": Percentage,
        "abs_diff": AbsoluteDifference,
    }

    @classmethod
    def create_operation(cls, operation_name: str, operand_a: float, operand_b: float):
        """
        Creates and returns an instance of the specified operation.

        Args:
            operation_name (str): The name of the operation (e.g., "add", "divide").
            operand_a (float): The first operand.
            operand_b (float): The second operand.

        Returns:
            Operation: An instance of the requested operation.

        Raises:
            ValueError: If the operation name is not supported.
        """
        operation_class = cls._operations.get(operation_name)
        if not operation_class:
            raise ValueError(f"Unsupported operation: {operation_name}")
        return operation_class(operand_a, operand_b)