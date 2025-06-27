
import pytest
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.calculator_config import AppConfig # Only AppConfig class
from app.exceptions import ValidationError, OperationError
from app.input_validators import validate_numerical_input, validate_operands_within_range, validate_division_by_zero, validate_nth_root_inputs
from app.calculator import Calculator # Import Calculator for its tests
from app.calculation import Calculation # Import Calculation for its type checks

# Fixture to temporarily set/clear environment variables and modify config for tests
@pytest.fixture(autouse=True)
def manage_config_env(monkeypatch):
    # Capture original state of the global config instance
    from app.calculator_config import config as original_global_config_instance

    # Instead of monkeypatching env var and reloading, directly patch the config's attribute
    # This is more robust for singletons like 'config'
    monkeypatch.setattr(original_global_config_instance, "MAX_INPUT_VALUE", 1000.0)

    yield # Run the test

    # Cleanup: restore original global config instance
    sys.modules['app.calculator_config'].config = original_global_config_instance


#Tests for validate_numerical_input
def test_validate_numerical_input_valid():
    """Test valid numerical inputs pass validation."""
    validate_numerical_input("10", "num")
    validate_numerical_input("10.5", "num")
    validate_numerical_input("-5", "num")
    validate_numerical_input("0", "num")
    validate_numerical_input("1e-5", "num") # Scientific notation

def test_validate_numerical_input_invalid_raises_error():
    """Test invalid numerical inputs raise ValidationError."""
    with pytest.raises(ValidationError, match="not a valid number"):
        validate_numerical_input("abc", "num")
    with pytest.raises(ValidationError, match="not a valid number"):
        validate_numerical_input("", "num")
    with pytest.raises(ValidationError, match="not a valid number"):
        validate_numerical_input(None, "num") # Non-string type that can't convert

#Tests for validate_operands_within_range
def test_validate_operands_within_range_valid():
    """Test operands within range pass validation."""
    validate_operands_within_range(500.0, 750.0)
    validate_operands_within_range(-500.0, -750.0)
    validate_operands_within_range(0.0, 0.0)

def test_validate_operands_within_range_exceeds_max_raises_error():
    """Test operands exceeding max range raise ValidationError."""
    # The fixture now directly sets config.MAX_INPUT_VALUE to 1000.0
    with pytest.raises(ValidationError, match="Input values must be within"):
        validate_operands_within_range(1001.0, 500.0)
    with pytest.raises(ValidationError, match="Input values must be within"):
        validate_operands_within_range(500.0, -1001.0)
    with pytest.raises(ValidationError, match="Input values must be within"):
        validate_operands_within_range(2000.0, 2000.0)

#Tests for validate_division_by_zero
def test_validate_division_by_zero_valid():
    """Test non-zero divisor passes validation."""
    validate_division_by_zero(5.0)
    validate_division_by_zero(-0.1)

def test_validate_division_by_zero_raises_error():
    """Test zero divisor raises OperationError."""
    with pytest.raises(OperationError, match="Division by zero is not allowed."):
        validate_division_by_zero(0.0)

#Tests for validate_nth_root_inputs
def test_validate_nth_root_inputs_valid():
    """Test valid nth root inputs pass validation."""
    validate_nth_root_inputs(8.0, 3.0) # Cube root of 8
    validate_nth_root_inputs(16.0, 4.0) # 4th root of 16
    validate_nth_root_inputs(-8.0, 3.0) # Cube root of -8 (valid)
    validate_nth_root_inputs(0.0, 5.0) # 5th root of 0

def test_validate_nth_root_inputs_zero_degree_raises_error():
    """Test zero root degree raises OperationError."""
    with pytest.raises(OperationError, match="Root degree cannot be zero."):
        validate_nth_root_inputs(10.0, 0.0)

def test_validate_nth_root_inputs_even_of_negative_raises_error():
    """Test even root of negative number raises OperationError."""
    with pytest.raises(OperationError, match="Cannot calculate even root of a negative number."):
        validate_nth_root_inputs(-8.0, 2.0) # Square root of -8

#Combined tests for Calculator integration
def test_calculator_handles_invalid_numerical_input():
    """Test Calculator raises ValidationError for non-numeric input strings."""
    calculator = Calculator()
    with pytest.raises(ValidationError, match="not a valid number"):
        calculator.execute_operation("add", "abc", "2")
    with pytest.raises(ValidationError, match="not a valid number"):
        calculator.execute_operation("subtract", "10", "xyz")

def test_calculator_handles_inputs_out_of_range():
    """Test Calculator raises ValidationError for inputs exceeding max value."""
    calculator = Calculator()
    # MAX_INPUT_VALUE is 1000.0 from fixture
    with pytest.raises(ValidationError, match="Input values must be within"):
        calculator.execute_operation("multiply", "1001", "5")
    with pytest.raises(ValidationError, match="Input values must be within"):
        calculator.execute_operation("add", "-10", "-1000.1")

def test_calculator_handles_division_by_zero_with_operation_error():
    """Test Calculator handles division by zero and raises OperationError."""
    calculator = Calculator()
    with pytest.raises(OperationError, match="Division by zero is not allowed."):
        calculator.execute_operation("divide", "5", "0")

def test_calculator_handles_invalid_nth_root_inputs_with_operation_error():
    """Test Calculator handles invalid nth root inputs and raises OperationError."""
    calculator = Calculator()
    with pytest.raises(OperationError, match="Root degree cannot be zero."):
        calculator.execute_operation("root", "10", "0")
    with pytest.raises(OperationError, match="Cannot calculate even root of a negative number."):
        calculator.execute_operation("root", "-8", "2")

def test_calculator_successful_operation_with_valid_string_inputs():
    """Test Calculator successfully executes operation with valid string inputs."""
    calculator = Calculator()
    calculation = calculator.execute_operation("add", "5", "3")
    assert calculation.operation_name == "add"
    assert calculation.operand_a == 5.0
    assert calculation.operand_b == 3.0
    assert calculation.result == 8.0

    calculation = calculator.execute_operation("power", "2", "3")
    assert calculation.operation_name == "power"
    assert calculation.result == 8.0