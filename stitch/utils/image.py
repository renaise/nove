"""Image processing utilities"""

from PIL import Image
from pathlib import Path
from typing import Tuple
import hashlib
from datetime import datetime


def validate_image(image_path: Path, max_size_mb: int = 10, max_dimension: int = 4096) -> Tuple[bool, str]:
    """
    Validate uploaded image

    Returns:
        (is_valid, error_message)
    """
    # Check file exists
    if not image_path.exists():
        return False, "Image file not found"

    # Check file size
    size_mb = image_path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"Image too large: {size_mb:.1f}MB (max {max_size_mb}MB)"

    # Try to open image
    try:
        with Image.open(image_path) as img:
            # Check dimensions
            width, height = img.size
            if width > max_dimension or height > max_dimension:
                return False, f"Image dimensions too large: {width}x{height} (max {max_dimension}px)"

            # Check format
            if img.format not in ["JPEG", "PNG", "WEBP"]:
                return False, f"Unsupported format: {img.format} (use JPEG, PNG, or WEBP)"

            return True, "Valid"

    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def resize_image(image_path: Path, output_path: Path, max_dimension: int = 2048) -> Path:
    """
    Resize image maintaining aspect ratio

    Args:
        image_path: Input image path
        output_path: Output image path
        max_dimension: Maximum width or height

    Returns:
        Path to resized image
    """
    with Image.open(image_path) as img:
        # Calculate new dimensions
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            ratio = min(max_dimension / width, max_dimension / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save
        img.save(output_path, quality=95, optimize=True)

    return output_path


def generate_image_id(image_path: Path) -> str:
    """Generate unique ID for an image based on content hash"""
    with open(image_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{file_hash}"


def create_placeholder_render(output_path: Path, width: int = 800, height: int = 1200) -> Path:
    """
    Create a placeholder image for demo purposes
    In production, this would be replaced by actual ANNY warping
    """
    from PIL import Image, ImageDraw, ImageFont

    # Create image
    img = Image.new('RGB', (width, height), color='#f5f5f5')
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([(10, 10), (width-10, height-10)], outline='#cccccc', width=2)

    # Add text
    text = "Virtual Try-On Render\n(Placeholder)"
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill='#666666')

    # Save
    img.save(output_path, 'PNG')
    return output_path
