"""Body analysis service using SAM-3D-Body + ANNY for 3D mesh extraction and fitting."""

from dataclasses import dataclass

from src.services.body_type import BodyType, classify_body_type
from src.services.silhouette import SilhouetteRecommendation, get_silhouette_recommendations
from src.services.sizing import calculate_dress_size, get_size_range

# Try to import ANNY integration (requires GPU dependencies)
try:
    from src.services.anny_integration import ANNYBodyAnalyzer, FittingResult

    ANNY_AVAILABLE = True
except ImportError:
    ANNY_AVAILABLE = False
    ANNYBodyAnalyzer = None
    FittingResult = None


@dataclass
class BodyMeasurements:
    """Extracted body measurements in inches."""

    bust: float
    waist: float
    hips: float
    height_cm: float | None = None
    weight_kg: float | None = None


@dataclass
class BodyAnalysisResult:
    """Complete body analysis results."""

    measurements: BodyMeasurements
    body_type: BodyType
    estimated_size: int
    size_range: str
    confidence: float
    mesh_url: str | None
    recommendations: list[SilhouetteRecommendation]
    # Raw phenotype data from ANNY
    phenotypes: dict[str, float] | None = None


class BodyAnalyzer:
    """
    Analyzes body proportions from SAM-3D-Body mesh output using ANNY fitting.

    Workflow:
    1. Receive SAM-3D-Body output (PLY mesh URL + keypoints)
    2. Fit ANNY parametric model to the mesh
    3. Extract body measurements from fitted ANNY
    4. Classify body type and recommend silhouettes
    """

    def __init__(self, use_anny: bool = True):
        """
        Initialize the body analyzer.

        Args:
            use_anny: Whether to use ANNY fitting (requires GPU)
        """
        self.use_anny = use_anny and ANNY_AVAILABLE
        self._anny_analyzer = None

    def _get_anny_analyzer(self) -> "ANNYBodyAnalyzer":
        """Lazy load ANNY analyzer."""
        if self._anny_analyzer is None:
            if not ANNY_AVAILABLE:
                raise RuntimeError(
                    "ANNY not available. Install GPU dependencies: "
                    "uv sync --extra gpu"
                )
            self._anny_analyzer = ANNYBodyAnalyzer()
        return self._anny_analyzer

    async def analyze_from_sam3d(
        self,
        ply_url: str,
        keypoints_3d: list[list[float]] | None = None,
        glb_url: str | None = None,
    ) -> BodyAnalysisResult:
        """
        Analyze body from SAM-3D-Body output.

        Args:
            ply_url: URL to PLY mesh from SAM-3D-Body
            keypoints_3d: Optional 3D keypoints from SAM-3D-Body
            glb_url: Optional GLB file URL for visualization

        Returns:
            BodyAnalysisResult with measurements, body type, and recommendations
        """
        if self.use_anny:
            return await self._analyze_with_anny(ply_url, keypoints_3d, glb_url)
        else:
            return await self._analyze_from_keypoints(keypoints_3d, glb_url)

    async def _analyze_with_anny(
        self,
        ply_url: str,
        keypoints_3d: list[list[float]] | None = None,
        glb_url: str | None = None,
    ) -> BodyAnalysisResult:
        """Analyze using ANNY mesh fitting."""
        analyzer = self._get_anny_analyzer()

        # Fit ANNY to SAM-3D mesh
        fitting_result = await analyzer.analyze_from_url(ply_url, keypoints_3d=keypoints_3d)

        # Convert cm to inches for sizing
        bust_inches = fitting_result.measurements.bust_cm / 2.54
        waist_inches = fitting_result.measurements.waist_cm / 2.54
        hips_inches = fitting_result.measurements.hips_cm / 2.54

        measurements = BodyMeasurements(
            bust=bust_inches,
            waist=waist_inches,
            hips=hips_inches,
            height_cm=fitting_result.measurements.height_cm,
            weight_kg=fitting_result.measurements.weight_kg,
        )

        # Classify body type
        body_type = classify_body_type(bust_inches, waist_inches, hips_inches)

        # Calculate dress size
        estimated_size = calculate_dress_size(bust_inches, waist_inches, hips_inches)
        size_range = get_size_range(estimated_size)

        # Get silhouette recommendations
        recommendations = get_silhouette_recommendations(body_type)

        return BodyAnalysisResult(
            measurements=measurements,
            body_type=body_type,
            estimated_size=estimated_size,
            size_range=size_range,
            confidence=fitting_result.confidence,
            mesh_url=glb_url,
            recommendations=recommendations,
            phenotypes=fitting_result.phenotypes,
        )

    async def _analyze_from_keypoints(
        self,
        keypoints_3d: list[list[float]] | None,
        glb_url: str | None = None,
    ) -> BodyAnalysisResult:
        """
        Fallback: Analyze using SAM-3D keypoints directly (no ANNY).

        This is less accurate but doesn't require GPU.
        """
        if not keypoints_3d or len(keypoints_3d) < 15:
            # Return placeholder if no keypoints
            return self._placeholder_result(glb_url)

        import numpy as np

        kp = np.array(keypoints_3d)

        # SAM-3D keypoint indices (approximate - verify with actual output)
        # Based on standard body model conventions
        RIGHT_SHOULDER, LEFT_SHOULDER = 1, 2
        RIGHT_HIP, LEFT_HIP = 9, 10

        # Estimate measurements from keypoint distances
        shoulder_width = np.linalg.norm(kp[RIGHT_SHOULDER] - kp[LEFT_SHOULDER])
        hip_width = np.linalg.norm(kp[RIGHT_HIP] - kp[LEFT_HIP])

        # Rough circumference estimates (multiply width by ~pi * depth_factor)
        # These are approximate and should be calibrated
        bust_m = shoulder_width * 2.8  # Approximate circumference
        waist_m = (shoulder_width + hip_width) / 2 * 2.2  # Estimate waist
        hips_m = hip_width * 3.0  # Approximate circumference

        # Convert to inches (assuming keypoints are in meters)
        bust_inches = bust_m * 39.37
        waist_inches = waist_m * 39.37
        hips_inches = hips_m * 39.37

        # Clamp to reasonable ranges
        bust_inches = max(30, min(60, bust_inches))
        waist_inches = max(22, min(50, waist_inches))
        hips_inches = max(32, min(60, hips_inches))

        measurements = BodyMeasurements(
            bust=bust_inches,
            waist=waist_inches,
            hips=hips_inches,
        )

        body_type = classify_body_type(bust_inches, waist_inches, hips_inches)
        estimated_size = calculate_dress_size(bust_inches, waist_inches, hips_inches)
        size_range = get_size_range(estimated_size)
        recommendations = get_silhouette_recommendations(body_type)

        return BodyAnalysisResult(
            measurements=measurements,
            body_type=body_type,
            estimated_size=estimated_size,
            size_range=size_range,
            confidence=0.6,  # Lower confidence for keypoint-only analysis
            mesh_url=glb_url,
            recommendations=recommendations,
            phenotypes=None,
        )

    def _placeholder_result(self, glb_url: str | None = None) -> BodyAnalysisResult:
        """Return placeholder result when analysis isn't possible."""
        measurements = BodyMeasurements(bust=36.0, waist=28.0, hips=38.0)
        body_type = classify_body_type(36.0, 28.0, 38.0)

        return BodyAnalysisResult(
            measurements=measurements,
            body_type=body_type,
            estimated_size=8,
            size_range="6-10",
            confidence=0.0,
            mesh_url=glb_url,
            recommendations=get_silhouette_recommendations(body_type),
            phenotypes=None,
        )


# Legacy function for backward compatibility
async def analyze_body_from_image(image_base64: str) -> BodyAnalysisResult:
    """
    Legacy function - analyze from base64 image.

    Note: This requires calling SAM-3D-Body API first to get the mesh.
    For direct image analysis, use the /api/analyze-body endpoint which
    handles the SAM-3D-Body call.
    """
    analyzer = BodyAnalyzer(use_anny=False)
    return analyzer._placeholder_result()
