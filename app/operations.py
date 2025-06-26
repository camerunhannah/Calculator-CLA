# app/operations.py

from abc import ABC, abstractmethod
import math

class Operation(ABC):
    """Abstract base class for all calculator operations."""
    def __init__(self, operand_a: float, operand_b: float):
        self.operand_a = operand_a
        self.operand_b = operand_b

    @abstractmethod
    def execute(self) -> float:
        """Execute the operation and return the result."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the operation."""
        pass

class Add(Operation):
    """Addition operation."""
    def execute(self) -> float:
        return self.operand_a + self.operand_b

    def get_name(self) -> str:
        return "add"

class Subtract(Operation):
    """Subtraction operation."""
    def execute(self) -> float:
        return self.operand_a - self.operand_b

    def get_name(self) -> str:
        return "subtract"

class Multiply(Operation):
    """Multiplication operation."""
    def execute(self) -> float:
        return self.operand_a * self.operand_b

    def get_name(self) -> str:
        return "multiply"

class Divide(Operation):
    """Division operation."""
    def execute(self) -> float:
        if self.operand_b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self.operand_a / self.operand_b

    def get_name(self) -> str:
        return "divide"

class Power(Operation):
    """Power operation (operand_a to the power of operand_b)."""
    def execute(self) -> float:
        return self.operand_a ** self.operand_b

    def get_name(self) -> str:
        return "power"

class NthRoot(Operation):
    """Nth Root operation (the operand_b-th root of operand_a)."""
    def execute(self) -> float:
        if self.operand_b == 0:
            raise ValueError("Root degree cannot be zero.")
        if self.operand_a < 0 and self.operand_b % 2 == 0:
            raise ValueError("Cannot calculate even root of a negative number.")
        return self.operand_a ** (1 / self.operand_b)

    def get_name(self) -> str:
        return "root"

class Hypotenuse(Operation):
    """Calculates the hypotenuse of a right triangle (sqrt(a^2 + b^2))."""
    def execute(self) -> float:
        return math.hypot(self.operand_a, self.operand_b)

    def get_name(self) -> str:
        return "hypotenuse"