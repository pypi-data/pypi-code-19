from sklearn.covariance import EmpiricalCovariance as EC
import numpy as np
from scipy import linalg
from scipy.stats import chi2
from shapely import geometry
from shapely import affinity

def score(A,B,conf=0.95,df=2):
    shapeA = shape_(A,conf,df)
    shapeB = shape_(B,conf,df)
    intersection = shapeA.intersection(shapeB)
    intersection_2 = shapeB.intersection(shapeA)
    intersection_area = intersection.area
    print('Intersection Area:', intersection.area)
    print('Intersection 2 Area:', intersection_2.area)
    print('Shape A Area:', shapeA.area)
    print('Shape B Area:', shapeB.area)

    return(round(max(intersection_area/shapeA.area, intersection_area/shapeB.area),3))

def shape_(data,conf,df):
    ec = EC()

    # Calculate mean
    centre = np.mean(data,axis=0)

    # Calculate covariance matrix
    covar = ec.fit(data).covariance_
    v, w = linalg.eigh(covar)

    # Major/Minor axis lengths from eigenvalues
    semi_axis_lengths = np.sqrt(chi2.ppf(conf,df)) * np.sqrt(v)

    # Normalise eigenvector
    u = w[:,0] / linalg.norm(w[:,0])

    # Compute angle to axis
    angle = np.arctan(u[1] / u[0])
    # angle = 180. * angle / np.pi

    # Create circle and scale to ellipse lengths
    circ = geometry.Point(centre).buffer(1)
    ellipse  = affinity.scale(circ,float(semi_axis_lengths[0]),float(semi_axis_lengths[1]))

    # Return rotated ellipse
    return affinity.rotate(ellipse,angle,use_radians=True)
