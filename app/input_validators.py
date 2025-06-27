

from app.calculator_config import config 
from app.exceptions import ValidationError, OperationError

def validate_numerical_input(value, param_name: str):
    """
    Validates if a value is a valid float or can be converted to one.
    Raises ValidationError if not.
    """
    try:
        float(value) 
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid input for {param_name}: '{value}' is not a valid number.")

def validate_operands_within_range(operand_a: float, operand_b: float):
    """
    Validates if both operands are within the configured maximum input value range.
    Raises ValidationError if any operand exceeds the limit.
    """
    max_value = config.MAX_INPUT_VALUE
    # DEBUGGING PRINTS
    print(f"\nDEBUG VALIDATION: Validating range.")
    print(f"DEBUG VALIDATION: Operand_a: {operand_a}, Operand_b: {operand_b}, MaxValue: {max_value}")
    print(f"DEBUG VALIDATION: Types - A:{type(operand_a)}, B:{type(operand_b)}, Max:{type(max_value)}")
    print(f"DEBUG VALIDATION: abs(operand_a) > max_value? {abs(operand_a) > max_value}")
    print(f"DEBUG VALIDATION: abs(operand_b) > max_value? {abs(operand_b) > max_value}")
    # END DEBUGGING PRINTS 
    if abs(operand_a) > max_value or abs(operand_b) > max_value:
        raise ValidationError(f"Input values must be within +/- {max_value}. Received: {operand_a}, {operand_b}")

def validate_division_by_zero(operand_b: float):
    """
    Validates if the divisor (operand_b) is zero for division operations.
    Raises OperationError if operand_b is zero.
    """
    if operand_b == 0:
        raise OperationError("Division by zero is not allowed.")

def validate_nth_root_inputs(operand_a: float, operand_b: float):
    """
    Validates inputs specifically for nth root operation.
    Raises OperationError for invalid root degrees or even roots of negative numbers.
    """
    if operand_b == 0:
        raise OperationError("Root degree cannot be zero.")
    if operand_a < 0 and operand_b % 2 == 0:
        raise OperationError("Cannot calculate even root of a negative number.")
  