from bing_image_downloader import downloader
import os

# List of recyclable items
items = [
    # Plastic
    "water bottle", "soda bottle", "milk jug", "yogurt container", "shampoo bottle",
    "detergent bottle", "plastic cup", "plastic food container", "plastic bag clean", "disposable cutlery",
    # Paper / Cardboard
    "newspaper", "magazine", "printer paper", "notebook paper", "cardboard box",
    "pizza box clean", "paper bag", "envelopes", "greeting card", "paper egg carton",
    # Metal / Aluminum
    "aluminum can", "tin can", "aluminum foil", "aluminum pie pan", "metal jar lid",
    "steel can", "beverage can ring", "metal bottle cap", "empty aerosol can clean", "small metal utensils",
    # Glass
    "glass bottle", "glass jar", "mason jar", "empty perfume bottle", "olive oil bottle",
    "juice bottle", "glass decanter", "candle jar glass", "medicine glass bottle", "pickle jar",
    # Other / Miscellaneous
    "milk carton", "phone book", "catalog", "paperboard packaging", "empty cosmetic jar",
    "plastic tray food packaging", "bubble wrap", "plastic container lid", "glass cup", "aluminum travel mug"
]

# Directory to save images
output_dir = "recyclable_samples"
os.makedirs(output_dir, exist_ok=True)

# Download images for each item
for item in items:
    print(f"Downloading images for: {item}")
    downloader.download(item, limit=5,  # number of images per item
                        output_dir=output_dir,
                        adult_filter_off=True,
                        force_replace=False,
                        timeout=60)
