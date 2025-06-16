"""
MCP Time Precision Server implementation.
"""

import json
import logging
import platform
import socket
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from .tools import (
    get_precise_time,
    get_epoch_micros,
    get_instance_info,
    convert_time_precision,
)

logger = logging.getLogger(__name__)


class TimePrecisionServer:
    """High-precision time MCP server."""
    
    def __init__(self, instance_id: str = "Default-001"):
        """Initialize the time precision server.
        
        Args:
            instance_id: Unique identifier for this instance
        """
        self.instance_id = instance_id
        self.start_time = time.time()
        self.server = Server(
            name="time-precision",
            version="0.1.0"
        )
        
        # Store instance context
        self.context = {
            "instance_id": instance_id,
            "start_time": self.start_time,
            "hostname": socket.gethostname(),
            "platform": platform.system(),
        }
        
        self._setup_handlers()
        logger.info(f"Time Precision Server initialized with instance ID: {instance_id}")
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="get_precise_time",
                    description="Get current time with microsecond precision",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "IANA timezone name (e.g., 'America/New_York')"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_epoch_micros",
                    description="Get current Unix epoch time in microseconds",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_instance_info",
                    description="Get information about this MCP instance",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="convert_time_precision",
                    description="Convert between different time precision formats",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "time": {
                                "type": ["string", "number"],
                                "description": "Time to convert (ISO string or epoch value)"
                            },
                            "input_format": {
                                "type": "string",
                                "enum": ["iso", "epoch_seconds", "epoch_millis", "epoch_micros"],
                                "description": "Format of the input time"
                            },
                            "output_format": {
                                "type": "string",
                                "enum": ["iso", "epoch_seconds", "epoch_millis", "epoch_micros"],
                                "description": "Desired output format"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone for ISO format (optional)"
                            }
                        },
                        "required": ["time", "input_format", "output_format"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> List[types.TextContent]:
            """Handle tool execution."""
            
            if arguments is None:
                arguments = {}
            
            # Add instance context to all calls
            arguments["_context"] = self.context
            
            try:
                if name == "get_precise_time":
                    result = await get_precise_time(**arguments)
                elif name == "get_epoch_micros":
                    result = await get_epoch_micros(**arguments)
                elif name == "get_instance_info":
                    result = await get_instance_info(**arguments)
                elif name == "convert_time_precision":
                    result = await convert_time_precision(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "tool": name,
                        "instance_id": self.instance_id
                    })
                )]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info(f"Time Precision Server running (Instance: {self.instance_id})")
            
            initialization_options = InitializationOptions(
                server_name="time-precision",
                server_version="0.1.0",
                capabilities=self.server.get_capabilities()
            )
            
            await self.server.run(
                read_stream,
                write_stream,
                initialization_options
            )
