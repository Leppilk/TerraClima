"""Módulo de processamento de dados meteorológicos."""

from .loader import DataLoader
from .processor import DataProcessor
from .aggregator import DataAggregator

__all__ = ['DataLoader', 'DataProcessor', 'DataAggregator']
