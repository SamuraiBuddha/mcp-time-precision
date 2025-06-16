"""
Time precision tools implementation.
"""

import time
import platform
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

import pytz
from dateutil import parser as date_parser


async def get_precise_time(
    timezone: Optional[str] = None,
    _context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get current time with microsecond precision.
    
    Args:
        timezone: IANA timezone name (optional)
        _context: Instance context (injected by server)
    
    Returns:
        Dictionary with timestamp, timezone, and instance_id
    """
    # Get current time with microsecond precision
    now_float = time.time()
    
    # Convert to datetime
    dt = datetime.fromtimestamp(now_float, tz=timezone.utc)
    
    # Apply timezone if specified
    if timezone:
        try:
            tz = pytz.timezone(timezone)
            dt = dt.astimezone(tz)
            tz_name = timezone
        except pytz.UnknownTimeZoneError:
            # Fall back to system timezone
            dt = dt.astimezone()
            tz_name = dt.tzinfo.tzname(dt)
    else:
        # Use system timezone
        dt = dt.astimezone()
        tz_name = dt.tzinfo.tzname(dt)
    
    # Format with microseconds
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    return {
        "timestamp": timestamp,
        "timezone": tz_name,
        "instance_id": _context.get("instance_id", "Unknown") if _context else "Unknown"
    }


async def get_epoch_micros(
    _context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get current Unix epoch time in microseconds.
    
    Args:
        _context: Instance context (injected by server)
    
    Returns:
        Dictionary with epoch microseconds and instance_id
    """
    # Get epoch time in microseconds
    epoch_micros = int(time.time() * 1_000_000)
    
    return {
        "epoch_micros": epoch_micros,
        "instance_id": _context.get("instance_id", "Unknown") if _context else "Unknown"
    }


async def get_instance_info(
    _context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get information about this MCP instance.
    
    Args:
        _context: Instance context (injected by server)
    
    Returns:
        Dictionary with instance information
    """
    if not _context:
        return {"error": "No context available"}
    
    current_time = time.time()
    start_time = _context.get("start_time", current_time)
    uptime_seconds = current_time - start_time
    
    # Format start time with microseconds
    start_dt = datetime.fromtimestamp(start_time, tz=timezone.utc)
    start_timestamp = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    return {
        "instance_id": _context.get("instance_id", "Unknown"),
        "start_time": start_timestamp,
        "uptime_seconds": round(uptime_seconds, 6),
        "system_info": {
            "hostname": _context.get("hostname", "Unknown"),
            "platform": _context.get("platform", platform.system())
        }
    }


async def convert_time_precision(
    time_value: Union[str, int, float],
    input_format: str,
    output_format: str,
    timezone: Optional[str] = None,
    _context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert between different time precision formats.
    
    Args:
        time_value: Time to convert
        input_format: Format of input (iso, epoch_seconds, epoch_millis, epoch_micros)
        output_format: Desired output format
        timezone: Timezone for ISO conversions (optional)
        _context: Instance context (injected by server)
    
    Returns:
        Dictionary with converted time and metadata
    """
    
    # Convert input to epoch seconds (float)
    if input_format == "iso":
        dt = date_parser.parse(str(time_value))
        epoch_seconds = dt.timestamp()
    elif input_format == "epoch_seconds":
        epoch_seconds = float(time_value)
    elif input_format == "epoch_millis":
        epoch_seconds = float(time_value) / 1000.0
    elif input_format == "epoch_micros":
        epoch_seconds = float(time_value) / 1_000_000.0
    else:
        raise ValueError(f"Unknown input format: {input_format}")
    
    # Convert to desired output format
    if output_format == "iso":
        dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                dt = dt.astimezone(tz)
            except pytz.UnknownTimeZoneError:
                dt = dt.astimezone()
        else:
            dt = dt.astimezone()
        
        output = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    elif output_format == "epoch_seconds":
        output = epoch_seconds
    elif output_format == "epoch_millis":
        output = int(epoch_seconds * 1000)
    elif output_format == "epoch_micros":
        output = int(epoch_seconds * 1_000_000)
    else:
        raise ValueError(f"Unknown output format: {output_format}")
    
    return {
        "input": {
            "value": time_value,
            "format": input_format
        },
        "output": {
            "value": output,
            "format": output_format
        },
        "instance_id": _context.get("instance_id", "Unknown") if _context else "Unknown"
    }
