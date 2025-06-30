# app/operations.py (Updated for consistent operation names and Operation.__str__)
from abc import ABC, abstractmethod
from decimal import Decimal
import logging

from app.exceptions import OperationError

class Operation(ABC):
    """
    Abstract Base Class for all calculator operations.
    Defines the interface for executing an operation.
    """
    @abstractmethod
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        """
        Executes the specific arithmetic operation.
        """
        pass

    def __str__(self) -> str: # Returns descriptive name, e.g., "Addition"
        return self.__class__.__name__

class Addition(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        return operand1 + operand2

class Subtraction(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        return operand1 - operand2

class Multiplication(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        return operand1 * operand2

class Division(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 == 0:
            raise OperationError("Division by zero is not allowed")
        return operand1 / operand2

class Power(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 < 0:
            raise OperationError("Negative exponents are not supported")
        return Decimal(pow(float(operand1), float(operand2)))

class Root(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 == 0:
            raise OperationError("Zero root is undefined")
        if operand1 < 0 and operand2 % 2 == 0:
            raise OperationError("Cannot calculate even root of a negative number")
        
        if operand1 < 0 and operand2 % 2 != 0:
            return -Decimal(pow(float(abs(operand1)), 1 / float(operand2)))
        
        return Decimal(pow(float(operand1), 1 / float(operand2)))

class Modulus(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 == 0:
            raise OperationError("Modulo by zero is not allowed")
        return operand1 % operand2

class IntegerDivision(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 == 0:
            raise OperationError("Integer division by zero is not allowed")
        return operand1 // operand2

class PercentageCalculation(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        if operand2 == 0:
            raise OperationError("Cannot calculate percentage with zero as the base")
        return (operand1 / operand2) * Decimal('100')

class AbsoluteDifference(Operation):
    def execute(self, operand1: Decimal, operand2: Decimal) -> Decimal:
        return abs(operand1 - operand2)

class OperationFactory:
    """
    Factory class to create instances of Operation.
    _operations maps short, lowercase command strings to Operation classes.
    """
    _operations = {
        "add": Addition,
        "subtract": Subtraction,
        "multiply": Multiplication,
        "divide": Division,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivision,
        "percent": PercentageCalculation,
        "abs_diff": AbsoluteDifference
    }

    @staticmethod
    def create_operation(operation_name: str) -> Operation:
        """
        Creates and returns an instance of the specified operation.
        Expects operation_name to be a short, lowercase command string.
        """
        op_class = OperationFactory._operations.get(operation_name)
        if not op_class:
            raise OperationError(f"Unknown operation: {operation_name}")
        return op_class()