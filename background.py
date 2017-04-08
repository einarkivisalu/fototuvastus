from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import os
import dlib
import glob
from skimage import io

from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, quickshift
from skimage.segmentation import mark_boundaries


dir = os.path.dirname(__file__)

faces_folder_path = os.path.join(dir,'images')

#win = dlib.image_window()

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("\nProcessing file: {}".format(f))
    img = io.imread(f)

    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
#    print (imageHeight, imageWidth)
#    img.size = (600,750)
    img1 = img[0:imageHeight/2.5,0:imageWidth/10]
    img2 = img[0:imageHeight/2.5, imageWidth-imageWidth/10:imageWidth]
    img2 = rgb2gray(img2)
    img1 = rgb2gray(img1)
#    img = rgb2gray(img)    

#    segments_fz = felzenszwalb(img, scale=300, sigma=0.8, min_size=60)
#    segments_fz1 = felzenszwalb(img1, scale=300, sigma=0.8, min_size=50)
#    segments_fz2 = felzenszwalb(img2, scale=300, sigma=0.8, min_size=50)
    
    segments_quick = quickshift(img, kernel_size=15, max_dist=6, ratio=0.5)
    
#    print("Felzenszwalb number of segments 1: {}".format(len(np.unique(segments_fz1))))
    print (img1.shape[0])    
    print (img1.shape[1])
#    print("Felzenszwalb number of segments 2: {}".format(len(np.unique(segments_fz2))))
    
    fig, ax = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True,
                           subplot_kw={'adjustable': 'box-forced'})
    
#    ax[0, 0].imshow(mark_boundaries(img1, segments_fz1))
    ax[0, 0].set_title("Felzenszwalbs's method, vasak serv")
    
#    ax[0, 1].imshow(mark_boundaries(img2, segments_fz2)) 
    ax[0, 1].set_title("Felzenszwalbs's method, parem serv")  
    
#   ax[1, 0].imshow(mark_boundaries(img, segments_fz))
 
    ax[1, 0].imshow(mark_boundaries(img, segments_quick))
    ax[1, 0].set_title('Quickshift')
    
    plt.tight_layout()
    plt.show()

# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:30:20 2017

@author: einark

import numpy as np
import dlib
import glob
import os
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage import io
from skimage.draw import polygon
from skimage import measure

dir = os.path.dirname(__file__)

faces_folder_path = os.path.join(dir,'images')

#img2 = np.zeros((10, 10), dtype=np.uint8)
r = np.array([0, 20, 80, 70, 0])
c = np.array([0, 70, 40, 20, 0])
rr, cc = polygon(r, c)

win = dlib.image_window()

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
#    print("\nProcessing file: {}".format(f))
    img = io.imread(f)

    #img = rgb2gray(img)
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
    s = np.linspace(0, 2*np.pi, 400)
    x = imageWidth/2 + imageWidth/2.3*np.cos(s)
    y = imageHeight/2.1 + imageHeight/2.1*np.sin(s)
    init = np.array([x, y]).T
    img[rr, cc] = 1        
    cropped = img[0:400,0:100]
    win.clear_overlay()
    
    win.set_image(img)
"""
"""
====================================================
Comparison of segmentation and superpixel algorithms
====================================================

This example compares four popular low-level image segmentation methods.  As
it is difficult to obtain good segmentations, and the definition of "good"
often depends on the application, these methods are usually used for obtaining
an oversegmentation, also known as superpixels. These superpixels then serve as
a basis for more sophisticated algorithms such as conditional random fields
(CRF).


Felzenszwalb's efficient graph based segmentation
-------------------------------------------------
This fast 2D image segmentation algorithm, proposed in [1]_ is popular in the
computer vision community.
The algorithm has a single ``scale`` parameter that influences the segment
size. The actual size and number of segments can vary greatly, depending on
local contrast.

.. [1] Efficient graph-based image segmentation, Felzenszwalb, P.F. and
       Huttenlocher, D.P.  International Journal of Computer Vision, 2004


Quickshift image segmentation
-----------------------------

Quickshift is a relatively recent 2D image segmentation algorithm, based on an
approximation of kernelized mean-shift. Therefore it belongs to the family of
local mode-seeking algorithms and is applied to the 5D space consisting of
color information and image location [2]_.

One of the benefits of quickshift is that it actually computes a
hierarchical segmentation on multiple scales simultaneously.

Quickshift has two main parameters: ``sigma`` controls the scale of the local
density approximation, ``max_dist`` selects a level in the hierarchical
segmentation that is produced. There is also a trade-off between distance in
color-space and distance in image-space, given by ``ratio``.

.. [2] Quick shift and kernel methods for mode seeking,
       Vedaldi, A. and Soatto, S.
       European Conference on Computer Vision, 2008


SLIC - K-Means based image segmentation
---------------------------------------

This algorithm simply performs K-means in the 5d space of color information and
image location and is therefore closely related to quickshift. As the
clustering method is simpler, it is very efficient. It is essential for this
algorithm to work in Lab color space to obtain good results.  The algorithm
quickly gained momentum and is now widely used. See [3]_ for details.  The
``compactness`` parameter trades off color-similarity and proximity, as in the
case of Quickshift, while ``n_segments`` chooses the number of centers for
kmeans.

.. [3] Radhakrishna Achanta, Appu Shaji, Kevin Smith, Aurelien Lucchi,
    Pascal Fua, and Sabine Suesstrunk, SLIC Superpixels Compared to
    State-of-the-art Superpixel Methods, TPAMI, May 2012.


Compact watershed segmentation of gradient images
-------------------------------------------------

Instead of taking a color image as input, watershed requires a grayscale
*gradient* image, where bright pixels denote a boundary between regions.
The algorithm views the image as a landscape, with bright pixels forming high
peaks. This landscape is then flooded from the given *markers*, until separate
flood basins meet at the peaks. Each distinct basin then forms a different
image segment. [4]_

As with SLIC, there is an additional *compactness* argument that makes it
harder for markers to flood faraway pixels. This makes the watershed regions
more regularly shaped. [5]_

.. [4] http://en.wikipedia.org/wiki/Watershed_%28image_processing%29

.. [5] Peer Neubert & Peter Protzel (2014). Compact Watershed and
       Preemptive SLIC: On Improving Trade-offs of Superpixel Segmentation
       Algorithms. ICPR 2014, pp 996-1001. DOI:10.1109/ICPR.2014.181
       https://www.tu-chemnitz.de/etit/proaut/forschung/rsrc/cws_pSLIC_ICPR.pdf
"""
