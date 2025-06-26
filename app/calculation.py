# app/calculation.py

from datetime import datetime
from typing import Union

class Calculation:
    """
    Represents a single calculation performed by the calculator.
    Stores the operation name, operands, result, and a timestamp.
    """
    def __init__(self, operation_name: str, operand_a: float, operand_b: float, result: float, timestamp: datetime = None):
        self.operation_name = operation_name
        self.operand_a = operand_a
        self.operand_b = operand_b
        self.result = result
        self.timestamp = timestamp if timestamp is not None else datetime.now()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Calculation(op='{self.operation_name}', a={self.operand_a}, b={self.operand_b}, "
                f"result={self.result}, time={self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")

    def to_dict(self) -> dict:
        """Converts the calculation to a dictionary for serialization."""
        return {
            'operation': self.operation_name,
            'operand_a': self.operand_a,
            'operand_b': self.operand_b,
            'result': self.result,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Calculation instance from a dictionary."""
        return cls(
            operation_name=data['operation'],
            operand_a=data['operand_a'],
            operand_b=data['operand_b'],
            result=data['result'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )