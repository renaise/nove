"""
Silhouette Recommendation Engine
Maps body proportions to optimal dress silhouettes
"""

from typing import List
from ..models import BodyProportions, SilhouetteRecommendation, SilhouetteType


class SilhouetteRecommendationEngine:
    """
    Recommends dress silhouettes based on body proportions

    Uses stylist knowledge to match body shapes with flattering silhouettes
    """

    # Silhouette matching rules based on professional bridal styling
    SILHOUETTE_RULES = {
        "hourglass": {
            SilhouetteType.MERMAID: {
                "score": 0.95,
                "reasoning": "Mermaid silhouettes beautifully showcase your balanced proportions and defined waist, hugging your curves before flaring at the knees.",
                "tips": ["Emphasize your natural waist", "Consider structured bodices", "Look for strategic seaming"]
            },
            SilhouetteType.A_LINE: {
                "score": 0.90,
                "reasoning": "A-line gowns elegantly highlight your waist while providing graceful movement from the hips.",
                "tips": ["Try fitted bodices", "Experiment with different necklines", "Consider embellished waistlines"]
            },
            SilhouetteType.TRUMPET: {
                "score": 0.85,
                "reasoning": "Trumpet silhouettes accentuate your curves while offering drama and movement below the knee.",
                "tips": ["Look for mid-thigh flare points", "Consider lace overlays", "Try sweetheart necklines"]
            }
        },
        "pear": {
            SilhouetteType.A_LINE: {
                "score": 0.95,
                "reasoning": "A-line silhouettes are perfect for your shape, balancing your proportions by drawing attention to your shoulders and gradually flowing from the waist.",
                "tips": ["Emphasize your shoulders with statement sleeves", "Look for fitted bodices", "Try ball skirts for drama"]
            },
            SilhouetteType.BALLGOWN: {
                "score": 0.90,
                "reasoning": "Ballgown styles create beautiful balance by adding volume from the waist, creating an elegant, princess-like silhouette.",
                "tips": ["Consider off-shoulder or boat necklines", "Look for embellished bodices", "Try fuller skirts"]
            },
            SilhouetteType.EMPIRE_WAIST: {
                "score": 0.85,
                "reasoning": "Empire waistlines draw the eye upward and flow gracefully over your hips, creating elongating vertical lines.",
                "tips": ["Try V-necklines to elongate", "Consider flowing fabrics", "Look for delicate waist details"]
            }
        },
        "apple": {
            SilhouetteType.EMPIRE_WAIST: {
                "score": 0.95,
                "reasoning": "Empire waists are ideal for your shape, defining just under the bust and flowing gracefully to create a flattering, elongated silhouette.",
                "tips": ["Emphasize your décolletage", "Look for flowing fabrics", "Try vertical details"]
            },
            SilhouetteType.A_LINE: {
                "score": 0.90,
                "reasoning": "A-line gowns provide structure through the bodice while flowing comfortably from the natural or empire waistline.",
                "tips": ["Try V or sweetheart necklines", "Look for structured bodices", "Consider ruching details"]
            },
            SilhouetteType.SHEATH: {
                "score": 0.80,
                "reasoning": "Sheath dresses with strategic draping can create beautiful vertical lines that elongate your frame.",
                "tips": ["Look for draping details", "Try wrap-style bodices", "Consider darker colors or vertical seaming"]
            }
        },
        "rectangle": {
            SilhouetteType.BALLGOWN: {
                "score": 0.90,
                "reasoning": "Ballgowns create dramatic curves by adding volume at the hips, defining your waist through contrast.",
                "tips": ["Look for fitted bodices with full skirts", "Try embellished waistlines", "Consider peplum details"]
            },
            SilhouetteType.MERMAID: {
                "score": 0.85,
                "reasoning": "Mermaid silhouettes with strategic seaming can create the illusion of curves while maintaining elegance.",
                "tips": ["Look for ruching or draping", "Try sweetheart necklines", "Consider beaded or embellished bodices"]
            },
            SilhouetteType.A_LINE: {
                "score": 0.90,
                "reasoning": "A-line gowns with defined waistlines help create shapely curves while maintaining a classic, timeless look.",
                "tips": ["Emphasize your waist with belts or sashes", "Try textured bodices", "Look for strategic embellishments"]
            }
        },
        "inverted_triangle": {
            SilhouetteType.A_LINE: {
                "score": 0.95,
                "reasoning": "A-line silhouettes perfectly balance your proportions by adding volume at the hips to match your shoulders.",
                "tips": ["Minimize shoulder details", "Look for full, flowing skirts", "Try simpler necklines"]
            },
            SilhouetteType.BALLGOWN: {
                "score": 0.90,
                "reasoning": "Ballgowns create beautiful proportion by adding dramatic volume below the waist to balance your shoulders.",
                "tips": ["Avoid heavily embellished shoulders", "Try fuller skirts", "Consider clean, simple necklines"]
            },
            SilhouetteType.TRUMPET: {
                "score": 0.85,
                "reasoning": "Trumpet styles add volume below the hips, creating balance while maintaining a sleek, modern silhouette.",
                "tips": ["Look for simpler bodices", "Try low flare points", "Consider flowing fabrics"]
            }
        }
    }

    def recommend_silhouettes(
        self,
        body_proportions: BodyProportions,
        max_recommendations: int = 3
    ) -> List[SilhouetteRecommendation]:
        """
        Generate silhouette recommendations based on body proportions

        Args:
            body_proportions: Analyzed body proportions
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of SilhouetteRecommendation sorted by match score
        """
        body_shape = body_proportions.body_shape
        rules = self.SILHOUETTE_RULES.get(body_shape, {})

        if not rules:
            # Fallback for unknown body shapes
            return self._get_default_recommendations(max_recommendations)

        # Create recommendations from rules
        recommendations = []
        for silhouette_type, details in rules.items():
            # Adjust score based on confidence
            adjusted_score = details["score"] * body_proportions.confidence

            recommendations.append(
                SilhouetteRecommendation(
                    silhouette_type=silhouette_type,
                    match_score=adjusted_score,
                    reasoning=details["reasoning"],
                    styling_tips=details["tips"]
                )
            )

        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:max_recommendations]

    def _get_default_recommendations(self, count: int = 3) -> List[SilhouetteRecommendation]:
        """Fallback recommendations for unknown body shapes"""
        defaults = [
            SilhouetteRecommendation(
                silhouette_type=SilhouetteType.A_LINE,
                match_score=0.85,
                reasoning="A-line silhouettes are universally flattering, creating a timeless and elegant bridal look.",
                styling_tips=["Try different necklines", "Consider various embellishments", "Experiment with different fabrics"]
            ),
            SilhouetteRecommendation(
                silhouette_type=SilhouetteType.EMPIRE_WAIST,
                match_score=0.80,
                reasoning="Empire waistlines offer a romantic, flowing silhouette that flatters many body types.",
                styling_tips=["Look for delicate details", "Try flowing fabrics", "Consider lace overlays"]
            ),
            SilhouetteRecommendation(
                silhouette_type=SilhouetteType.SHEATH,
                match_score=0.75,
                reasoning="Sheath dresses offer a sleek, modern aesthetic with comfortable movement.",
                styling_tips=["Keep accessories minimal", "Try interesting necklines", "Look for quality fabrics"]
            )
        ]
        return defaults[:count]

    def generate_stylist_feedback(
        self,
        body_proportions: BodyProportions,
        recommendations: List[SilhouetteRecommendation]
    ) -> str:
        """
        Generate human-readable feedback for the bride

        Returns a warm, professional message explaining the analysis
        """
        body_shape_descriptions = {
            "hourglass": "beautifully balanced proportions with a defined waist",
            "pear": "graceful proportions with elegant curves",
            "apple": "a sophisticated frame with beautiful shoulders",
            "rectangle": "a statuesque figure with clean lines",
            "inverted_triangle": "strong, confident proportions with elegant shoulders"
        }

        body_desc = body_shape_descriptions.get(
            body_proportions.body_shape,
            "unique and beautiful proportions"
        )

        top_silhouette = recommendations[0].silhouette_type.value.replace("_", "-").title()

        feedback = f"""We've analyzed your silhouette and you have {body_desc}.

Your frame is beautifully suited for **{top_silhouette}** silhouettes, which will {recommendations[0].reasoning.split(',')[0].lower()}.

We've curated our boutique collection to show you styles that will make you feel absolutely stunning on your special day."""

        return feedback
