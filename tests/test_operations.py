# tests/test_operations.py

import pytest
import math # Needed for math.sqrt in hypotenuse test

# Consolidate all operation imports into one line
from app.operations import Add, Subtract, Multiply, Divide, Power, NthRoot, Hypotenuse

def test_add_operation():
    """Test the Add operation with positive numbers."""
    op = Add(5, 3)
    assert op.execute() == 8
    assert op.get_name() == "add"

def test_subtract_operation():
    """Test the Subtract operation with positive numbers."""
    op = Subtract(10, 4)
    assert op.execute() == 6
    assert op.get_name() == "subtract"

def test_multiply_operation():
    """Test the Multiply operation with positive numbers."""
    op = Multiply(6, 7)
    assert op.execute() == 42
    assert op.get_name() == "multiply"

def test_divide_operation():
    """Test the Divide operation with positive numbers."""
    op = Divide(10, 2)
    assert op.execute() == 5
    assert op.get_name() == "divide"

def test_divide_by_zero_raises_error():
    """Test that Divide operation raises ValueError on division by zero."""
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        op = Divide(5, 0)
        op.execute()

def test_power_operation():
    """Test the Power operation."""
    op = Power(2, 3) # 2^3 = 8
    assert op.execute() == 8
    assert op.get_name() == "power"

    op = Power(4, 0.5) # 4^0.5 = 2 (square root)
    assert op.execute() == 2
    assert op.get_name() == "power"

def test_nth_root_operation():
    """Test the NthRoot operation."""
    op = NthRoot(8, 3) # cube root of 8 = 2
    assert op.execute() == pytest.approx(2) # Use pytest.approx for float comparisons
    assert op.get_name() == "root"

    op = NthRoot(16, 4) # 4th root of 16 = 2
    assert op.execute() == pytest.approx(2)

def test_nth_root_of_zero_degree_raises_error():
    """Test that NthRoot operation raises ValueError for degree zero."""
    with pytest.raises(ValueError, match="Root degree cannot be zero."):
        op = NthRoot(10, 0)
        op.execute()

def test_nth_root_even_of_negative_raises_error():
    """Test that NthRoot operation raises ValueError for even root of negative."""
    with pytest.raises(ValueError, match="Cannot calculate even root of a negative number."):
        op = NthRoot(-8, 2) # Square root of -8
        op.execute()

def test_hypotenuse_operation():
    """Test the Hypotenuse operation with standard values."""
    op = Hypotenuse(3, 4) # 3^2 + 4^2 = 9 + 16 = 25, sqrt(25) = 5
    assert op.execute() == pytest.approx(5.0) # Use approx for float comparisons
    assert op.get_name() == "hypotenuse"

def test_hypotenuse_with_zero_and_negative():
    """Test Hypotenuse with zero and negative inputs (squares make them positive)."""
    op = Hypotenuse(0, 5) # sqrt(0^2 + 5^2) = 5
    assert op.execute() == pytest.approx(5.0)

    op = Hypotenuse(-3, -4) # sqrt((-3)^2 + (-4)^2) = sqrt(9 + 16) = 5
    assert op.execute() == pytest.approx(5.0)

def test_hypotenuse_with_floats():
    """Test Hypotenuse with floating point numbers."""
    op = Hypotenuse(1.0, 1.0) # sqrt(1^2 + 1^2) = sqrt(2)
    assert op.execute() == pytest.approx(math.sqrt(2))