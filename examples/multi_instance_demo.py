#!/usr/bin/env python3
"""
Demo of multi-instance coordination using microsecond precision.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any


# Simulated MCP client calls
async def call_tool(tool_name: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Simulate calling an MCP tool."""
    # In real usage, this would be the actual MCP client call
    # For demo, we'll simulate the responses
    
    if tool_name == "get_precise_time":
        import time
        now = time.time()
        dt = datetime.fromtimestamp(now)
        return {
            "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "timezone": "America/New_York",
            "instance_id": args.get("instance_id", "Demo-001")
        }
    
    elif tool_name == "get_epoch_micros":
        import time
        return {
            "epoch_micros": int(time.time() * 1_000_000),
            "instance_id": args.get("instance_id", "Demo-001")
        }


class MemoryBreadcrumb:
    """Represents a timestamped operation in the knowledge graph."""
    
    def __init__(self, instance_id: str):
        self.instance_id = instance_id
    
    async def add_breadcrumb(self, operation: str, status: str, details: str) -> str:
        """Add a breadcrumb with microsecond precision."""
        # Get precise timestamp
        result = await call_tool("get_precise_time", {"instance_id": self.instance_id})
        timestamp = result["timestamp"]
        
        # Format breadcrumb
        breadcrumb = f"[{timestamp}][{self.instance_id}][{operation}][{status}][{details}]"
        return breadcrumb
    
    async def add_breadcrumb_with_lock(self, operation: str) -> Dict[str, Any]:
        """Add a breadcrumb for a locked operation."""
        # Get epoch microseconds for unique operation ID
        result = await call_tool("get_epoch_micros", {"instance_id": self.instance_id})
        epoch_micros = result["epoch_micros"]
        
        # Create operation lock
        operation_id = f"{epoch_micros}-{self.instance_id}"
        lock_breadcrumb = await self.add_breadcrumb(
            operation, "LOCKED", f"Operation ID: {operation_id}"
        )
        
        return {
            "operation_id": operation_id,
            "lock_breadcrumb": lock_breadcrumb,
            "epoch_micros": epoch_micros
        }


async def simulate_multi_instance():
    """Simulate multiple Claude instances working simultaneously."""
    
    # Create three instances (MAGI)
    melchior = MemoryBreadcrumb("Melchior-001")
    balthasar = MemoryBreadcrumb("Balthasar-001")
    caspar = MemoryBreadcrumb("Caspar-001")
    
    print("=== Multi-Instance Coordination Demo ===")
    print("\nSimulating three Claude instances working on CORTEX...\n")
    
    # Simulate concurrent operations
    tasks = [
        melchior.add_breadcrumb("REVIT_SCAN", "STARTED", "Processing point cloud data"),
        balthasar.add_breadcrumb("LLM_INFERENCE", "STARTED", "Loading Llama 3.2 model"),
        caspar.add_breadcrumb("CODE_GEN", "STARTED", "Generating n8n custom node")
    ]
    
    breadcrumbs = await asyncio.gather(*tasks)
    
    print("Concurrent operations:")
    for bc in breadcrumbs:
        print(bc)
    
    print("\n--- Demonstrating Operation Locks ---\n")
    
    # Simulate locked operations
    docker_lock = await melchior.add_breadcrumb_with_lock("DOCKER_COMPOSE_UP")
    print(f"Melchior locked operation: {docker_lock['operation_id']}")
    print(docker_lock['lock_breadcrumb'])
    
    # Simulate completion
    await asyncio.sleep(0.1)  # Simulate work
    completion = await melchior.add_breadcrumb(
        "DOCKER_COMPOSE_UP", "COMPLETED", 
        f"Operation ID: {docker_lock['operation_id']}, All services running"
    )
    print(f"\nOperation completed:")
    print(completion)
    
    print("\n--- Collision Detection Demo ---\n")
    
    # Rapid succession operations
    rapid_tasks = []
    for i in range(3):
        rapid_tasks.extend([
            melchior.add_breadcrumb("RAPID_OP", "TEST", f"Operation {i}"),
            balthasar.add_breadcrumb("RAPID_OP", "TEST", f"Operation {i}"),
            caspar.add_breadcrumb("RAPID_OP", "TEST", f"Operation {i}")
        ])
    
    rapid_breadcrumbs = await asyncio.gather(*rapid_tasks)
    
    print("\nRapid operations (check microsecond differences):")
    for bc in rapid_breadcrumbs[:6]:  # Show first 6
        print(bc)
    
    # Extract and compare timestamps
    timestamps = [bc.split("]")[0][1:] for bc in rapid_breadcrumbs]
    unique_timestamps = set(timestamps)
    
    print(f"\nTotal operations: {len(rapid_breadcrumbs)}")
    print(f"Unique timestamps: {len(unique_timestamps)}")
    print(f"Collision rate: {(1 - len(unique_timestamps)/len(rapid_breadcrumbs))*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(simulate_multi_instance())
