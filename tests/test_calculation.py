# tests/test_calculation.py 

import pytest
from decimal import Decimal, getcontext
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging
import math

# Set Decimal precision for consistent testing, matching what Calculator might do
getcontext().prec = 28 # Default precision for Decimal operations

# --- Core Operation Tests (using short, lowercase operation_name) ---

def test_addition():
    calc = Calculation(operation_name="add", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("5")

def test_subtraction():
    calc = Calculation(operation_name="subtract", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc.result == Decimal("2")

def test_multiplication():
    calc = Calculation(operation_name="multiply", operand1=Decimal("4"), operand2=Decimal("2"))
    assert calc.result == Decimal("8")

def test_division():
    calc = Calculation(operation_name="divide", operand1=Decimal("8"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")

def test_division_by_zero():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation_name="divide", operand1=Decimal("8"), operand2=Decimal("0"))

def test_power():
    calc = Calculation(operation_name="power", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("8")

def test_power_decimal_exponent():
    calc = Calculation(operation_name="power", operand1=Decimal("9"), operand2=Decimal("0.5"))
    assert calc.result == Decimal("3")

def test_power_zero_exponent():
    calc = Calculation(operation_name="power", operand1=Decimal("5"), operand2=Decimal("0"))
    assert calc.result == Decimal("1")

def test_power_negative_base_even_exponent():
    calc = Calculation(operation_name="power", operand1=Decimal("-2"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")

def test_power_negative_base_odd_exponent():
    calc = Calculation(operation_name="power", operand1=Decimal("-2"), operand2=Decimal("3"))
    assert calc.result == Decimal("-8")

def test_negative_power():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation_name="power", operand1=Decimal("2"), operand2=Decimal("-3"))

def test_root():
    calc = Calculation(operation_name="root", operand1=Decimal("16"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")

def test_root_fractional():
    calc = Calculation(operation_name="root", operand1=Decimal("27"), operand2=Decimal("3"))
    assert math.isclose(float(calc.result), float(Decimal("3")), rel_tol=1e-9)

def test_root_of_one():
    calc = Calculation(operation_name="root", operand1=Decimal("1"), operand2=Decimal("5"))
    assert math.isclose(float(calc.result), float(Decimal("1")), rel_tol=1e-9)

def test_root_by_one():
    calc = Calculation(operation_name="root", operand1=Decimal("25"), operand2=Decimal("1"))
    assert math.isclose(float(calc.result), float(Decimal("25")), rel_tol=1e-9)

def test_root_of_zero():
    calc = Calculation(operation_name="root", operand1=Decimal("0"), operand2=Decimal("5"))
    assert math.isclose(float(calc.result), float(Decimal("0")), rel_tol=1e-9)

def test_root_zero_degree():
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation(operation_name="root", operand1=Decimal("16"), operand2=Decimal("0"))

def test_root_of_negative_number_even_degree():
    with pytest.raises(OperationError, match="Cannot calculate even root of a negative number"):
        Calculation(operation_name="root", operand1=Decimal("-16"), operand2=Decimal("2"))

def test_root_of_negative_number_odd_degree():
    calc = Calculation(operation_name="root", operand1=Decimal("-27"), operand2=Decimal("3"))
    assert math.isclose(float(calc.result), float(Decimal("-3")), rel_tol=1e-9)

def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation: Unknown"):
        Calculation(operation_name="Unknown", operand1=Decimal("5"), operand2=Decimal("3"))

# --- Serialization/Deserialization Tests (using short, lowercase operation_name in data) ---

def test_to_dict():
    calc = Calculation(operation_name="add", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "add",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }

def test_from_dict():
    data = {
        "operation": "add",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation_name == "add"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")

def test_invalid_from_dict():
    data = {
        "operation": "add",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)

def test_format_result():
    calc = Calculation(operation_name="divide", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"
    calc2 = Calculation(operation_name="multiply", operand1=Decimal("2.5"), operand2=Decimal("4"))
    assert calc2.format_result() == "10"
    calc3 = Calculation(operation_name="divide", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc3.format_result(precision=0) == "3"

def test_equality():
    calc1 = Calculation(operation_name="add", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation_name="add", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation_name="subtract", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3

def test_from_dict_result_mismatch(caplog):
    data = {
        "operation": "add",
        "operand1": "2",
        "operand2": "3",
        "result": "10",
        "timestamp": datetime.now().isoformat()
    }

    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)

    assert "Loaded calculation result 10 differs from computed result 5" in caplog.text

# New Operations Tests (using short, lowercase operation_name)

def test_modulus():
    calc = Calculation(operation_name="modulus", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc.result == Decimal("1")
    calc2 = Calculation(operation_name="modulus", operand1=Decimal("10"), operand2=Decimal("2"))
    assert calc2.result == Decimal("0")
    calc3 = Calculation(operation_name="modulus", operand1=Decimal("-10"), operand2=Decimal("3"))
    
    assert calc3.result == Decimal("-1") # Changed from Decimal("2")
    calc4 = Calculation(operation_name="modulus", operand1=Decimal("10"), operand2=Decimal("-3"))
    
    assert calc4.result == Decimal("1") # Changed from Decimal("-2")


def test_modulus_by_zero():
    with pytest.raises(OperationError, match="Modulo by zero is not allowed"):
        Calculation(operation_name="modulus", operand1=Decimal("10"), operand2=Decimal("0"))

def test_integer_division():
    calc = Calculation(operation_name="int_divide", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc.result == Decimal("3")
    calc2 = Calculation(operation_name="int_divide", operand1=Decimal("9"), operand2=Decimal("3"))
    assert calc2.result == Decimal("3")
    calc3 = Calculation(operation_name="int_divide", operand1=Decimal("10"), operand2=Decimal("-3"))
  
    assert calc3.result == Decimal("-3") # Changed from Decimal("-4")
    calc4 = Calculation(operation_name="int_divide", operand1=Decimal("-10"), operand2=Decimal("3"))

    assert calc4.result == Decimal("-3") # Changed from Decimal("-4")

def test_integer_division_by_zero():
    with pytest.raises(OperationError, match="Integer division by zero is not allowed"):
        Calculation(operation_name="int_divide", operand1=Decimal("10"), operand2=Decimal("0"))

def test_percentage_calculation():
    calc = Calculation(operation_name="percent", operand1=Decimal("50"), operand2=Decimal("200"))
    assert calc.result == Decimal("25")
    calc2 = Calculation(operation_name="percent", operand1=Decimal("10"), operand2=Decimal("100"))
    assert calc2.result == Decimal("10")
    calc3 = Calculation(operation_name="percent", operand1=Decimal("150"), operand2=Decimal("100"))
    assert calc3.result == Decimal("150")

def test_percentage_calculation_by_zero():
    with pytest.raises(OperationError, match="Cannot calculate percentage with zero as the base"):
        Calculation(operation_name="percent", operand1=Decimal("10"), operand2=Decimal("0"))

def test_absolute_difference():
    calc = Calculation(operation_name="abs_diff", operand1=Decimal("10"), operand2=Decimal("5"))
    assert calc.result == Decimal("5")
    calc2 = Calculation(operation_name="abs_diff", operand1=Decimal("5"), operand2=Decimal("10"))
    assert calc2.result == Decimal("5")
    calc3 = Calculation(operation_name="abs_diff", operand1=Decimal("-10"), operand2=Decimal("-5"))
    assert calc3.result == Decimal("5")
    calc4 = Calculation(operation_name="abs_diff", operand1=Decimal("10"), operand2=Decimal("-5"))
    assert calc4.result == Decimal("15")