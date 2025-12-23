"""Dress size calculation from body measurements."""

# Standard US Bridal Sizing Chart
# (size, bust, waist, hips) - all in inches
SIZE_CHART: list[tuple[int, float, float, float]] = [
    (0, 32.5, 24.5, 35.5),
    (2, 33.5, 25.5, 36.5),
    (4, 34.5, 26.5, 37.5),
    (6, 35.5, 27.5, 38.5),
    (8, 36.5, 28.5, 39.5),
    (10, 37.5, 29.5, 40.5),
    (12, 39.0, 31.0, 42.0),
    (14, 41.0, 33.0, 44.0),
    (16, 43.0, 35.0, 46.0),
    (18, 45.0, 37.0, 48.0),
    (20, 47.0, 39.0, 50.0),
    (22, 49.0, 41.0, 52.0),
    (24, 51.0, 43.0, 54.0),
]


def calculate_dress_size(bust: float, waist: float, hips: float) -> int:
    """
    Calculate US bridal dress size from measurements (in inches).

    Bridal sizing is conservative - we go with the LARGEST measurement
    to ensure the dress will fit and can be altered down.

    Args:
        bust: Bust circumference in inches
        waist: Waist circumference in inches
        hips: Hip circumference in inches

    Returns:
        US bridal dress size (0, 2, 4, ..., 24)
    """
    # Find size for each measurement
    bust_size = _find_size_for_measurement(bust, measurement_index=1)
    waist_size = _find_size_for_measurement(waist, measurement_index=2)
    hip_size = _find_size_for_measurement(hips, measurement_index=3)

    # Conservative sizing: use the largest
    return max(bust_size, waist_size, hip_size)


def _find_size_for_measurement(value: float, measurement_index: int) -> int:
    """Find the size where the measurement fits."""
    for row in SIZE_CHART:
        if value <= row[measurement_index]:
            return row[0]
    # If larger than chart, return largest size
    return SIZE_CHART[-1][0]


def get_size_range(primary_size: int) -> str:
    """
    Get a size range string accounting for brand variations.

    Different bridal brands size slightly differently, so we provide
    a range to set realistic expectations.

    Args:
        primary_size: The calculated primary size

    Returns:
        Size range string like "6-10"
    """
    # Sizes can vary +/- 1 size between brands
    min_size = max(0, primary_size - 2)
    max_size = min(24, primary_size + 2)
    return f"{min_size}-{max_size}"


def get_measurement_chart() -> list[dict[str, float | int]]:
    """Get the full sizing chart for reference."""
    return [
        {"size": size, "bust": bust, "waist": waist, "hips": hips}
        for size, bust, waist, hips in SIZE_CHART
    ]
