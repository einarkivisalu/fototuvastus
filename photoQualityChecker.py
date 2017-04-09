# -*- coding: utf-8 -*-
import os
import dlib
import glob
import configparser
import numpy as np
import matplotlib.pyplot as plt

from random import randint
from time import clock

from skimage import io#, color
from skimage.color import rgb2gray
from skimage.segmentation import felzenszwalb
from skimage.segmentation import mark_boundaries

startTime = clock()
config = configparser.ConfigParser()
config.read('config.ini')

def checkPhotoDimensions(img):    
    photoMinWidth = int(config['dimensions']['photoMinWidth'])
    photoMinHeight = int(config['dimensions']['photoMinHeight'])
    
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    if imageWidth >= photoMinWidth and imageHeight >= photoMinHeight:
        return True
    else:
        return False
                  
def is_color(img):
    pixelsCount = int(config['is_color']['pixelsCount'])
    r1,g1,b1 = 0,0,0
    if len(img.shape)==2:
        return False
    else:
        imageHeight = (img.shape[0])
        imageWidth = (img.shape[1])

        for x in range(pixelsCount): # random pixels from image
            randomX =  randint(1,imageHeight-1)
            randomY = randint(1,imageWidth-1)            
            r,g,b = img[randomX,randomY]
            r1 += r
            g1 += g
            b1 += b
        if r1 == g1 == b1:            
            return False
    return True
    
def checkBrightness(img):
    minBrightness = int(config['brightness']['minBrightness'])
    maxBrightness = int(config['brightness']['maxBrightness'])    
    meanBrightness = (np.mean(img))
    print (meanBrightness)
    if minBrightness <= meanBrightness <= maxBrightness:
        return True
    else:
        return False      
        
def checkFaceCenterToImage(img,shape):
    axeMinCoeff = float(config['faceCenter']['axeMinCoeff'])
    axeMaxCoeff = float(config['faceCenter']['axeMaxCoeff'])    
    imageWidth = (len((img)[0]))
    axeCoeff = (imageWidth/shape.part(27).x) #nose upper point
    if axeMinCoeff <= axeCoeff <= axeMaxCoeff:
        return True
    else:
        return False

def checkFaceQuantity(dets):
    if len(dets) == 1:
        return True
    else:
        return False

def checkFaceVerticalAxe(shape, detection):
    maxTiltLimit = float(config['faceVerticality']['maxTiltLimit'])
    chinBottomPoint = shape.part(8).x # (l6ug)
    noseUpperPoint = shape.part(27).x #ninajuur
    faceAxe = abs(chinBottomPoint - noseUpperPoint)/detection.width()
    if faceAxe <= maxTiltLimit:
        return True
    else:
        return False
        
def checkFaceStraight(shape):
    faceAssymmetryConstant = float(config['faceCenter']['faceAssymmetryConstant'])    
    leftSideDistance = shape.part(28).x-shape.part(1).x #Distance betveen nose and left side
    rightSideDistance = shape.part(15).x - shape.part(28).x ##Distance betveen nose and right side
    faceWeight = shape.part(15).x - shape.part(1).x
    faceAssymmetry = abs(leftSideDistance - rightSideDistance)  
    faceStraightFactor = faceAssymmetry / faceWeight
    if faceStraightFactor <= faceAssymmetryConstant:
        return True
    else:
        return False
    return "Not checked yet"

# height of 50–70% of the total vertical length of the photo
def checkEyesHeight(img,shape):
    eyesMinHeight = float(config['eyesHeight']['eyesMinHeight'])
    eyesMaxHeight = float(config['eyesHeight']['eyesMaxHeight'])      
    leftEyeLeftPoint = shape.part(36).y
    rightEyeRightPoint = shape.part(45).y
    eyesHeightLine = (leftEyeLeftPoint + rightEyeRightPoint)/2
    imageHeight = (img.shape[0])    
    eyesHeightFactor = (1-eyesHeightLine/imageHeight)
    if eyesMinHeight <= eyesHeightFactor <= eyesMaxHeight:
        return True
    else:
        return False    
        
def checkMouthClosed(shape, detection):
    mouthOpenLimit = float(config['mouthClosed']['mouthOpenLimit'])    
    upperLipY= shape.part(66).y
    lowerLipY= shape.part(62).y
    mouthOpenFactor= (upperLipY-lowerLipY)/detection.height()
#    print (mouthOpenFactor)
    if mouthOpenFactor <= mouthOpenLimit:
        return True
    else:
        return False

#TODO Kuna silmade detekteerimine ei ole väga hea, siis see lahendus ei toimi.
def checkEyesOpen(shape, detection):
    return "Not checked yet"

#TODO
def checkRedEyes(shape, detection):
#    leftEyeRectangle = shape.part(37).y 
    return "Not checked yet"
 
def checkBackgroundObjects(img):
    upperRectangleHeight = float(config['mouthClosed']['mouthOpenLimit'])  
    img = rgb2gray(img)
