
# EcoPulse Data Quality Architecture

## Validation technology

EcoPulse uses Pydantic v2 for normalized record validation.

## Processing flow

Raw source data
    |
    v
Source-specific normalization
    |
    v
Pydantic validation
    |
    +---- Valid records ----> Validated data
    |
    +---- Invalid records --> Quarantine

## Validation responsibilities

### Air quality
- Required fields and types
- Nonnegative measurement values
- Valid geographic coordinates
- Timezone-aware timestamps
- OpenAQ source identification

### Weather
- Required fields and types
- Parameter-specific physical plausibility checks
- Valid geographic coordinates
- Timezone-aware timestamps
- Forecast and valid-time metadata

## Error handling

- Raw files remain unchanged.
- Invalid JSON is recorded separately.
- Pydantic validation errors are preserved.
- Rejected records are quarantined.
- Validation reports contain total, valid, rejected,
  and quality-rate statistics.

## Limitations

These checks establish structural validity and basic
physical plausibility. They do not establish instrument
calibration, regulatory compliance, or scientific accuracy.
