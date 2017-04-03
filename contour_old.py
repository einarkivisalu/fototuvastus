# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 20:46:21 2017
@author: einark
"""
import numpy as np
import dlib
import glob
import os
import matplotlib.pyplot as plt
#from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage import io


dir = os.path.dirname(__file__)
path = os.path.join(dir, 'images', 'photo.jpg')#.replace("\\","/")
img = io.imread(path)

dir = os.path.dirname(__file__)

faces_folder_path = os.path.join(dir,'images')

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
#    print("\nProcessing file: {}".format(f))
    img = io.imread(f)

    #img = rgb2gray(img)
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
    s = np.linspace(0, 2*np.pi, 400)
    x = imageWidth/2 + imageWidth/2.5*np.cos(s)
    y = imageHeight/2.1 + imageHeight/2.1*np.sin(s)
    init = np.array([x, y]).T
    
    snake = active_contour(gaussian(img, 3),
                           init, alpha=0.015, beta=5, gamma=0.001)
    
    #print(snake) 
    #win.add_overlay(snake)
    
    #Järgnev osa joonistab kontuuri pildile
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111)
    plt.gray()
    ax.imshow(img)
    ax.plot(init[:, 0], init[:, 1], '--r', lw=3) #piirav kontuur
    ax.plot(snake[:, 0], snake[:, 1], '-b', lw=3)
    ax.set_xticks([]), ax.set_yticks([]) #pikslite teljestik 0
    ax.axis([0, img.shape[1], img.shape[0], 0]) #pildi raam 0
#    plt.savefig(f +'.png', bbox_inches='tight')