from bing_image_downloader import downloader
import os

# Non-recyclable items
items = [
    "styrofoam cup", "styrofoam tray", "plastic straw", "plastic utensils dirty", "chip bag",
    "candy wrapper", "plastic wrap cling film", "coffee cup lid plastic-coated", "bubble wrap",
    "frozen food packaging", "pizza box greasy", "paper towels", "napkins", "tissue paper",
    "waxed paper", "paper plates used", "sticky notes", "laminated paper", "paper cups dirty",
    "paper cartons with food residue", "aluminum foil with food", "aerosol cans not empty",
    "paint cans", "non-empty spray bottles", "light bulbs incandescent", "batteries",
    "electronics parts", "mirrors", "ceramics pottery", "broken glass", "clothes textiles",
    "rubber bands", "hair ties", "shoes", "food scraps", "diapers", "chewing gum", "plastic toys",
    "cigarette butts", "wax candles", "styrofoam packaging peanuts", "bubble wrap not accepted",
    "plastic-coated magnets", "plastic-coated photos", "plastic-coated cards", "rubber gloves",
    "chip clips", "toothbrushes", "disposable razors", "pet waste bags"
]

# Directory to save images
output_dir = "non_recyclable_samples"
os.makedirs(output_dir, exist_ok=True)

# Download images for each item
for item in items:
    print(f"Downloading images for: {item}")
    downloader.download(item, limit=5,  # images per item
                        output_dir=output_dir,
                        adult_filter_off=True,
                        force_replace=False,
                        timeout=60)
