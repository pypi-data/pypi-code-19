from math import sqrt, cos, sin, degrees, asin, atan
# Import Pillow:
from PIL import Image

# Load the original image:
for i_img, img_name in enumerate(["rot_poly_p3.jpg", "rot_poly_m3.jpg"]):
    img = Image.open(img_name)
    
    if i_img==0:
        #img_name = "rot_poly_p3.jpg"
        xmin = (135, 666)
        xmax = (877, 627)
    else:
        #img_name = "rot_poly_m3.jpg"
        xmin = (106, 627)
        xmax = (848, 666)

    print( img_name )
    dy = float( xmax[1] - xmin[1] )
    dx = float( xmax[0] - xmin[0] )
    print('dx=%g, dy=%g'%(dx,dy))
    ang = atan( dy/dx )
    print('ang=%g(%g)'%(ang, degrees(ang)))
        
    print('='*55)
    
    img_name_fixed = 'fixed_' + img_name
    img_fix = img.rotate(degrees(ang), resample=Image.BICUBIC)
    img_fix.save(img_name_fixed)


