"""
Factory pattern for calculation operations.

This module implements the Factory design pattern to create different
calculation operations (Add, Subtract, Multiply, Divide) dynamically.
"""
from abc import ABC, abstractmethod
from typing import Dict, Type


class Operation(ABC):
    """
    Abstract base class for all calculation operations.
    
    Each concrete operation must implement the calculate method.
    """
    
    @abstractmethod
    def calculate(self, a: float, b: float) -> float:
        """
        Perform the calculation.
        
        Args:
            a: First operand
            b: Second operand
            
        Returns:
            Result of the calculation
        """
        pass


class AddOperation(Operation):
    """Addition operation."""
    
    def calculate(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b


class SubtractOperation(Operation):
    """Subtraction operation."""
    
    def calculate(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b


class MultiplyOperation(Operation):
    """Multiplication operation."""
    
    def calculate(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b


class DivideOperation(Operation):
    """Division operation."""
    
    def calculate(self, a: float, b: float) -> float:
        """
        Divide a by b.
        
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b


class CalculationFactory:
    """
    Factory class for creating calculation operations.
    
    Uses a registry pattern to map operation types to their implementations.
    """
    
    # Registry mapping operation names to their classes
    _operations: Dict[str, Type[Operation]] = {
        "Add": AddOperation,
        "Subtract": SubtractOperation,
        "Multiply": MultiplyOperation,
        "Divide": DivideOperation,
    }
    
    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance based on the operation type.
        
        Args:
            operation_type: Type of operation (Add, Subtract, Multiply, Divide)
            
        Returns:
            An instance of the appropriate Operation subclass
            
        Raises:
            ValueError: If operation_type is not supported
        """
        operation_class = cls._operations.get(operation_type)
        if operation_class is None:
            raise ValueError(
                f"Unsupported operation type: {operation_type}. "
                f"Supported types: {', '.join(cls._operations.keys())}"
            )
        return operation_class()
    
    @classmethod
    def get_supported_operations(cls) -> list[str]:
        """
        Get a list of supported operation types.
        
        Returns:
            List of supported operation names
        """
        return list(cls._operations.keys())
    
    @classmethod
    def calculate(cls, operation_type: str, a: float, b: float) -> float:
        """
        Convenience method to create an operation and calculate in one step.
        
        Args:
            operation_type: Type of operation
            a: First operand
            b: Second operand
            
        Returns:
            Result of the calculation
        """
        operation = cls.create_operation(operation_type)
        return operation.calculate(a, b)
