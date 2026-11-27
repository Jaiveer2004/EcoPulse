
# EcoPulse Engineering Standards

## Python
- Python 3.12 compatibility baseline.
- Modular application architecture.
- Type hints for public functions.
- Meaningful function and variable names.

## Dependencies
- Dependencies declared in pyproject.toml.
- Development dependencies separated.
- Exact dependency versions will be locked for releases.

## Configuration
- Secrets stored in environment variables.
- .env excluded from Git.
- .env.example contains placeholders only.

## Logging
- Python logging module.
- INFO for normal application events.
- WARNING for recoverable issues.
- ERROR for failures.
- Tracebacks recorded for unexpected exceptions.

## Database
- Parameterized SQL queries.
- Explicit transaction boundaries.
- Least-privilege application access.
- Versioned database migrations.

## Testing
- Pytest for automated tests.
- Unit tests for isolated logic.
- Integration tests for infrastructure.
- Regression tests for resolved incidents.

## Code Quality
- Ruff for linting.
- Ruff for formatting.
- Consistent naming and structure.

## Git
- Feature branches.
- Meaningful commit messages.
- No secrets or generated data committed.
