# -*- coding: utf-8 -*-
# Einar Kivisalu, Riivo Mägi, Martin Talimets jt. TTY 04.2017

import os
import sys
import dlib
#import glob
import configparser
import numpy as np
import matplotlib.pyplot as plt
import exifread

from flask import Flask, request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import base64
import io

from random import randint
#from time import clock
from datetime import datetime

#import skimage.io as io

from scipy import misc
#from skimage import filters#, color, io
from skimage.color import rgb2gray
from skimage.segmentation import felzenszwalb
#from skimage.segmentation import mark_boundaries
from skimage.exposure import histogram

# structure for data fields that are returned as response json maessage
class Results:
    result = True
    dimensions = True
    color = True
    brightness = True 
    photoAge = True
    faceQuantity = True
    faceCenter = True
    vertical = True
    eyesHeight = True
    straight = True
    mouthClosed = True
    faceNotSmall = True
    faceNotLarge = True
    background = True    
    fileError = False

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
#    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Fototuvastus API',
    description='Meeskonnaprojekt: Fototuvastus',)

ns = api.namespace('detect', description='Face detection')

#startTime = clock()
config = configparser.ConfigParser()
config.read('config.ini')

dir = os.path.dirname(__file__)
predictor_path = os.path.join(dir, 'shape_predictor_68_face_landmarks.dat')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

# checks whether photo dimensions are more than required minimum values
def checkPhotoDimensions(img):
    try:
        photoMinWidth = int(config['dimensions']['photoMinWidth'])
        photoMinHeight = int(config['dimensions']['photoMinHeight'])
        
        imageHeight = (img.shape[0])    
        imageWidth = (img.shape[1])
        return imageWidth >= photoMinWidth and imageHeight >= photoMinHeight
    except:
        return False

# checks whether randomly selected pixels on the image are all grey 
def is_color(img):
    try:
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
    except:
        return False
    
# checks whether image brightness falls within the allowed limits
def checkBrightness(img):
    try:
        minBrightness = int(config['brightness']['minBrightness'])
        maxBrightness = int(config['brightness']['maxBrightness'])    
        meanBrightness = (np.mean(img))
        
        if minBrightness <= meanBrightness <= maxBrightness:
            return True
        else:
            return False
    except:
        return ("error", False) 
        
# reads the image creation date if image conatains EXIF data 
def checkPhotoAge(data):
    try:
        allowedAge = float(config['photoAge']['allowedAge'])        
        tags = exifread.process_file(data, details=False, stop_tag='EXIF DateTimeOriginal')
        dte = datetime.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
        return ((datetime.date(datetime.now()) - datetime.date(dte)).days) >= allowedAge
    except:
        return "No EXIF data"

# checks that nose is on the image central axis 
def checkFaceCenterToImage(img,shape):
    try:
        axeMinCoeff = float(config['faceCenter']['axeMinCoeff'])
        axeMaxCoeff = float(config['faceCenter']['axeMaxCoeff'])    
        imageWidth = (len((img)[0]))
        axeCoeff = (imageWidth/shape.part(27).x) #nose upper point
        return axeMinCoeff <= axeCoeff <= axeMaxCoeff
    except:
        return False

# checks that only one face is detected on the image 
def checkFaceQuantity(dets):
    try:
        return len(dets) == 1
    except:
        return False

# checks whether nose and chin are in on the same vertical axis
def checkFaceVerticalAxe(shape, detection):
    try:
        maxTiltLimit = float(config['faceVerticality']['maxTiltLimit'])
        chinBottomPoint = shape.part(8).x # (l6ug)
        noseUpperPoint = shape.part(27).x #ninajuur
        faceAxe = abs(chinBottomPoint - noseUpperPoint)/detection.width()
        return faceAxe <= maxTiltLimit
    except:
        return False            
        
