"""
Cost Sharing with Shapley Value

A comprehensive system for fair cost allocation using Shapley values from
cooperative game theory. Includes applications for cloud computing and ridesharing.
"""

from .shapley_value import ShapleyValue, ShapleyAnalyzer, compare_algorithms
from .cloud_cost_sharing import CloudCostSharingSystem, CloudCostModel, Customer
from .rideshare_cost import RideshareCostSharingSystem, RideshareCostModel, Rider, Location

__version__ = '1.0.0'

__all__ = [
    'ShapleyValue',
    'ShapleyAnalyzer',
    'compare_algorithms',
    'CloudCostSharingSystem',
    'CloudCostModel',
    'Customer',
    'RideshareCostSharingSystem',
    'RideshareCostModel',
    'Rider',
    'Location',
]
