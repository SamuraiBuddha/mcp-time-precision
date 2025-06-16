"""
MCP Time Precision Server

High-precision time server with microsecond accuracy for multi-instance coordination.
"""

from .server import TimePrecisionServer
from .tools import (
    get_precise_time,
    get_epoch_micros,
    get_instance_info,
    convert_time_precision,
)

__version__ = "0.1.0"
__all__ = [
    "TimePrecisionServer",
    "get_precise_time",
    "get_epoch_micros",
    "get_instance_info",
    "convert_time_precision",
]
