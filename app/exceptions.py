
class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass

class OperationError(CalculatorError):
    """Exception raised for errors during an arithmetic operation (e.g., invalid operands)."""
    pass

class ValidationError(CalculatorError):
    """Exception raised for invalid input or configuration values."""
    pass

class HistoryError(CalculatorError):
    """Exception raised for errors related to history management (e.g., undo/redo on empty history)."""
    pass

class ConfigError(CalculatorError):
    """Exception raised for errors related to application configuration."""
    pass

class DataPersistenceError(CalculatorError):
    """Exception raised for errors during saving or loading data."""
    pass