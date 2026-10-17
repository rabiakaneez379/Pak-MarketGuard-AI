
from io import BytesIO

from PIL import Image

from app.image_inspector import inspect_image


def create_test_image(color="red"):
    image = Image.new("RGB", (100, 80), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_valid_image():
    result = inspect_image(create_test_image())

    assert result["status"] == "success"
    assert result["width"] == 100
    assert result["height"] == 80
    assert result["format"] == "PNG"


def test_empty_image():
    result = inspect_image(b"")

    assert result["status"] == "error"


def test_invalid_image():
    result = inspect_image(b"this is not an image")

    assert result["status"] == "error"


def test_identical_reference_image():
    image_bytes = create_test_image()

    result = inspect_image(
        image_bytes,
        reference_bytes=image_bytes,
    )

    assert result["status"] == "success"
    assert result["reference_comparison"]["perceptual_hash_distance"] == 0
