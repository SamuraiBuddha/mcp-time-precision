# Breadcrumb Pattern for Multi-Instance Memory

## Standard Breadcrumb Format

```
[TIMESTAMP][INSTANCE][PROJECT][OPERATION][STATUS][DETAILS]
```

### Examples:

```
[2025-06-16T11:30:45.123456][Melchior-001][CORTEX][DOCKER_START][SUCCESS][Started n8n container]
[2025-06-16T11:30:45.234567][Balthasar-001][CORTEX][MODEL_LOAD][PENDING][Loading Llama-3.2-8B]
[2025-06-16T11:30:45.345678][Caspar-001][CORTEX][CODE_GEN][FAILED][Syntax error in generated code]
```

## Operation Locking Pattern

For operations that must be exclusive:

### Lock Acquisition:
```
[2025-06-16T11:30:45.123456][Melchior-001][CORTEX][DATABASE_MIGRATION][LOCKED][Est. duration: 5 minutes]
```

### Lock Release:
```
[2025-06-16T11:30:50.789012][Melchior-001][CORTEX][DATABASE_MIGRATION][COMPLETED][Migration successful, 1247 records updated]
```

## Collision Resolution

When multiple instances attempt the same operation:

1. **Check for existing locks:**
   ```python
   # Search for: [*][*][PROJECT][OPERATION][LOCKED][*]
   existing_locks = search_breadcrumbs(project="CORTEX", operation="DATABASE_MIGRATION", status="LOCKED")
   ```

2. **Use epoch microseconds for ordering:**
   ```
   1718553045123456-Melchior-001  # First
   1718553045123457-Balthasar-001 # Second (defers)
   ```

3. **Implement backoff:**
   ```
   [2025-06-16T11:30:45.123457][Balthasar-001][CORTEX][DATABASE_MIGRATION][DEFERRED][Waiting for Melchior-001 lock]
   ```

## Performance Tracking

Use microsecond precision for performance analysis:

```
[2025-06-16T11:30:45.100000][Caspar-001][AGENTIC_REVIT][SCAN_PROCESS][STARTED][Processing 1.2GB point cloud]
[2025-06-16T11:30:47.250000][Caspar-001][AGENTIC_REVIT][SCAN_PROCESS][MILESTONE][50% complete, 425k points processed]
[2025-06-16T11:30:49.500000][Caspar-001][AGENTIC_REVIT][SCAN_PROCESS][COMPLETED][2.4 seconds, 850k points, 354k points/sec]
```

## Distributed Consensus

For operations requiring agreement:

```
[2025-06-16T11:30:45.100000][Melchior-001][CORTEX][CONSENSUS_PROPOSE][INITIATED][Proposal: Scale n8n workers to 5]
[2025-06-16T11:30:45.150000][Balthasar-001][CORTEX][CONSENSUS_VOTE][APPROVED][Proposal accepted]
[2025-06-16T11:30:45.200000][Caspar-001][CORTEX][CONSENSUS_VOTE][APPROVED][Proposal accepted]
[2025-06-16T11:30:45.250000][Melchior-001][CORTEX][CONSENSUS_EXECUTE][SUCCESS][Scaling initiated, 2/3 votes]
```

## Integration with Memory(Ref)

When adding to the knowledge graph:

```python
# Get precise timestamp
time_result = await mcp.call_tool("get_precise_time")
timestamp = time_result["timestamp"]
instance = time_result["instance_id"]

# Create breadcrumb
breadcrumb = f"[{timestamp}][{instance}][{project}][{operation}][{status}][{details}]"

# Add to Session_Breadcrumbs
await memory_ref.add_observation(
    entity_name="Session_Breadcrumbs",
    observation=breadcrumb
)
```

## Best Practices

1. **Always include microseconds** - Critical for multi-instance coordination
2. **Use consistent status values** - PENDING, STARTED, SUCCESS, FAILED, LOCKED, COMPLETED
3. **Keep details concise** - Breadcrumbs are for tracking, not full logs
4. **Include operation IDs** - For tracking related operations
5. **Clean up old locks** - Implement timeout mechanism for abandoned locks
