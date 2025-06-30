# tests/test_operations.py 
import pytest
from decimal import Decimal
from app.exceptions import OperationError, ValidationError
# Import all concrete operation classes and the OperationFactory
from app.operations import Operation, Addition, Subtraction, Multiplication, Division, \
                           Power, Root, Modulus, IntegerDivision, PercentageCalculation, \
                           AbsoluteDifference, OperationFactory


class TestOperation:
    """Base class for testing individual operations."""
    operation_class = None
    valid_test_cases = {}
    invalid_test_cases = {}

    @pytest.mark.parametrize("name, case", list(valid_test_cases.items()))
    def test_valid_operations(self, name, case):
        """Test operation with valid inputs."""
        operation = self.operation_class()
        a = Decimal(str(case["a"]))
        b = Decimal(str(case["b"]))
        expected = Decimal(str(case["expected"]))
        assert operation.execute(a, b) == expected

    @pytest.mark.parametrize("name, case", list(invalid_test_cases.items()))
    def test_invalid_operations(self, name, case):
        """Test operation with invalid inputs raises appropriate errors."""
        operation = self.operation_class()
        a = Decimal(str(case["a"]))
        b = Decimal(str(case["b"]))
        error = case.get("error", OperationError) # Changed default error to OperationError
        error_message = case.get("message", "")

        with pytest.raises(error, match=error_message):
            operation.execute(a, b)

    def test_str_representation(self): # This test is for the base Operation class's __str__
        """Test that string representation returns class name."""
        # For an abstract class, we need a concrete implementation for testing.
        class ConcreteOperation(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a + b
        assert str(ConcreteOperation()) == "ConcreteOperation"


# Concrete Test Classes for each Operation 

class TestAddition(TestOperation):
    operation_class = Addition
    valid_test_cases = {
        "positive": {"a": 2, "b": 3, "expected": 5},
        "negative": {"a": -2, "b": -3, "expected": -5},
        "mixed": {"a": 2, "b": -3, "expected": -1},
        "decimals": {"a": 2.5, "b": 3.5, "expected": 6.0},
    }

class TestSubtraction(TestOperation):
    operation_class = Subtraction
    valid_test_cases = {
        "positive": {"a": 5, "b": 3, "expected": 2},
        "negative": {"a": -5, "b": -3, "expected": -2},
        "mixed": {"a": 5, "b": -3, "expected": 8},
        "decimals": {"a": 5.5, "b": 3.2, "expected": 2.3},
    }

class TestMultiplication(TestOperation):
    operation_class = Multiplication
    valid_test_cases = {
        "positive": {"a": 4, "b": 2, "expected": 8},
        "zero": {"a": 4, "b": 0, "expected": 0},
        "negative": {"a": -4, "b": 2, "expected": -8},
        "decimals": {"a": 2.5, "b": 2, "expected": 5.0},
    }

class TestDivision(TestOperation):
    operation_class = Division
    valid_test_cases = {
        "positive": {"a": 8, "b": 2, "expected": 4},
        "decimal_result": {"a": 10, "b": 3, "expected": Decimal("3.333333333333333333333333333")}, # Using 28 places for Decimal
        "negative": {"a": -8, "b": 2, "expected": -4},
    }
    invalid_test_cases = {
        "division_by_zero": {"a": 5, "b": 0, "error": OperationError, "message": "Division by zero is not allowed"}
    }

class TestPower(TestOperation):
    operation_class = Power
    valid_test_cases = {
        "positive": {"a": 2, "b": 3, "expected": 8},
        "zero_exponent": {"a": 5, "b": 0, "expected": 1},
        "fractional_exponent": {"a": 9, "b": 0.5, "expected": 3},
        "negative_base_even_exponent": {"a": -2, "b": 2, "expected": 4},
        "negative_base_odd_exponent": {"a": -2, "b": 3, "expected": -8},
    }
    invalid_test_cases = {
        "negative_exponent": {"a": 2, "b": -3, "error": OperationError, "message": "Negative exponents are not supported"}
    }

class TestRoot(TestOperation):
    operation_class = Root
    valid_test_cases = {
        "square_root": {"a": 16, "b": 2, "expected": 4},
        "cube_root": {"a": 27, "b": 3, "expected": 3},
        "root_of_one": {"a": 1, "b": 5, "expected": 1},
        "root_by_one": {"a": 25, "b": 1, "expected": 25},
        "root_of_zero": {"a": 0, "b": 5, "expected": 0},
        "negative_base_odd_degree": {"a": -27, "b": 3, "expected": -3}, # Cube root of -27 is -3
    }
    invalid_test_cases = {
        "zero_degree": {"a": 16, "b": 0, "error": OperationError, "message": "Zero root is undefined"},
        "negative_base_even_degree": {"a": -16, "b": 2, "error": OperationError, "message": "Cannot calculate even root of a negative number"},
    }

class TestModulus(TestOperation):
    operation_class = Modulus
    valid_test_cases = {
        "positive": {"a": 10, "b": 3, "expected": 1},
        "exact_division": {"a": 10, "b": 2, "expected": 0},
        "negative_dividend": {"a": -10, "b": 3, "expected": 2}, # Python's behavior
        "negative_divisor": {"a": 10, "b": -3, "expected": -2}, # Python's behavior
        "both_negative": {"a": -10, "b": -3, "expected": -1}, # Python's behavior
    }
    invalid_test_cases = {
        "modulus_by_zero": {"a": 10, "b": 0, "error": OperationError, "message": "Modulo by zero is not allowed"}
    }

class TestIntegerDivision(TestOperation):
    operation_class = IntegerDivision
    valid_test_cases = {
        "positive": {"a": 10, "b": 3, "expected": 3},
        "exact_division": {"a": 9, "b": 3, "expected": 3},
        "negative_dividend": {"a": -10, "b": 3, "expected": -4}, # Python's floor division
        "negative_divisor": {"a": 10, "b": -3, "expected": -4}, # Python's floor division
        "both_negative": {"a": -10, "b": -3, "expected": 3}, # Python's floor division
    }
    invalid_test_cases = {
        "integer_division_by_zero": {"a": 10, "b": 0, "error": OperationError, "message": "Integer division by zero is not allowed"}
    }

class TestPercentageCalculation(TestOperation):
    operation_class = PercentageCalculation
    valid_test_cases = {
        "simple": {"a": 50, "b": 200, "expected": 25},
        "one_hundred_percent": {"a": 10, "b": 10, "expected": 100},
        "greater_than_100_percent": {"a": 150, "b": 100, "expected": 150},
        "zero_dividend": {"a": 0, "b": 100, "expected": 0},
    }
    invalid_test_cases = {
        "percentage_by_zero": {"a": 10, "b": 0, "error": OperationError, "message": "Cannot calculate percentage with zero as the base"}
    }

class TestAbsoluteDifference(TestOperation):
    operation_class = AbsoluteDifference
    valid_test_cases = {
        "positive_difference": {"a": 10, "b": 5, "expected": 5},
        "negative_difference": {"a": 5, "b": 10, "expected": 5},
        "same_numbers": {"a": 7, "b": 7, "expected": 0},
        "mixed_signs": {"a": -10, "b": 5, "expected": 15},
        "both_negative": {"a": -10, "b": -5, "expected": 5},
    }


class TestOperationFactory:
    """Tests for the OperationFactory."""

    def test_create_valid_operations(self):
        """Test creation of all valid operations."""
        operation_map = {
            'add': Addition, # Use short names
            'subtract': Subtraction,
            'multiply': Multiplication,
            'divide': Division,
            'power': Power,
            'root': Root,
            'modulus': Modulus,
            'int_divide': IntegerDivision,
            'percent': PercentageCalculation,
            'abs_diff': AbsoluteDifference,
        }

        for op_name, op_class in operation_map.items():
            operation = OperationFactory.create_operation(op_name)
            assert isinstance(operation, op_class)

    def test_create_invalid_operation(self):
        """Test creation of invalid operation raises error."""
        with pytest.raises(OperationError, match="Unknown operation: invalid_op"): # Expected OperationError
            OperationFactory.create_operation("invalid_op")

    # Removed test_register_valid_operation and test_register_invalid_operation
    # as the OperationFactory currently does not have a 'register_operation' method
    # per the initial factory implementation.