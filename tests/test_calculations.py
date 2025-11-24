"""
Unit tests for calculation schemas, factory pattern, and operations.
"""
import pytest
import sys
import os
from pydantic import ValidationError
from uuid import UUID, uuid4

# Import only what we need without triggering database connections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import CalculationCreate, CalculationRead, OperationType
from app.factory import (
    CalculationFactory,
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    Operation
)


class TestOperationType:
    """Test suite for OperationType enum."""
    
    def test_operation_type_values(self):
        """Test that all operation types are defined correctly."""
        assert OperationType.ADD.value == "Add"
        assert OperationType.SUBTRACT.value == "Subtract"
        assert OperationType.MULTIPLY.value == "Multiply"
        assert OperationType.DIVIDE.value == "Divide"
    
    def test_operation_type_from_string(self):
        """Test creating OperationType from string."""
        assert OperationType("Add") == OperationType.ADD
        assert OperationType("Subtract") == OperationType.SUBTRACT
        assert OperationType("Multiply") == OperationType.MULTIPLY
        assert OperationType("Divide") == OperationType.DIVIDE


class TestCalculationCreateSchema:
    """Test suite for CalculationCreate schema validation."""
    
    def test_valid_addition(self):
        """Test creating calculation with valid addition data."""
        calc = CalculationCreate(a=10.5, b=5.5, type=OperationType.ADD)
        assert calc.a == 10.5
        assert calc.b == 5.5
        assert calc.type == OperationType.ADD
        assert calc.user_id is None
    
    def test_valid_subtraction(self):
        """Test creating calculation with valid subtraction data."""
        calc = CalculationCreate(a=20.0, b=7.5, type=OperationType.SUBTRACT)
        assert calc.a == 20.0
        assert calc.b == 7.5
        assert calc.type == OperationType.SUBTRACT
    
    def test_valid_multiplication(self):
        """Test creating calculation with valid multiplication data."""
        calc = CalculationCreate(a=3.0, b=4.0, type=OperationType.MULTIPLY)
        assert calc.a == 3.0
        assert calc.b == 4.0
        assert calc.type == OperationType.MULTIPLY
    
    def test_valid_division(self):
        """Test creating calculation with valid division data."""
        calc = CalculationCreate(a=10.0, b=2.0, type=OperationType.DIVIDE)
        assert calc.a == 10.0
        assert calc.b == 2.0
        assert calc.type == OperationType.DIVIDE
    
    def test_division_by_zero_validation(self):
        """Test that division by zero raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(a=10.0, b=0.0, type=OperationType.DIVIDE)
        assert "Division by zero is not allowed" in str(exc_info.value)
    
    def test_division_by_zero_allowed_for_other_operations(self):
        """Test that zero divisor is allowed for non-division operations."""
        # Should not raise error for addition, subtraction, multiplication
        calc_add = CalculationCreate(a=10.0, b=0.0, type=OperationType.ADD)
        assert calc_add.b == 0.0
        
        calc_sub = CalculationCreate(a=10.0, b=0.0, type=OperationType.SUBTRACT)
        assert calc_sub.b == 0.0
        
        calc_mul = CalculationCreate(a=10.0, b=0.0, type=OperationType.MULTIPLY)
        assert calc_mul.b == 0.0
    
    def test_with_user_id(self):
        """Test creating calculation with user_id."""
        user_id = uuid4()
        calc = CalculationCreate(
            a=5.0,
            b=3.0,
            type=OperationType.ADD,
            user_id=user_id
        )
        assert calc.user_id == user_id
    
    def test_invalid_operation_type(self):
        """Test that invalid operation type raises error."""
        with pytest.raises(ValidationError):
            CalculationCreate(a=10.0, b=5.0, type="InvalidOperation")
    
    def test_missing_required_fields(self):
        """Test that missing required fields raises error."""
        with pytest.raises(ValidationError):
            CalculationCreate(a=10.0)  # Missing b and type
    
    def test_negative_numbers(self):
        """Test calculations with negative numbers."""
        calc = CalculationCreate(a=-10.5, b=5.5, type=OperationType.ADD)
        assert calc.a == -10.5
        assert calc.b == 5.5


class TestCalculationReadSchema:
    """Test suite for CalculationRead schema."""
    
    def test_calculation_read_structure(self):
        """Test CalculationRead schema structure."""
        from datetime import datetime
        
        data = {
            "id": uuid4(),
            "a": 10.5,
            "b": 5.5,
            "type": "Add",
            "result": 16.0,
            "user_id": None,
            "created_at": datetime.now()
        }
        
        calc_read = CalculationRead(**data)
        assert isinstance(calc_read.id, UUID)
        assert calc_read.a == 10.5
        assert calc_read.b == 5.5
        assert calc_read.type == "Add"
        assert calc_read.result == 16.0
        assert calc_read.user_id is None


class TestAddOperation:
    """Test suite for AddOperation."""
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        op = AddOperation()
        result = op.calculate(10.5, 5.5)
        assert result == 16.0
    
    def test_add_negative_numbers(self):
        """Test adding negative numbers."""
        op = AddOperation()
        result = op.calculate(-10.5, -5.5)
        assert result == -16.0
    
    def test_add_mixed_signs(self):
        """Test adding positive and negative numbers."""
        op = AddOperation()
        result = op.calculate(10.5, -5.5)
        assert result == 5.0
    
    def test_add_zero(self):
        """Test adding zero."""
        op = AddOperation()
        result = op.calculate(10.5, 0)
        assert result == 10.5


class TestSubtractOperation:
    """Test suite for SubtractOperation."""
    
    def test_subtract_positive_numbers(self):
        """Test subtracting positive numbers."""
        op = SubtractOperation()
        result = op.calculate(10.5, 5.5)
        assert result == 5.0
    
    def test_subtract_larger_from_smaller(self):
        """Test subtracting larger number from smaller."""
        op = SubtractOperation()
        result = op.calculate(5.5, 10.5)
        assert result == -5.0
    
    def test_subtract_negative_numbers(self):
        """Test subtracting negative numbers."""
        op = SubtractOperation()
        result = op.calculate(-10.5, -5.5)
        assert result == -5.0


class TestMultiplyOperation:
    """Test suite for MultiplyOperation."""
    
    def test_multiply_positive_numbers(self):
        """Test multiplying positive numbers."""
        op = MultiplyOperation()
        result = op.calculate(10.0, 5.0)
        assert result == 50.0
    
    def test_multiply_by_zero(self):
        """Test multiplying by zero."""
        op = MultiplyOperation()
        result = op.calculate(10.5, 0)
        assert result == 0.0
    
    def test_multiply_negative_numbers(self):
        """Test multiplying negative numbers."""
        op = MultiplyOperation()
        result = op.calculate(-10.0, -5.0)
        assert result == 50.0
    
    def test_multiply_mixed_signs(self):
        """Test multiplying positive and negative numbers."""
        op = MultiplyOperation()
        result = op.calculate(10.0, -5.0)
        assert result == -50.0


class TestDivideOperation:
    """Test suite for DivideOperation."""
    
    def test_divide_positive_numbers(self):
        """Test dividing positive numbers."""
        op = DivideOperation()
        result = op.calculate(10.0, 2.0)
        assert result == 5.0
    
    def test_divide_by_zero_raises_error(self):
        """Test that division by zero raises ValueError."""
        op = DivideOperation()
        with pytest.raises(ValueError) as exc_info:
            op.calculate(10.0, 0.0)
        assert "Division by zero is not allowed" in str(exc_info.value)
    
    def test_divide_negative_numbers(self):
        """Test dividing negative numbers."""
        op = DivideOperation()
        result = op.calculate(-10.0, -2.0)
        assert result == 5.0
    
    def test_divide_mixed_signs(self):
        """Test dividing positive and negative numbers."""
        op = DivideOperation()
        result = op.calculate(10.0, -2.0)
        assert result == -5.0
    
    def test_divide_resulting_in_decimal(self):
        """Test division resulting in decimal."""
        op = DivideOperation()
        result = op.calculate(10.0, 3.0)
        assert abs(result - 3.3333333333333335) < 0.0001


class TestCalculationFactory:
    """Test suite for CalculationFactory."""
    
    def test_create_add_operation(self):
        """Test factory creates AddOperation."""
        op = CalculationFactory.create_operation("Add")
        assert isinstance(op, AddOperation)
        assert isinstance(op, Operation)
    
    def test_create_subtract_operation(self):
        """Test factory creates SubtractOperation."""
        op = CalculationFactory.create_operation("Subtract")
        assert isinstance(op, SubtractOperation)
    
    def test_create_multiply_operation(self):
        """Test factory creates MultiplyOperation."""
        op = CalculationFactory.create_operation("Multiply")
        assert isinstance(op, MultiplyOperation)
    
    def test_create_divide_operation(self):
        """Test factory creates DivideOperation."""
        op = CalculationFactory.create_operation("Divide")
        assert isinstance(op, DivideOperation)
    
    def test_unsupported_operation_raises_error(self):
        """Test that unsupported operation type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.create_operation("Modulo")
        assert "Unsupported operation type" in str(exc_info.value)
        assert "Modulo" in str(exc_info.value)
    
    def test_get_supported_operations(self):
        """Test getting list of supported operations."""
        operations = CalculationFactory.get_supported_operations()
        assert "Add" in operations
        assert "Subtract" in operations
        assert "Multiply" in operations
        assert "Divide" in operations
        assert len(operations) == 4
    
    def test_calculate_convenience_method_add(self):
        """Test calculate convenience method for addition."""
        result = CalculationFactory.calculate("Add", 10.0, 5.0)
        assert result == 15.0
    
    def test_calculate_convenience_method_subtract(self):
        """Test calculate convenience method for subtraction."""
        result = CalculationFactory.calculate("Subtract", 10.0, 5.0)
        assert result == 5.0
    
    def test_calculate_convenience_method_multiply(self):
        """Test calculate convenience method for multiplication."""
        result = CalculationFactory.calculate("Multiply", 10.0, 5.0)
        assert result == 50.0
    
    def test_calculate_convenience_method_divide(self):
        """Test calculate convenience method for division."""
        result = CalculationFactory.calculate("Divide", 10.0, 5.0)
        assert result == 2.0
    
    def test_calculate_convenience_method_division_by_zero(self):
        """Test calculate convenience method handles division by zero."""
        with pytest.raises(ValueError):
            CalculationFactory.calculate("Divide", 10.0, 0.0)


class TestFactoryIntegration:
    """Integration tests for factory with all operations."""
    
    def test_all_operations_with_same_inputs(self):
        """Test all operations with the same input values."""
        a, b = 20.0, 4.0
        
        add_result = CalculationFactory.calculate("Add", a, b)
        assert add_result == 24.0
        
        subtract_result = CalculationFactory.calculate("Subtract", a, b)
        assert subtract_result == 16.0
        
        multiply_result = CalculationFactory.calculate("Multiply", a, b)
        assert multiply_result == 80.0
        
        divide_result = CalculationFactory.calculate("Divide", a, b)
        assert divide_result == 5.0
    
    def test_chaining_operations(self):
        """Test using factory to chain multiple operations."""
        # (10 + 5) * 2 - 3 = 27
        result1 = CalculationFactory.calculate("Add", 10.0, 5.0)
        result2 = CalculationFactory.calculate("Multiply", result1, 2.0)
        result3 = CalculationFactory.calculate("Subtract", result2, 3.0)
        assert result3 == 27.0
