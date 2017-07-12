#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import math

from hgl.calculate.point import vector_multiply
from hgl.settings import X, Y, Z

# http://stackoverflow.com/questions/5443653/opengl-coordinates-from-bezier-curves
# http://nccastaff.bournemouth.ac.uk/jmacey/RobTheBloke/www/opengl_programming.html#3
# http://www.pasteall.org/6266/python
# http://stackoverflow.com/questions/12643079/b%C3%A9zier-curve-fitting-with-scipy



def curve_simple(p1, p2, p3):
    return generate_quadratic_bezier_curve_points((p1, p2, p3))

def generate_quadratic_bezier_curve_points(points, steps=20):
    """Given a list of points interpolate between them by x steps generating the curve points 
    for a Quadratic Bezier Curve

    Args:
      points (point list): List of point locations
      steps (int): number of points between each point
      
    Returns:
      points: returns list of new points 

    Links:
        http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B.C3.A9zier_curves
    Images:"""


    jump = 1.0 / steps
    new_points = []
    results = [points[0]]
    for step in range(1, steps):
        t = jump * step
        tmp_points = points
        while len(tmp_points) > 1:
            new_points = []
            for end in range(1, len(tmp_points)):
                start = end - 1
                direction = (tmp_points[end][X] - tmp_points[start][X],
                             tmp_points[end][Y] - tmp_points[start][Y],
                             tmp_points[end][Z] - tmp_points[start][Z])
                if t and t>0.0 and t<=1.0:
                    new_points.append((tmp_points[start][X] + (direction[X] * t),
                                       tmp_points[start][Y] + (direction[Y] * t),
                                       tmp_points[start][Z] + (direction[Z] * t)))
            tmp_points = new_points
        if new_points:
            results.append(new_points[0])
    results.append(points[-1])
    return results


#~ 
    #~ steps = 20
    #~ for i in range(steps):
#~ 
        #~ t = i / float(steps)
#~ 
        #~ xloc = math.pow(1-t,3) * points[0][0] \
             #~ + 3*t*math.pow(1-t,2) * points[1][0] \
             #~ + 3*(1-t)*math.pow(t,2) * points[2][0] \
             #~ + math.pow(t,3) * points[3][0]
        #~ yloc = math.pow(1-t,3) * points[0][1] \
             #~ + 3*t*math.pow(1-t,2) * points[1][1] \
             #~ + 3*(1-t)*math.pow(t,2) * points[2][1] \
             #~ + math.pow(t,3) * points[3][1]


def generate_cubic_bezier_curve_points2(points, t1=0.1, steps=16):
    """Given a list of points interpolate between them by x steps generating the curve points 
    for a Cubic Bezier Curve

    Args:
      points (point list): List of point locations
      steps (int): number of points between each point
      
    Returns:
      points: returns list of new points 

    Links:
        http://en.wikipedia.org/wiki/Bézier_curve
        http://www.pasteall.org/6266/python
        http://html5tutorial.com/how-to-draw-n-grade-bezier-curve-with-canvas-api/
        http://html5tutorial.com/how-to-join-two-bezier-curves-with-the-canvas-api/
        http://pomax.github.io/bezierinfo/
    Images:"""
    
    #testing
    t1_step = 1 / steps
    t1 = t1_step
    while t1 < 1:
        t1_pow_of_three = math.pow(t1, 3)
        t1_pow_of_two = math.pow(t1, 2)

        t2 = (1 - t1) 
        t2_pow_of_three = math.pow(t2, 3)
        t2_pow_of_two = math.pow(t2, 2)


        part1 = vector_multiply(points[0], t2_pow_of_three)
        part2 = vector_multiply(points[1], 3 * t2_pow_of_two * t1)
        part3 = vector_multiply(points[2], 3 * t2 * t1_pow_of_two)
        part4 = vector_multiply(points[3], t1_pow_of_three)

        #~ print part1
        #~ print part2
        #~ print part3
        #~ print part4

        point = (part1[0] + part2[0] + part3[0] + part4[0],
                part1[1] + part2[1] + part3[1] + part4[1],
                part1[2] + part2[2] + part3[2] + part4[2])
        #~ print 'point'
        #~ print point
        t1 += t1_step


    #~ point = (part1[0] + part2[0] + part3[0], part4[0],
            #~ part1[1] + part2[1] + part3[1], part4[1],
            #~ part1[2] + part2[2] + part3[2], part4[2])
    #testing

    #~ jump = 1.0 / steps
    #~ new_points = []
    #~ results = [points[0]]
    #~ for step in range(1, steps):
        #~ t = jump * step
        #~ tmp_points = points
        #~ while len(tmp_points) > 1:
            #~ new_points = []
            #~ for end in xrange(1, len(tmp_points)):
                #~ start = end - 1
                #~ direction = (tmp_points[end][X] - tmp_points[start][X],
                             #~ tmp_points[end][Y] - tmp_points[start][Y],
                             #~ tmp_points[end][Z] - tmp_points[start][Z])
                #~ if t and t>0.0 and t<=1.0:
                    #~ new_points.append([tmp_points[start][X] + (direction[X] * t),
                                       #~ tmp_points[start][Y] + (direction[Y] * t),
                                       #~ tmp_points[start][Z] + (direction[Z] * t)])
            #~ tmp_points = new_points
        #~ if new_points:
            #~ results.append(new_points[0])
    #~ results.append(points[-1])
    return results


def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i

def generate_cubic_bezier_curve_points(points, steps=16):
    #~ print 'generate_cubic_bezier_curve_points'
    jump = 1.0 / steps
    new_points = [points[0]]
    t = 0
    for step in range(1, steps):
        t += jump #* step
        #~ print 't = ' + str(t)
        new_points.append(generate_bezier(points, t))
        
    new_points.append(points[-1])
    return new_points


def generate_bezier(points, t):
    start = 0
    end = len(points)
    if end == 1:
        return points[0]
        
    de_casteljau(points, t)
    return generate_bezier(de_casteljau(points, t), t)


def de_casteljau(points, t):
    """interpolate each control line to gain a point on the line and reduce the handles by one, repeat until a single point is left
    repeat incrementing the point on each iteration.

    Args:
      points (point list): List of point locations
      t (int): t point between 0 and 1, 0 is near first point 1 being closed to the second point
      
    Returns:
      points: returns list of new points 

    Links:
        http://en.wikipedia.org/wiki/De_Casteljau's_algorithm

    Images:"""
    t1 = 1 - t
    
    #~ start = 0
    end = len(points)
    #~ if end == 1:
        #~ return points[0]

    start = 0
    new_points = []
    for end in range(1, end):
        new_points.append([
            ((points[start][X] * t1) + (points[end][X] * t)),
            ((points[start][Y] * t1) + (points[end][Y] * t)),
            ((points[start][Z] * t1) + (points[end][Z] * t))])
        start += 1
    return new_points #de_casteljau(new_points, t)


#de_casteljau
#http://23ars.blogspot.ro/2012/12/generating-bezier-curves-using-de.html
def smooth(self, points, i, j, t):
    #print 'points i ' + str(points[i])
    if j==0:
        return points[i]
    return self.smooth(points,i,j-1,t)*(1-t)+self.smooth(points,i+1,j-1,t)*t