# checks whether nose location is symmetric to the detected face central axis 
def checkFaceStraight(shape):
    try:
        faceAssymmetryConstant = float(config['faceAssymmetry']['faceAssymmetryConstant'])    
        leftSideDistance = shape.part(28).x-shape.part(1).x #Distance betveen nose and left side
        rightSideDistance = shape.part(15).x - shape.part(28).x ##Distance betveen nose and right side
        faceWeight = shape.part(15).x - shape.part(1).x
        faceAssymmetry = abs(leftSideDistance - rightSideDistance)  
        faceStraightFactor = faceAssymmetry / faceWeight
        return faceStraightFactor <= faceAssymmetryConstant
    except:
        return False

# checks whether the eye corners are within the allowed limits 
def checkEyesHeight(img,shape):
    try:
        eyesMinHeight = float(config['eyesHeight']['eyesMinHeight'])
        eyesMaxHeight = float(config['eyesHeight']['eyesMaxHeight'])      
        leftEyeLeftPoint = shape.part(36).y
        rightEyeRightPoint = shape.part(45).y
        eyesHeightLine = (leftEyeLeftPoint + rightEyeRightPoint)/2
        imageHeight = (img.shape[0])    
        eyesHeightFactor = (1-eyesHeightLine/imageHeight)
        return eyesMinHeight <= eyesHeightFactor <= eyesMaxHeight
    except:
        return False            
        
# checks whether the distance between lip coordinates is over the limit
def checkMouthClosed(shape, detection):
    try:
        mouthOpenLimit = float(config['mouthClosed']['mouthOpenLimit'])    
        upperLipY= shape.part(66).y
        lowerLipY= shape.part(62).y
        mouthOpenFactor= (upperLipY-lowerLipY)/detection.height()
        return mouthOpenFactor <= mouthOpenLimit
    except:
        return False
 
# checks whether there are color changes in the image upper coreners using Felzenszwalb method
def checkBackgroundObjects(img):
    try:
        upperRectangleHeight = float(config['backGround']['upperRectangleHeight'])
        upperRectangleWidth = float(config['backGround']['upperRectangleWidth'])
        outsideRectangleHeight = float(config['backGround']['outsideRectangleHeight'])
        outsideRectangleWidth = float(config['backGround']['outsideRectangleWidth'])
        scale = float(config['backGround']['scale'])
        sigma = float(config['backGround']['sigma'])
        min_size = int(config['backGround']['min_size'])
        img = rgb2gray(img)
        
        imageHeight = (img.shape[0])    
        imageWidth = (img.shape[1])
        
		#3 pixels from border
        img1 = img[3:int(imageHeight*outsideRectangleHeight), 3:int(imageWidth*outsideRectangleWidth)]
        img2 = img[3:int(imageHeight*upperRectangleHeight), 3:int(imageWidth*upperRectangleWidth)]
        img3 = img[3:int(imageHeight*outsideRectangleHeight), imageWidth-int(imageWidth*outsideRectangleWidth):int(imageWidth-3)]
        img4 = img[3:int(imageHeight*upperRectangleHeight), imageWidth-int(imageWidth*upperRectangleWidth):imageWidth-3]
    
        segments_fz1 = felzenszwalb(img1, scale, sigma, min_size)
        segments_fz2 = felzenszwalb(img2, scale, sigma, min_size)
        segments_fz3 = felzenszwalb(img3, scale, sigma, min_size)
        segments_fz4 = felzenszwalb(img4, scale, sigma, min_size)
        
        segmentsCount1 = (len(np.unique(segments_fz1)))
        segmentsCount2 = (len(np.unique(segments_fz2)))
        segmentsCount3 = (len(np.unique(segments_fz3)))
        segmentsCount4 = (len(np.unique(segments_fz4)))
        sumSegmentsCount = segmentsCount1 + segmentsCount2 + segmentsCount3 + segmentsCount4
        
        return sumSegmentsCount >4    
    except:
        return False
    
# checks whether the face size is under the allowed limits
def checkFaceTooSmall(img, detection):
    try:
        faceSizeMinFactor = float(config['faceDimensions']['faceSizeMinFactor'])
        imageWidth = (len((img)[0]))
        faceSizeFactor = imageWidth/detection.width()
        return faceSizeFactor >= faceSizeMinFactor
    except:
        return False

