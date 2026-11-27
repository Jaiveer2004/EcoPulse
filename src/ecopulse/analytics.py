def calculate_average(values: list[float]) -> float:
    """Calculate the arithmetic mean of numerical values."""

    if not values:
        raise ValueError("Input values cannot be empty")

    return sum(values) / len(values)
