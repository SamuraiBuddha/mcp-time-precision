# MCP Time Precision Server

🕐 A high-precision time MCP (Model Context Protocol) server providing microsecond-accurate timestamps for multi-instance Claude coordination.

## Features

- **Microsecond Precision**: Timestamps accurate to 6 decimal places (YYYY-MM-DDTHH:MM:SS.ffffff)
- **Epoch Microseconds**: Unix epoch time in microseconds for precise ordering
- **Instance Identification**: Unique instance IDs for multi-Claude deployments
- **Collision Detection**: Built-in support for detecting simultaneous operations
- **Timezone Support**: Full IANA timezone database support
- **MAGI Integration**: Pre-configured instance names for the Three Wise Men setup

## Why Microsecond Precision?

When running multiple Claude Desktop instances (e.g., on Melchior, Balthasar, and Caspar machines) that share a common Memory(Ref) knowledge graph:

- **Second precision**: High collision probability with 3+ instances
- **Millisecond precision**: 1/1000 collision probability per second
- **Microsecond precision**: 1/1,000,000 collision probability per second

## Installation

### Via pip
```bash
pip install mcp-time-precision
```

### Via uv (recommended)
```bash
uvx mcp-time-precision
```

### From source
```bash
git clone https://github.com/SamuraiBuddha/mcp-time-precision.git
cd mcp-time-precision
pip install -e .
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "time-precision": {
      "command": "python",
      "args": ["-m", "mcp_time_precision", "--instance-id", "Melchior-001"]
    }
  }
}
```

### Multi-Instance Setup (MAGI)

For the Three Wise Men configuration:

**Melchior (CAD/3D Machine):**
```json
{
  "mcpServers": {
    "time-precision": {
      "command": "python",
      "args": ["-m", "mcp_time_precision", "--instance-id", "Melchior-001"]
    }
  }
}
```

**Balthasar (AI/LLM Machine):**
```json
{
  "mcpServers": {
    "time-precision": {
      "command": "python",
      "args": ["-m", "mcp_time_precision", "--instance-id", "Balthasar-001"]
    }
  }
}
```

**Caspar (Code/Data Machine):**
```json
{
  "mcpServers": {
    "time-precision": {
      "command": "python",
      "args": ["-m", "mcp_time_precision", "--instance-id", "Caspar-001"]
    }
  }
}
```

## Available Tools

### `get_precise_time`
Get current time with microsecond precision in ISO format.

**Parameters:**
- `timezone` (optional): IANA timezone name (default: system timezone)

**Returns:**
```json
{
  "timestamp": "2025-06-16T11:30:45.123456",
  "timezone": "America/New_York",
  "instance_id": "Melchior-001"
}
```

### `get_epoch_micros`
Get current Unix epoch time in microseconds.

**Returns:**
```json
{
  "epoch_micros": 1718553045123456,
  "instance_id": "Melchior-001"
}
```

### `get_instance_info`
Get information about this MCP instance.

**Returns:**
```json
{
  "instance_id": "Melchior-001",
  "start_time": "2025-06-16T11:00:00.000000",
  "uptime_seconds": 1845.123456,
  "system_info": {
    "hostname": "melchior-workstation",
    "platform": "Windows-11"
  }
}
```

### `convert_time_precision`
Convert between different time precisions.

**Parameters:**
- `time` (required): Time string or epoch value
- `input_format`: "iso", "epoch_seconds", "epoch_millis", "epoch_micros"
- `output_format`: "iso", "epoch_seconds", "epoch_millis", "epoch_micros"
- `timezone` (optional): For ISO format conversions

## Usage Examples

### Memory Breadcrumb Pattern
```python
# Get microsecond timestamp for breadcrumb
result = await mcp.call_tool("get_precise_time")
timestamp = result["timestamp"]
instance = result["instance_id"]

# Create breadcrumb: [2025-06-16T11:30:45.123456][Melchior-001][OPERATION][STATUS]
breadcrumb = f"[{timestamp}][{instance}][DOCKER_START][SUCCESS][Started n8n container]"
```

### Collision Detection
```python
# Get epoch microseconds for precise ordering
result = await mcp.call_tool("get_epoch_micros")
epoch_micros = result["epoch_micros"]

# Use for distributed consensus or operation ordering
operation_id = f"{epoch_micros}-{result['instance_id']}"
```

## Development

### Running Tests
```bash
pytest tests/
```

### Debug Mode
```bash
python -m mcp_time_precision --debug --instance-id "Test-001"
```

### MCP Inspector
```bash
npx @modelcontextprotocol/inspector python -m mcp_time_precision
```

## Architecture

- Built on MCP SDK for standardized protocol support
- Uses Python's `time.time()` for microsecond precision
- Thread-safe implementation for concurrent access
- Minimal dependencies for reliability

## Contributing

Contributions welcome! Especially interested in:
- Performance optimizations for high-frequency calls
- Additional time manipulation tools
- Integration with distributed systems
- Alternative precision options (nanoseconds?)

## License

MIT License - see LICENSE file

## Acknowledgments

- Inspired by the need for precise multi-instance coordination in CORTEX
- Named after the MAGI supercomputer from Evangelion
- Built for the BIM/AI integration future

---

*"Time is an illusion. Microsecond time, slightly less so."* - With apologies to Douglas Adams