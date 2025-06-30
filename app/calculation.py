# app/calculation.py (Updated for consistent operation_name storage)
from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation, getcontext
import logging
from typing import Any, Dict

from app.exceptions import OperationError
from app.operations import OperationFactory, Operation

@dataclass
class Calculation:
    """
    Value Object representing a single calculation.
    """

    operation_name: str      # The short, lowercase name of the operation (e.g., "add", "power")
    operand1: Decimal       # The first operand in the calculation
    operand2: Decimal       # The second operand in the calculation
    
    _operation_instance: Operation = field(init=False, repr=False)

    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        """
        Post-initialization processing.
        """
        # Create the operation instance using the factory, passing the short operation_name
        self._operation_instance = OperationFactory.create_operation(self.operation_name)
        self.result = self.calculate()

    def calculate(self) -> Decimal:
        """
        Execute calculation using the specified operation instance.
        """
        try:
            return self._operation_instance.execute(self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as e:
            raise OperationError(f"Calculation failed: {str(e)}") # pragma: no cover
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert calculation to dictionary for serialization.
        The 'operation' key will store the short, lowercase name.
        """
        return {
            'operation': self.operation_name, # Storing the short name (e.g., "add")
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """
        Create calculation from dictionary.
        Expects the 'operation' key in data to be the short, lowercase name.
        """
        try:
            calc = Calculation(
                operation_name=data['operation'], # Expecting the short name from data
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2'])
            )

            calc.timestamp = datetime.datetime.fromisoformat(data['timestamp'])

            saved_result = Decimal(data['result'])
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded calculation result {saved_result} "
                    f"differs from computed result {calc.result}"
                ) # pragma: no cover

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    def __str__(self) -> str:
        """
        Return string representation of calculation.
        Uses the descriptive name from the operation instance, not the stored short name.
        """
        descriptive_name = str(self._operation_instance) # e.g., "Addition" from the Operation class's __str__
        return f"{descriptive_name}({self.operand1}, {self.operand2}) = {self.result}" # pragma: no cover

    def __repr__(self) -> str:
        """
        Return detailed string representation of calculation.
        """
        # Using the actual stored operation_name for repr for precise representation
        return ( # pragma: no cover
            f"Calculation(operation_name='{self.operation_name}', "
            f"operand1={self.operand1}, "
            f"operand2={self.operand2}, "
            f"result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        """
        Check if two calculations are equal.
        """
        if not isinstance(other, Calculation):
            return NotImplemented # pragma: no cover
        return (
            self.operation_name == other.operation_name and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        """
        Format the calculation result with specified precision.
        Adjusted to be compatible with Python versions < 3.10 (no Decimal.localcontext).
        """
        try:
            # Get the current global context
            original_context = getcontext()
           
            quantizer = Decimal('0.' + '0' * precision)
            quantized_result = self.result.quantize(quantizer)
            
            # Normalize to remove trailing zeros for whole numbers or exact decimals
            normalized_result = quantized_result.normalize()

            if normalized_result == normalized_result.to_integral_value():
                return str(int(normalized_result))
            else:
                return str(normalized_result)
        except InvalidOperation: # pragma: no cover
            return str(self.result)