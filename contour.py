# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:34:22 2017

@author: Einar
"""

#import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from skimage import io, color
#import dlib
import glob
import os

dir = os.path.dirname(__file__)

faces_folder_path = os.path.join(dir,'images')

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("\nProcessing file: {}".format(f))
    r = io.imread(f)


#    r = io.imread(r'D:\isiklik\TTY\Meeskonnatoo\codewc\trunk\images\passportphoto-front.jpg')
    r = color.rgb2gray(r)
    
    # Find contours at a constant value of 0.8
    contours = measure.find_contours(r, 0.8)
    
    # Select the largest contiguous contour
    contour = sorted(contours, key=lambda x: len(x))[-1]
    
    # Display the image and plot the contour
    fig, ax = plt.subplots()
    ax.imshow(r, interpolation='nearest', cmap=plt.cm.gray)
    X, Y = ax.get_xlim(), ax.get_ylim()
    ax.step(contour.T[1], contour.T[0], linewidth=2, c='b')
    ax.set_xlim(X), ax.set_ylim(Y)
    
    plt.show()
    