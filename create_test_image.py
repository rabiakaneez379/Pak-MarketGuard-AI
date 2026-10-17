from pathlib import Path
from tkinter import Tk, filedialog
from PIL import Image

# Open a file picker to select the original image
root = Tk()
root.withdraw()

selected_file = filedialog.askopenfilename(
    title="Select headphone small.jpg",
    filetypes=[
        ("Image files", "*.jpg *.jpeg *.png *.webp"),
        ("All files", "*.*"),
    ],
)

root.destroy()

if not selected_file:
    print("No image selected. Please run the script again.")
    raise SystemExit

source_path = Path(selected_file)
output_path = Path.cwd() / "headphone_cropped_test6.jpg"

with Image.open(source_path) as image:
    image = image.convert("RGB")

    width, height = image.size

    # Remove 3% from each edge
    left = int(width * 0.03)
    top = int(height * 0.03)
    right = int(width * 0.97)
    bottom = int(height * 0.97)

    cropped = image.crop((left, top, right, bottom))
    cropped.save(output_path, "JPEG", quality=95)

    print("Original image:", image.size)
    print("Cropped image:", cropped.size)
    print("Saved test image:", output_path)