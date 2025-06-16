"""
Tests for time precision tools.
"""

import asyncio
import time
import pytest
from datetime import datetime

from mcp_time_precision.tools import (
    get_precise_time,
    get_epoch_micros,
    get_instance_info,
    convert_time_precision,
)


@pytest.mark.asyncio
class TestTimePrecisionTools:
    """Test time precision tools."""
    
    async def test_get_precise_time(self):
        """Test getting precise time with microseconds."""
        result = await get_precise_time()
        
        assert "timestamp" in result
        assert "timezone" in result
        assert "instance_id" in result
        
        # Check microsecond precision (6 decimal places)
        timestamp = result["timestamp"]
        microseconds = timestamp.split(".")[-1]
        assert len(microseconds) == 6
    
    async def test_get_precise_time_with_timezone(self):
        """Test getting precise time with specific timezone."""
        result = await get_precise_time(timezone="America/New_York")
        
        assert result["timezone"] == "America/New_York"
        assert "." in result["timestamp"]  # Has microseconds
    
    async def test_get_epoch_micros(self):
        """Test getting epoch microseconds."""
        before = int(time.time() * 1_000_000)
        result = await get_epoch_micros()
        after = int(time.time() * 1_000_000)
        
        assert "epoch_micros" in result
        assert "instance_id" in result
        
        # Check value is in expected range
        epoch_micros = result["epoch_micros"]
        assert before <= epoch_micros <= after
        assert epoch_micros > 1_700_000_000_000_000  # After year 2023
    
    async def test_get_instance_info(self):
        """Test getting instance information."""
        context = {
            "instance_id": "Test-001",
            "start_time": time.time() - 100,  # Started 100 seconds ago
            "hostname": "test-host",
            "platform": "TestOS"
        }
        
        result = await get_instance_info(_context=context)
        
        assert result["instance_id"] == "Test-001"
        assert "start_time" in result
        assert result["uptime_seconds"] >= 100
        assert result["system_info"]["hostname"] == "test-host"
        assert result["system_info"]["platform"] == "TestOS"
    
    async def test_convert_time_precision_iso_to_micros(self):
        """Test converting ISO time to epoch microseconds."""
        iso_time = "2025-06-16T12:00:00.123456"
        
        result = await convert_time_precision(
            time_value=iso_time,
            input_format="iso",
            output_format="epoch_micros"
        )
        
        assert result["input"]["value"] == iso_time
        assert result["input"]["format"] == "iso"
        assert result["output"]["format"] == "epoch_micros"
        assert isinstance(result["output"]["value"], int)
    
    async def test_convert_time_precision_micros_to_iso(self):
        """Test converting epoch microseconds to ISO time."""
        epoch_micros = 1718550000123456  # Some timestamp
        
        result = await convert_time_precision(
            time_value=epoch_micros,
            input_format="epoch_micros",
            output_format="iso",
            timezone="UTC"
        )
        
        assert result["output"]["format"] == "iso"
        output = result["output"]["value"]
        assert isinstance(output, str)
        assert "." in output  # Has microseconds
        assert len(output.split(".")[-1]) == 6  # 6 decimal places
    
    async def test_precision_comparison(self):
        """Test that microsecond precision actually works."""
        # Take multiple timestamps in quick succession
        timestamps = []
        for _ in range(10):
            result = await get_epoch_micros()
            timestamps.append(result["epoch_micros"])
            await asyncio.sleep(0.0001)  # 100 microseconds
        
        # All timestamps should be unique
        assert len(set(timestamps)) == len(timestamps)
        
        # Check they're in ascending order
        assert timestamps == sorted(timestamps)