#    img = resize(img, (750,600))
    
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
    img1 = img[3:int(imageHeight*0.4), 3:int(imageWidth*0.06)]
    img2 = img[3:int(imageHeight*0.2), 3:int(imageWidth*0.15)]
    img3 = img[3:int(imageHeight*0.4), imageWidth-int(imageWidth*0.06):int(imageWidth-3)]
    img4 = img[3:int(imageHeight*0.2), imageWidth-int(imageWidth*0.15):imageWidth-3]

#    segments_fz = felzenszwalb(img, scale=300, sigma=2.2, min_size=80)
    segments_fz1 = felzenszwalb(img1, scale=300, sigma=2.2, min_size=80)
    segments_fz2 = felzenszwalb(img2, scale=300, sigma=2.2, min_size=80)
    segments_fz3 = felzenszwalb(img3, scale=300, sigma=2.2, min_size=80)
    segments_fz4 = felzenszwalb(img4, scale=300, sigma=2.2, min_size=80)
    
    segmentsCount1 = (len(np.unique(segments_fz1)))
    segmentsCount2 = (len(np.unique(segments_fz2)))
    segmentsCount3 = (len(np.unique(segments_fz3)))
    segmentsCount4 = (len(np.unique(segments_fz4)))
    sumSegmentsCount = segmentsCount1 + segmentsCount2 + segmentsCount3 + segmentsCount4

    """    
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
    if sumSegmentsCount >4:
        return False
    else:
        return True    
    return "Not checked yet"
    
def checkFaceTooSmall(img, detection):
    imageWidth = (len((img)[0]))
    imagesizeFactor = imageWidth/detection.width()
#    print ("imagesizeFactor: ",imagesizeFactor)
    if imagesizeFactor >=3:
        return False
    else:
        return True
        
def checkFaceTooLarge(img, detection):
    imageWidth = (len((img)[0]))
    imagesizeFactor = imageWidth/detection.width()
#    print ("imagesizeFactor: ",imagesizeFactor)
    if imagesizeFactor <=1.5:
        return False
    else:
        return True

def main():
             
    dir = os.path.dirname(__file__)
    predictor_path = os.path.join(dir, 'shape_predictor_68_face_landmarks.dat')
    
    faces_folder_path = os.path.join(dir,'images')
    print (faces_folder_path)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    win = dlib.image_window()
    
    for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
        print("\nProcessing file: {}".format(f))
        img = io.imread(f)
    
        win.clear_overlay()
        win.set_image(img)
               
        photoDimensionsB = checkPhotoDimensions(img)
        print ("Photo minimal dimensions OK: {}".format(photoDimensionsB))
        
        photoColorityB = is_color(img) #checkPhotoColor(img)
        print ("Photo is color: {}".format(photoColorityB)) 
        
        photoBrightnessB = checkBrightness(img)
        print ("Photo brightness is OK: {}".format(photoBrightnessB))
    
        # Ask the detector to find the bounding boxes of each face. The 1 in the
        # second argument indicates that we should upsample the image 1 time. This
        # will make everything bigger and allow us to detect more faces.
        dets = detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))
        for k, d in enumerate(dets): 
            print("\nDetected face No: {}".format(k))
            # Get the landmarks/parts for the face in box d.
            shape = predictor(img, d)
    
            faceQuantityB = checkFaceQuantity(dets)
            print ("Face quantity: {}".format(faceQuantityB))
            
            faceCenterB =checkFaceCenterToImage(img,shape)
            print ("Face centering: {}".format(faceCenterB))
            
            faceVerticalAxeB = checkFaceVerticalAxe(shape, d)
            print ("Face verticality: {}".format(faceVerticalAxeB))
         
            faceIsStraightB = checkFaceStraight(shape)
            print ("Face is straight: {}".format(faceIsStraightB))
            
            eyesHeightB =checkEyesHeight(img,shape)
            print ("Eyes height correct: {}".format(eyesHeightB))        
            
            mouthClosedB = checkMouthClosed(shape, d)
            print ("Mouth is closed: {}".format(mouthClosedB))
            
            faceTooSmallB= checkFaceTooSmall(img,d)
            print ("Face not small: {}".format(faceTooSmallB))        
            
            faceTooLargeB= checkFaceTooLarge(img,d)
            print ("Face not large: {}".format(faceTooLargeB)) 
            
    #        eyesOpendB = checkEyesOpen(shape, d)
    #        print ("Eyes are open: {}".format(eyesOpendB))
            
    #        redEyesB = checkRedEyes(shape, d)
    #        print ("Red eyes not detected: {}".format(redEyesB))
    
            backgroundB= checkBackgroundObjects(img)
            print ("Background correct: {}".format(backgroundB))
            
            # Draw the face landmarks on the screen.
            win.add_overlay(shape)
        win.add_overlay(dets)    
#        input("Press Enter to continue...")
        timeLeft = (clock() - startTime) #arvutab kulunud aja

    print("Time left: {} sec".format(timeLeft))
    
if __name__ == '__main__':
    main()