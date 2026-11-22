
# INC-001: PostgreSQL Health Check Failure

## Incident
PostgreSQL container started but reported an unhealthy status.

## Symptoms
Docker Compose reported PostgreSQL as unhealthy.

## Root Cause
The configured health check attempted to connect to
a nonexistent database named ecopulse_health_typo.

## Resolution
Updated the health check to use the configured
POSTGRES_DB environment variable.

## Prevention
Use configuration-driven health checks instead of
hardcoded database names.

## Verification
Successfully executed SELECT 1 against the
configured PostgreSQL database.

## Status
Resolved.
