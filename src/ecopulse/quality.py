
import math
from datetime import UTC, datetime
from typing import Any


def is_valid_timestamp(value: Any) -> bool:
    """Check that a timestamp is valid and includes timezone information."""
    
    if not isinstance(value, str):
        return False
    
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError:
        return False
    
    
def is_finite_number(value: Any) -> bool:
    """Reject strings, booleans, NaN, and infinity."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
    
def validate_air_record(record: dict[str, Any]) -> list[str]:
    errors = []
    
    required_fields = [
        "sensor_id",
        "location_id",
        "parameter",
        "value",
        "unit",
        "observed_at",
        "latitude",
        "longitude",
        "source_type",
        "source_name",
        "ingested_at",
    ]
    
    for field in required_fields:
        if record.get(field) is None:
            errors.append(f"Missing required field: {field}")
            
    if not is_finite_number(record.get("value")):
        errors.append("value must be a finite number")
        
        