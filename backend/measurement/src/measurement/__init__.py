"""Novia Body Measurement Service - HMR 2.0 + SMPL Anthropometry"""

__version__ = "0.1.0"

from .models import BodyMeasurements, BodyType
from .service import MeasurementService, measure, get_service
from .anthropometry import extract_measurements

__all__ = [
    "BodyMeasurements",
    "BodyType",
    "MeasurementService",
    "measure",
    "get_service",
    "extract_measurements",
]
