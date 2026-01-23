from PIL import Image
import os

def convert():
    try:
        img = Image.open("assets/icon.png")
        img.save("assets/icon.ico", format="ICO", sizes=[(256, 256)])
        print("Converted assets/icon.png to assets/icon.ico successfully.")
    except Exception as e:
        print(f"Failed to convert icon: {e}")

if __name__ == "__main__":
    convert()
