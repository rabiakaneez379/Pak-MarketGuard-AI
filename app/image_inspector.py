
from io import BytesIO
from typing import Any
import warnings

import imagehash
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_PIXELS = 20_000_000


def inspect_image(
    image_bytes: bytes,
    reference_bytes: bytes | None = None,
) -> dict[str, Any]:
    """
    Inspect a product image and optionally compare it with a reference
    image using perceptual hashing.

    Returns a consistent status field so the dashboard can handle errors.
    """

    if not image_bytes:
        return {
            "status": "error",
            "message": "No image data was supplied.",
        }

    if len(image_bytes) > MAX_IMAGE_BYTES:
        return {
            "status": "error",
            "message": "Image exceeds the 5 MB size limit.",
        }

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(image_bytes)) as source:
                source.verify()

            with Image.open(BytesIO(image_bytes)) as source:
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    return {
                        "status": "error",
                        "message": (
                            "Image dimensions exceed the permitted limit "
                            f"of {MAX_IMAGE_PIXELS:,} pixels."
                        ),
                    }

                image_format = source.format
                image = source.convert("RGB")

        width, height = image.size
        image_hash = imagehash.phash(image)

        result = {
            "status": "success",
            "format": image_format,
            "width": width,
            "height": height,
            "file_size_bytes": len(image_bytes),
            "perceptual_hash": str(image_hash),
            "reference_comparison": None,
            "limitations": [
                "Image metadata and perceptual hashes cannot prove authenticity.",
                "A reference comparison only checks the supplied reference image.",
                "Different crops, edits, or compression can affect similarity.",
            ],
        }

        # Compare against the optional reference image.
        if reference_bytes is not None:
            if not reference_bytes:
                result["reference_comparison"] = {
                    "status": "error",
                    "message": "No reference image data was supplied.",
                }
                return result

            if len(reference_bytes) > MAX_IMAGE_BYTES:
                result["reference_comparison"] = {
                    "status": "error",
                    "message": "Reference image exceeds the 5 MB size limit.",
                }
                return result

            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)

                with Image.open(BytesIO(reference_bytes)) as ref_source:
                    ref_source.verify()

                with Image.open(BytesIO(reference_bytes)) as ref_source:
                    if ref_source.width * ref_source.height > MAX_IMAGE_PIXELS:
                        result["reference_comparison"] = {
                            "status": "error",
                            "message": (
                                "Reference image dimensions exceed the "
                                f"permitted limit of {MAX_IMAGE_PIXELS:,} pixels."
                            ),
                        }
                        return result

                    reference = ref_source.convert("RGB")

            reference_hash = imagehash.phash(reference)
            distance = image_hash - reference_hash

            result["reference_comparison"] = {
                "status": "success",
                "perceptual_hash_distance": int(distance),
                "interpretation": (
                    "The images have very similar perceptual hashes."
                    if distance <= 5
                    else (
                        "The images have some perceptual-hash similarity."
                        if distance <= 10
                        else "The images are not strongly similar by this hash comparison."
                    )
                ),
            }

        return result

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        return {
            "status": "error",
            "message": (
                "The image could not be processed. It may be invalid, "
                "unsupported, or too large."
            ),
        }
