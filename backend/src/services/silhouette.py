"""Silhouette recommendation service based on body type."""

from dataclasses import dataclass
from enum import Enum

from src.services.body_type import BodyType


class Silhouette(str, Enum):
    """Wedding dress silhouette types."""

    BALLGOWN = "ballgown"
    A_LINE = "a-line"
    MERMAID = "mermaid"
    SHEATH = "sheath"
    EMPIRE = "empire"
    FIT_AND_FLARE = "fit-and-flare"
    BOHEMIAN = "bohemian"


@dataclass
class SilhouetteRecommendation:
    """A silhouette recommendation with score and reasoning."""

    silhouette: Silhouette
    score: float  # 0.0 to 1.0
    reason: str


# Recommendation matrix: body_type -> list of (silhouette, base_score, reason)
SILHOUETTE_MATRIX: dict[BodyType, list[tuple[Silhouette, float, str]]] = {
    BodyType.HOURGLASS: [
        (Silhouette.MERMAID, 0.95, "Showcases your natural curves beautifully"),
        (Silhouette.SHEATH, 0.90, "Follows your figure elegantly"),
        (Silhouette.FIT_AND_FLARE, 0.88, "Highlights your defined waist"),
        (Silhouette.A_LINE, 0.82, "Classic and flattering on any figure"),
        (Silhouette.BALLGOWN, 0.75, "Creates a timeless princess look"),
    ],
    BodyType.PEAR: [
        (Silhouette.A_LINE, 0.95, "Skims over hips and balances proportions"),
        (Silhouette.BALLGOWN, 0.92, "Full skirt balances your silhouette"),
        (Silhouette.EMPIRE, 0.85, "Draws attention upward to the bust"),
        (Silhouette.FIT_AND_FLARE, 0.78, "Flare adds volume to balance hips"),
        (Silhouette.BOHEMIAN, 0.75, "Flowy fabric flatters your shape"),
    ],
    BodyType.APPLE: [
        (Silhouette.EMPIRE, 0.95, "Flows over midsection gracefully"),
        (Silhouette.A_LINE, 0.92, "Skims the waist with elegant ease"),
        (Silhouette.BALLGOWN, 0.85, "Cinches above the waist for definition"),
        (Silhouette.BOHEMIAN, 0.80, "Relaxed fit is comfortable and flattering"),
        (Silhouette.SHEATH, 0.65, "Works with the right fabric draping"),
    ],
    BodyType.RECTANGLE: [
        (Silhouette.BALLGOWN, 0.95, "Creates curves with a full skirt"),
        (Silhouette.MERMAID, 0.90, "Adds curves at the hips and bust"),
        (Silhouette.FIT_AND_FLARE, 0.88, "Defines the waist and adds shape"),
        (Silhouette.A_LINE, 0.82, "Classic and universally flattering"),
        (Silhouette.SHEATH, 0.75, "Sleek and modern with the right details"),
    ],
    BodyType.INVERTED_TRIANGLE: [
        (Silhouette.A_LINE, 0.95, "Balances broader shoulders with flared skirt"),
        (Silhouette.BALLGOWN, 0.92, "Full skirt creates visual balance"),
        (Silhouette.FIT_AND_FLARE, 0.85, "Adds volume below to balance shoulders"),
        (Silhouette.BOHEMIAN, 0.78, "Soft, flowy silhouette softens angles"),
        (Silhouette.EMPIRE, 0.72, "Draws focus to the bust and away from shoulders"),
    ],
}


def get_silhouette_recommendations(
    body_type: BodyType,
    *,
    limit: int = 5,
) -> list[SilhouetteRecommendation]:
    """
    Get silhouette recommendations for a body type.

    Args:
        body_type: The classified body type
        limit: Maximum number of recommendations to return

    Returns:
        List of SilhouetteRecommendation sorted by score descending
    """
    recommendations = SILHOUETTE_MATRIX.get(body_type, [])

    return [
        SilhouetteRecommendation(
            silhouette=silhouette,
            score=score,
            reason=reason,
        )
        for silhouette, score, reason in recommendations[:limit]
    ]


def get_all_silhouettes() -> list[dict[str, str]]:
    """Get information about all silhouette types."""
    descriptions = {
        Silhouette.BALLGOWN: "Full, voluminous skirt with fitted bodice - classic princess style",
        Silhouette.A_LINE: "Fitted at hips and gradually flares out - universally flattering",
        Silhouette.MERMAID: "Fitted through hips and flares at knee - dramatic and glamorous",
        Silhouette.SHEATH: "Slim, form-fitting throughout - sleek and sophisticated",
        Silhouette.EMPIRE: "High waistline just below bust, flowing skirt - romantic and elongating",
        Silhouette.FIT_AND_FLARE: "Fitted bodice with skirt that flares at waist - playful and feminine",
        Silhouette.BOHEMIAN: "Relaxed, flowy fit with romantic details - free-spirited and effortless",
    }

    return [{"type": s.value, "description": descriptions[s]} for s in Silhouette]
