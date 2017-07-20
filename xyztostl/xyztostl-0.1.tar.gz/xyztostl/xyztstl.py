import numpy as np
from scipy.spatial import Delaunay
import os
import sys
def xyztostl(filename,centerfinder = "centroid",showpoints=False,showpointswithcentroid=False):
    #apply selected method to all data in order to find the center point
    checkedFilename = filenameChecker(filename=filename)
    yourResult = np.loadtxt(fname = str(checkedFilename),delimiter=',')
    center = [0,0,0]
    if(centerfinder=="centroid"):
       center = np.divide(np.sum(yourResult,axis=0),len(yourResult))
    
    # #In order to calculate the direction of the normal vector given points a,b,c we are going to 
    # #look at the cross product of a-b, a-c
    # unscaledNormalVector = np.cross(yourResult[0]-yourResult[1],yourResult[0]-yourResult[2])
    # scaledNormalVector = unscaledNormalVector/np.linalg.norm(unscaledNormalVector)
    # #This is how we are going to check the direction of the normal vector
    # if(np.dot((yourResult[0]+yourResult[1]+yourResult[2])/3 - center, scaledNormalVector) < 0):
    #     scaledNormalVector *= -1



    #The indexes of the facets we wish to consider is: Delaunay(yourResult).simplices
    with open(filename+'.stl','w+') as file:
        simplex = Delaunay(yourResult).simplices
        file.write("sold OpenSCAD_Model\n")
        for i in simplex:
            vertexList = [yourResult[j] for j in i]
            facetNormal = np.cross(vertexList[0]-vertexList[1],vertexList[0]-vertexList[2])
            scaledFacetNormal = np.linalg.norm(facetNormal)
            scaledNormalVector = facetNormal/scaledFacetNormal
            print((vertexList[0]+vertexList[1]+vertexList[2])/3 - center)
            print(scaledFacetNormal)
            if(np.dot((vertexList[0]+vertexList[1]+vertexList[2])/3 - center, scaledNormalVector) < 0):
                scaledNormalVector *= -1
            file.write("    facet normal "+ str(scaledNormalVector[0]) + " " +str(scaledNormalVector[1]) + " " +str(scaledNormalVector[2]) +'\n')
            file.write("        outer loop\n")
            for vert in vertexList:
                file.write("            vertex " +str(vert[0]) + " " + str(vert[1]) + " " + str(vert[2]) + "\n")
            file.write("        endloop\n")
            file.write("    endfacet\n")
        file.write("endsolid OpenSCAD_Model")



    #We will solve triangulation using delaunary triangulation



def textfiletester(numpytextfile):
    for i in numpytextfile:
        if(len(i)!=3):
            raise Exception('XYZ file has a line that is not 3 dimensional')

def filenameChecker(filename):
    if(os.path.isfile(filename)):
        return filename
    elif(os.path.isfile(filename+".txt")):
        return filename+".txt"
    else:
        sys.exit("Unknown file type")


if __name__ == "__main__":
    xyztostl("test2sphere")


# solid OpenSCAD_Model
#   facet normal -1 0 0
#     outer loop
#       vertex 1.75 0 21
#       vertex 1.75 23 36
#       vertex 1.75 23 21
#     endloop
#   endfacet
#   facet normal -1 -0 0
#     outer loop
#       vertex 1.75 23 36
#       vertex 1.75 0 21
#       vertex 1.75 0 36
#     endloop
#   endfacet
# endsolid OpenSCAD_Model