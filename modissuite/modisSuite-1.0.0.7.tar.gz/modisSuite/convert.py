#!/usr/bin/python3
# coding: utf8 

# Importations
import numpy as np


# Function to convert points
def cartToSin(x,y,diameter):
    # Convert radient coordinates to sin
    phy=y/diameter
    lamb=x/diameter
    return lamb*np.cos(phy),phy

def sinToCart(x,y,diameter):
    # Convert radient sin to coordinates
    x/=(diameter)
    y/=(diameter)
    return x/(np.cos(y)),y 
