"""Tests for backend services."""

import pytest

from src.services.body_type import BodyType, classify_body_type
from src.services.silhouette import Silhouette, get_silhouette_recommendations
from src.services.sizing import calculate_dress_size, get_size_range


class TestBodyTypeClassification:
    """Tests for body type classification."""

    def test_hourglass_classification(self):
        """Hourglass: balanced bust/hips with defined waist."""
        body_type = classify_body_type(bust=36.0, waist=26.0, hips=36.0)
        assert body_type == BodyType.HOURGLASS

    def test_pear_classification(self):
        """Pear: hips significantly larger than bust."""
        body_type = classify_body_type(bust=34.0, waist=28.0, hips=40.0)
        assert body_type == BodyType.PEAR

    def test_apple_classification(self):
        """Apple: waist similar to or larger than hips."""
        body_type = classify_body_type(bust=38.0, waist=36.0, hips=37.0)
        assert body_type == BodyType.APPLE

    def test_rectangle_classification(self):
        """Rectangle: relatively uniform measurements."""
        body_type = classify_body_type(bust=35.0, waist=32.0, hips=36.0)
        assert body_type == BodyType.RECTANGLE

    def test_inverted_triangle_classification(self):
        """Inverted triangle: bust significantly larger than hips."""
        body_type = classify_body_type(bust=40.0, waist=30.0, hips=35.0)
        assert body_type == BodyType.INVERTED_TRIANGLE


class TestSilhouetteRecommendations:
    """Tests for silhouette recommendations."""

    def test_hourglass_gets_mermaid_first(self):
        """Hourglass body type should get mermaid as top recommendation."""
        recs = get_silhouette_recommendations(BodyType.HOURGLASS)
        assert len(recs) > 0
        assert recs[0].silhouette == Silhouette.MERMAID

    def test_pear_gets_aline_first(self):
        """Pear body type should get a-line as top recommendation."""
        recs = get_silhouette_recommendations(BodyType.PEAR)
        assert len(recs) > 0
        assert recs[0].silhouette == Silhouette.A_LINE

    def test_apple_gets_empire_first(self):
        """Apple body type should get empire as top recommendation."""
        recs = get_silhouette_recommendations(BodyType.APPLE)
        assert len(recs) > 0
        assert recs[0].silhouette == Silhouette.EMPIRE

    def test_recommendations_have_reasons(self):
        """All recommendations should include reasons."""
        for body_type in BodyType:
            recs = get_silhouette_recommendations(body_type)
            for rec in recs:
                assert rec.reason
                assert len(rec.reason) > 10

    def test_limit_parameter(self):
        """Limit parameter should restrict number of recommendations."""
        recs = get_silhouette_recommendations(BodyType.HOURGLASS, limit=2)
        assert len(recs) <= 2


class TestDressSizing:
    """Tests for dress size calculation."""

    def test_size_calculation_small(self):
        """Small measurements should give small size."""
        size = calculate_dress_size(bust=33.0, waist=25.0, hips=36.0)
        assert size == 2

    def test_size_calculation_medium(self):
        """Medium measurements should give medium size."""
        size = calculate_dress_size(bust=36.5, waist=28.5, hips=39.5)
        assert size == 8

    def test_size_calculation_large(self):
        """Larger measurements should give larger size."""
        size = calculate_dress_size(bust=41.0, waist=33.0, hips=44.0)
        assert size == 14

    def test_conservative_sizing(self):
        """Size should be based on largest measurement."""
        # Small bust/waist but larger hips
        size = calculate_dress_size(bust=33.0, waist=25.0, hips=42.0)
        assert size == 12  # Based on hips

    def test_size_range(self):
        """Size range should account for brand variations."""
        range_str = get_size_range(8)
        assert range_str == "6-10"

    def test_size_range_boundaries(self):
        """Size range should respect min/max boundaries."""
        range_str = get_size_range(0)
        assert range_str == "0-2"

        range_str = get_size_range(24)
        assert range_str == "22-24"
