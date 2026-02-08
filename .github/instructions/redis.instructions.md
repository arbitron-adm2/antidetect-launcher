---
name: redis-rules
applyTo: "**/*redis*"
---

# Redis Rules

## Connection

- Use connection pooling
- Async client only (redis-py async)
- Connection timeout required
- Reconnect on failure

## Data Structure

- Key format: `{prefix}:{exchange}:{market}:{symbol}`
- TTL on all keys (prevent memory leaks)
- HSET for orderbook data
- Pipeline for batch operations

## Performance

- Use pipelines for batch writes
- Avoid blocking commands (KEYS, SMEMBERS on large sets)
- Monitor memory usage
- Configure maxmemory-policy (allkeys-lru)

## Configuration

- Host/port via ENV override
- Password via ENV (not in config files)
- Connection pool size matches workload

## Docker

- Use redis:7-alpine image
- Enable AOF persistence for durability
- Set maxmemory limit
- Health check via redis-cli ping
