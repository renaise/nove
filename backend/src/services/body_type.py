"""Body type classification from measurements."""

from enum import Enum


class BodyType(str, Enum):
    """Body type classifications for dress recommendations."""

    HOURGLASS = "hourglass"
    PEAR = "pear"
    APPLE = "apple"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"


def classify_body_type(bust: float, waist: float, hips: float) -> BodyType:
    """
    Classify body type based on measurements.

    Classification rules:
    - Hourglass: Bust and hips are similar (within 1"), waist is 9"+ smaller
    - Pear: Hips are 3"+ larger than bust
    - Apple: Waist is close to or larger than hips (within 2")
    - Rectangle: All measurements within 5%, waist difference < 9"
    - Inverted Triangle: Bust is 3"+ larger than hips

    Args:
        bust: Bust circumference in inches
        waist: Waist circumference in inches
        hips: Hip circumference in inches

    Returns:
        BodyType classification
    """
    bust_hip_diff = abs(bust - hips)
    waist_diff = min(bust, hips) - waist

    # Hourglass: balanced bust/hips with defined waist
    if bust_hip_diff <= 1 and waist_diff >= 9:
        return BodyType.HOURGLASS

    # Pear: hips significantly larger than bust
    if hips > bust + 3:
        return BodyType.PEAR

    # Apple: waist similar to or larger than hips
    if waist >= hips - 2:
        return BodyType.APPLE

    # Inverted Triangle: bust significantly larger than hips
    if bust > hips + 3:
        return BodyType.INVERTED_TRIANGLE

    # Rectangle: relatively uniform measurements
    return BodyType.RECTANGLE


def get_body_type_description(body_type: BodyType) -> str:
    """Get a user-friendly description of a body type."""
    descriptions = {
        BodyType.HOURGLASS: (
            "Your bust and hips are balanced with a well-defined waist, "
            "creating a classic hourglass figure."
        ),
        BodyType.PEAR: (
            "Your hips are fuller than your bust, creating a beautiful pear-shaped silhouette."
        ),
        BodyType.APPLE: (
            "You carry weight around your midsection with slimmer hips "
            "and legs, creating an apple shape."
        ),
        BodyType.RECTANGLE: (
            "Your bust, waist, and hips are similar in measurement, "
            "creating a balanced, athletic figure."
        ),
        BodyType.INVERTED_TRIANGLE: (
            "Your shoulders and bust are broader than your hips, "
            "creating an inverted triangle shape."
        ),
    }
    return descriptions[body_type]
