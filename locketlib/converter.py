from PIL import Image
import random
import string

def image_to_webp(filepath: str) -> None:
    """Convert image to webp and return the filepath"""
    filename = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    image = Image.open(filepath)
    webp = image.copy()
    webp.convert("RGB")
    webp.save(filename + ".webp", "webp", optimize = True, quality = 10)
    return filename + ".webp"