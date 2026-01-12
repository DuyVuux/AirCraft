"""
Strategy Adapters Package - Data conversion adapters for optimization algorithms.
"""
from .base import IDataAdapter
from src.strategy.orStrategy.or_adapter import OrAdapter

__all__ = ['IDataAdapter', 'OrAdapter']
