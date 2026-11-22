
# INC-002: Invalid Station Coordinate Rejected

## Incident
An invalid environmental station record was submitted to PostgreSQL.

## Symptoms
The INSERT operation failed with a check constraint violation.

## Root Cause
The supplied latitude was 120, outside the permitted
geographical range of -90 to 90.

## Resolution
Corrected the input data and inserted a valid synthetic station.

## Prevention
- Validate coordinates during ingestion.
- Retain database-level CHECK constraints.
- Monitor rejected records.
- Add regression tests for invalid coordinates.

## Verification
The invalid record was rejected.
A valid synthetic station and its measurement were inserted successfully.

## Status
Resolved.