# checks whether the face size is over the allowed limits
def checkFaceTooLarge(img, detection):
    try:
        faceSizeMaxFactor = float(config['faceDimensions']['faceSizeMaxFactor'])    
        imageWidth = (len((img)[0]))
        faceSizeFactor = imageWidth/detection.width()
        return faceSizeFactor <= faceSizeMaxFactor
    except:
        return False
    
# main detection function - calls to the 'check' functions to do the actual checking 
def runDetect(data):
    result = Results()    

    try:
        d2 = io.BytesIO(data)
    except:
        result.result = False
        result.fileError = True
        return result

        # Photo age
    result.photoage = checkPhotoAge(d2)

    try:
        img = misc.imread(d2, False, 'RGB')
        d2.close()
    except:
        result.result = False
        result.fileError = True
        return result
          
    # Photo minimal dimensions
    result.dimensions = checkPhotoDimensions(img)
            
    # Photo has color, not grayscale
    result.color = is_color(img) #checkPhotoColor(img)
    
    # Photo brightness is OK
    result.brightness = checkBrightness(img)
    
    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    # Number of faces detected
    dets = detector(img, 1)
    
    # Background correct
    result.background = checkBackgroundObjects(img)
   
    # Face quantity
    result.facequantity = checkFaceQuantity(dets)

    for k, d in enumerate(dets): 
        # Get the landmarks/parts for the face in box d.
        shape = predictor(img, d)

        # Face centering
        result.faceCenter = checkFaceCenterToImage(img,shape)
        
        # Face verticality
        result.vertical = checkFaceVerticalAxe(shape, d)
     
        # Face is straight
        result.straight = checkFaceStraight(shape)
        
        # Eyes height correct
        result.eyesHeight = checkEyesHeight(img,shape)
        
        # Mouth is closed
        result.mouthClosed = checkMouthClosed(shape, d)
        
        # Face not small
        result.faceNotSmall = checkFaceTooSmall(img,d)    
        
        # Face not large
        result.faceNotLarge = checkFaceTooLarge(img,d)
        
        
    # Draw the face landmarks on the screen.
    if (result.background == False or result.brightness == False or
        result.color == False or result.dimensions == False or 
        result.eyesHeight == False or result.faceCenter == False or
        result.faceNotLarge == False or result.faceQuantity == False or 
        result.faceNotSmall == False or result.mouthClosed == False or
        result.photoAge == False or result.straight == False or 
        result.vertical == False): 
        result.result = False
    else:
        result.result = True
                
    return result.__dict__

# currently unused
def main():
    dir = os.path.dirname(__file__)
# do the image detection with all the image files on the specified path
"""
    for f in glob.glob(os.path.join(dir, 'images',"*.*")):
        extension = os.path.splitext(f)[1]
        if extension == ".jpg" or extension == ".jpeg" or extension == ".png" or extension == ".tif" or extension == ".tiff" or extension == ".bmp":
            print(f)
            for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
            print("\nProcessing file: {}".format(f))
            img = misc.imread(d2, False, 'RGB')
            runDetect(data)
"""            
# generate base64 encoded text file from each image into the python code directory
"""
            fi = open(f, "rb")
            data = fi.read()
            b64 = base64.b64encode(data)
            b64fn = os.path.splitext(os.path.basename(f))[0] + ".txt"
            f2 = open(b64fn, "wb")
            f2.write(b64)
            fi.close()
            f2.close()
"""         

resource_fields = api.model('Resource', {
    'base64': fields.String,
})

@ns.route('/start')
class Detection(Resource):
    @ns.doc('Process image')
    @api.expect(resource_fields)
    def post(self):
        try:
            json_data = request.get_json(force=True)
            b64 = json_data['base64']
            data = base64.b64decode(b64)
            return runDetect(data)
        except:
            result = Results();
            result.result = False;
            result.fileError = True;
            return result.__dict__
    
if __name__ == '__main__':
    app.run() #Comment this line in, for running on localhost
#    app.run(host="0.0.0.0", port=int("80"),)
    main()
#    timeLeft = (clock() - startTime) #arvutab kulunud aja
