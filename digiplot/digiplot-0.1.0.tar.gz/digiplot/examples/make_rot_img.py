
# Import Pillow:
from PIL import Image

# Load the original image:
img = Image.open("sample_poly.png")

img8 = img.rotate(-3, resample=Image.BICUBIC)
img8.save("rot_poly_m3.jpg")

