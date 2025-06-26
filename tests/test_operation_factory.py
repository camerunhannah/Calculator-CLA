# tests/test_operation_factory.py

import pytest
from app.operation_factory import OperationFactory
from app.operations import Add, Subtract, Multiply, Divide, Power, NthRoot, Hypotenuse
from app.calculation import Calculation 
from datetime import datetime
from app.calculator import Calculator 

def test_factory_creates_add_operation():
    """Test that the factory correctly creates an Add operation."""
    op = OperationFactory.create_operation("add", 5, 3)
    assert isinstance(op, Add)
    assert op.execute() == 8

def test_factory_creates_subtract_operation():
    """Test that the factory correctly creates a Subtract operation."""
    op = OperationFactory.create_operation("subtract", 10, 4)
    assert isinstance(op, Subtract)
    assert op.execute() == 6

def test_factory_creates_multiply_operation():
    """Test that the factory correctly creates a Multiply operation."""
    op = OperationFactory.create_operation("multiply", 6, 7)
    assert isinstance(op, Multiply)
    assert op.execute() == 42

def test_factory_creates_divide_operation():
    """Test that the factory correctly creates a Divide operation."""
    op = OperationFactory.create_operation("divide", 10, 2)
    assert isinstance(op, Divide)
    assert op.execute() == 5

def test_factory_creates_power_operation():
    """Test that the factory correctly creates a Power operation."""
    op = OperationFactory.create_operation("power", 2, 3)
    assert isinstance(op, Power)
    assert op.execute() == 8

def test_factory_creates_nth_root_operation():
    """Test that the factory correctly creates an NthRoot operation."""
    op = OperationFactory.create_operation("root", 8, 3)
    assert isinstance(op, NthRoot)
    assert op.execute() == pytest.approx(2)

def test_factory_creates_hypotenuse_operation():
    """Test that the factory correctly creates a Hypotenuse operation."""
    op = OperationFactory.create_operation("hypotenuse", 3, 4)
    assert isinstance(op, Hypotenuse)
    assert op.execute() == pytest.approx(5)

def test_factory_raises_error_for_unsupported_operation():
    """Test that the factory raises ValueError for an unsupported operation name."""
    with pytest.raises(ValueError, match="Unsupported operation: unknown_op"):
        OperationFactory.create_operation("unknown_op", 1, 2)

def test_calculator_execute_operation():
    """Test the Calculator's execute_operation method."""
    calculator = Calculator()
    calculation = calculator.execute_operation("add", 5, 3)
    assert calculation.operation_name == "add"
    assert calculation.operand_a == 5
    assert calculation.operand_b == 3
    assert calculation.result == 8
    assert isinstance(calculation.timestamp, type(Calculation(None,None,None,None).timestamp)) # Check datetime type

def test_calculator_execute_operation_unsupported_error():
    """Test Calculator handles unsupported operation errors from factory."""
    calculator = Calculator()
    with pytest.raises(ValueError, match="Unsupported operation: bad_op"):
        calculator.execute_operation("bad_op", 1, 2)

def test_calculator_execute_operation_division_by_zero_error():
    """Test Calculator handles division by zero error from operation."""
    calculator = Calculator()
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        calculator.execute_operation("divide", 5, 0)