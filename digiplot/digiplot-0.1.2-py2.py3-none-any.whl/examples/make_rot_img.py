
# Import Pillow:
from PIL import Image

# Load the original image:
img = Image.open("Tank_ExpEff.jpg")

img8 = img.rotate(1, resample=Image.BICUBIC)
img8.save("Tank_ExpEff_p1.jpg")

