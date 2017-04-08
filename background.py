# idea from http://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html
#from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from skimage import io

from skimage.color import rgb2gray
from skimage.segmentation import felzenszwalb
from skimage.segmentation import mark_boundaries
#from skimage.transform import resize

dir = os.path.dirname(__file__)

faces_folder_path = os.path.join(dir,'images')

#win = dlib.image_window()

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("\nProcessing file: {}".format(f))
    img = io.imread(f)    
    img = rgb2gray(img)
#    img = resize(img, (750,600))
    
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
    img1 = img[3:int(imageHeight*0.4), 3:int(imageWidth*0.06)]
    img2 = img[3:int(imageHeight*0.2), 3:int(imageWidth*0.15)]
    img3 = img[3:int(imageHeight*0.4), imageWidth-int(imageWidth*0.06):int(imageWidth-3)]
    img4 = img[3:int(imageHeight*0.2), imageWidth-int(imageWidth*0.15):imageWidth-3]

    segments_fz = felzenszwalb(img, scale=300, sigma=2.2, min_size=80)
    segments_fz1 = felzenszwalb(img1, scale=300, sigma=2.2, min_size=80)
    segments_fz2 = felzenszwalb(img2, scale=300, sigma=2.2, min_size=80)
    segments_fz3 = felzenszwalb(img3, scale=300, sigma=2.2, min_size=80)
    segments_fz4 = felzenszwalb(img4, scale=300, sigma=2.2, min_size=80)
    
    segmentsCount1 = (len(np.unique(segments_fz1)))
    segmentsCount2 = (len(np.unique(segments_fz2)))
    segmentsCount3 = (len(np.unique(segments_fz3)))
    segmentsCount4 = (len(np.unique(segments_fz4)))
    sumSegmentsCount = segmentsCount1 + segmentsCount2 + segmentsCount3 + segmentsCount4
    
    print("Felzenszwalb number of corner segments: {}".format(sumSegmentsCount))
    
    fig, ax = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True,
                           subplot_kw={'adjustable': 'box-forced'})
    
    ax[0, 0].imshow(mark_boundaries(img1, segments_fz1, (100,20,100)))
    ax[0, 0].imshow(mark_boundaries(img2, segments_fz2, (100,20,100)))    
    ax[0, 0].set_title("Felzenszwalbs's method, vasak ylemine nurk")    
    
    ax[0, 1].imshow(mark_boundaries(img3, segments_fz3, (100,100,10)))
    ax[0, 1].imshow(mark_boundaries(img4, segments_fz4, (100,100,10)))    
    ax[0, 1].set_title("Felzenszwalbs's method, parem ylemine nurk")  
    
    ax[1, 0].imshow(mark_boundaries(img, segments_fz, (100,20,50)))
     
    plt.tight_layout()
    plt.show()

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
"""
