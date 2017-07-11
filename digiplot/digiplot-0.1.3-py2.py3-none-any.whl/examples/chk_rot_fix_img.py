
# Import Pillow:
from PIL import Image

# Load the original image:
img = Image.open("rot_poly_m3.jpg")

img8 = img.rotate(3, resample=Image.BICUBIC)
img8.save("fixed_rot_poly_m3.jpg")

