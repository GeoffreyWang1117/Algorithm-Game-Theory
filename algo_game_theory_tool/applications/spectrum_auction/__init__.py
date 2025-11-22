"""
Spectrum Auction System

A comprehensive implementation of combinatorial spectrum auctions including:
- Winner Determination Problem (WDP) solvers
- VCG (Vickrey-Clarke-Groves) pricing mechanism
- Real-world FCC auction scenarios
"""

from .wdp_solver import Bid, Allocation, WDPSolver, compare_algorithms
from .vcg_pricing import VCGPricingMechanism, VCGPayment, VCGOutcome, VCGVariants

__version__ = '1.0.0'

__all__ = [
    'Bid',
    'Allocation',
    'WDPSolver',
    'compare_algorithms',
    'VCGPricingMechanism',
    'VCGPayment',
    'VCGOutcome',
    'VCGVariants',
]
