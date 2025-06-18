from customtkinter import CTkImage
from PIL import Image
from .constants import ICON_DIR

def load(name: str, size=(18, 18)) -> CTkImage | None:
    path = ICON_DIR / name
    try:
        return CTkImage(Image.open(path), size=size)
    except FileNotFoundError:
        print(f"[WARN] icon missing: {path}")
        return None
