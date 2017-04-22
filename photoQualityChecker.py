# -*- coding: utf-8 -*-
# Einar Kivisalu, Riivo Mägi, Martin Talimets jt. TTY 04.2017

import os
import sys
import dlib
import glob
import configparser
import numpy as np
import matplotlib.pyplot as plt
import exifread

from flask import Flask, request
#import flask_restplus.api as Api
#import flask_restplus.resource as Resource
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import base64
import io

from random import randint
from time import clock
from datetime import datetime

#import skimage.io as io

from scipy import misc
from skimage import filters#, color, io
from skimage.color import rgb2gray
from skimage.segmentation import felzenszwalb
from skimage.segmentation import mark_boundaries
from skimage.exposure import histogram

class Results:
    result = True
    dimensions = True
    color = True
    brightness = True 
    photoage = True
    facequantity = True
    facecenter = True
    vertical = True
    eyesheight = True
    straight = True
    mouthclosed = True
    facesmall = True
    facelarge = True
    background = True    

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
#    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__)

#app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Fototuvastus API',
    description='Meeskonnaprojekt: Fototuvastus',)

ns = api.namespace('detect', description='Face detection')

startTime = clock()
config = configparser.ConfigParser()
config.read('config.ini')

def checkPhotoDimensions(img):
    try:
        photoMinWidth = int(config['dimensions']['photoMinWidth'])
        photoMinHeight = int(config['dimensions']['photoMinHeight'])
        
        imageHeight = (img.shape[0])    
        imageWidth = (img.shape[1])
        if imageWidth >= photoMinWidth and imageHeight >= photoMinHeight:
            return True
        else:
            return False
    except:
        return False
                  
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
    
def checkBrightness(img):
    try:
        minBrightness = int(config['brightness']['minBrightness'])
        maxBrightness = int(config['brightness']['maxBrightness'])    
        meanBrightness = (np.mean(img))
#        print ("  Photo mean brightness: ", meanBrightness)

#        result = filters.exposure.adjust_gamma(img, 2)
#        print (result)
        
        if minBrightness <= meanBrightness <= maxBrightness:
            return True
        else:
            return False
    except:
        return ("error", False)

def checkOverExposure(img):
    a = histogram(img.ravel())
#    print (a[0])
#    print (a[0].sum())
#    print (a[1].sum())
#    b = np.hstack((a[0].normal(size=1000),a[0].normal(loc=5, scale=2, size=1000)))
#    plt.a(b,bins='auto')
    rng = histogram(img) #np.random.RandomState(10)  # deterministic random data
    a = np.hstack((rng[0]))#.normal(size=1000),rng[0]))#.normal(loc=5, scale=2, size=1000)))
    plt.hist(a, bins='auto')  # plt.hist passes it's arguments to np.histogram
    plt.title("Histogram with 'auto' bins")
    plt.show()    
        
def checkPhotoAge(data):
    try:
        allowedAge = float(config['photoAge']['allowedAge'])        
        tags = exifread.process_file(data, details=False, stop_tag='EXIF DateTimeOriginal')
#        kuupString = str(tags['EXIF DateTimeOriginal'])
#        dte = datetime.strptime(kuupString, '%Y:%m:%d %H:%M:%S')
        dte = datetime.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
        if ((datetime.date(datetime.now()) - datetime.date(dte)).days) >= allowedAge:
            return False
        else:
            return True
    except:
        return "No EXIF data"
        
def checkFaceCenterToImage(img,shape):
    try:
        axeMinCoeff = float(config['faceCenter']['axeMinCoeff'])
        axeMaxCoeff = float(config['faceCenter']['axeMaxCoeff'])    
        imageWidth = (len((img)[0]))
        axeCoeff = (imageWidth/shape.part(27).x) #nose upper point
        if axeMinCoeff <= axeCoeff <= axeMaxCoeff:
            return True
        else:
            return False
    except:
        return False


def checkFaceQuantity(dets):
    try:
        if len(dets) == 1:
            return True
        else:
            return False
    except:
        return False

def checkFaceVerticalAxe(shape, detection):
    try:
        maxTiltLimit = float(config['faceVerticality']['maxTiltLimit'])
        chinBottomPoint = shape.part(8).x # (l6ug)
        noseUpperPoint = shape.part(27).x #ninajuur
        faceAxe = abs(chinBottomPoint - noseUpperPoint)/detection.width()
        if faceAxe <= maxTiltLimit:
            return True
        else:
            return False
    except:
        return False            
        
def checkFaceStraight(shape):
    try:
        faceAssymmetryConstant = float(config['faceAssymmetry']['faceAssymmetryConstant'])    
        leftSideDistance = shape.part(28).x-shape.part(1).x #Distance betveen nose and left side
        rightSideDistance = shape.part(15).x - shape.part(28).x ##Distance betveen nose and right side
        faceWeight = shape.part(15).x - shape.part(1).x
        faceAssymmetry = abs(leftSideDistance - rightSideDistance)  
        faceStraightFactor = faceAssymmetry / faceWeight
        if faceStraightFactor <= faceAssymmetryConstant:
            return True
        else:
            return False
    except:
        return False

# height of 50–70% of the total vertical length of the photo
def checkEyesHeight(img,shape):
    try:
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
    except:
        return False            
        
def checkMouthClosed(shape, detection):
    try:
        mouthOpenLimit = float(config['mouthClosed']['mouthOpenLimit'])    
        upperLipY= shape.part(66).y
        lowerLipY= shape.part(62).y
        mouthOpenFactor= (upperLipY-lowerLipY)/detection.height()
    #    print (mouthOpenFactor)
        if mouthOpenFactor <= mouthOpenLimit:
            return True
        else:
            return False
    except:
        return False

#TODO Kuna silmade detekteerimine ei ole väga hea, siis see lahendus ei toimi.
def checkEyesOpen(shape, detection):
    try:
        return "Not checked yet"
    except:
        return False        

#TODO 
def checkRedEyes(shape, detection):
    try:
#    leftEyeRectangle = shape.part(37).y 
        return "Not checked yet"
    except:
        return False
 
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
        
        img1 = img[3:int(imageHeight*outsideRectangleHeight), 3:int(imageWidth*outsideRectangleWidth)]
        img2 = img[3:int(imageHeight*upperRectangleHeight), 3:int(imageWidth*upperRectangleWidth)]
        img3 = img[3:int(imageHeight*outsideRectangleHeight), imageWidth-int(imageWidth*outsideRectangleWidth):int(imageWidth-3)]
        img4 = img[3:int(imageHeight*upperRectangleHeight), imageWidth-int(imageWidth*upperRectangleWidth):imageWidth-3]
    
    #    segments_fz = felzenszwalb(img, scale=300, sigma=2.2, min_size=80)  #whole img
        segments_fz1 = felzenszwalb(img1, scale, sigma, min_size)
        segments_fz2 = felzenszwalb(img2, scale, sigma, min_size)
        segments_fz3 = felzenszwalb(img3, scale, sigma, min_size)
        segments_fz4 = felzenszwalb(img4, scale, sigma, min_size)
        
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
    except:
        return False
    
def checkFaceTooSmall(img, detection):
    try:
        faceSizeMinFactor = float(config['faceDimensions']['faceSizeMinFactor'])
        imageWidth = (len((img)[0]))
        faceSizeFactor = imageWidth/detection.width()
        if faceSizeFactor >= faceSizeMinFactor:
            return False
        else:
            return True
    except:
        return False
            
def checkFaceTooLarge(img, detection):
    try:
        faceSizeMaxFactor = float(config['faceDimensions']['faceSizeMaxFactor'])    
        imageWidth = (len((img)[0]))
        faceSizeFactor = imageWidth/detection.width()
        if faceSizeFactor <= faceSizeMaxFactor:
            return False
        else:
            return True
    except:
        return False

def runDetect(data):
    dir = os.path.dirname(__file__)
    predictor_path = os.path.join(dir, 'shape_predictor_68_face_landmarks.dat')
    result = Results()
    
#    faces_folder_path = os.path.join(dir,'images')
#    print (faces_folder_path)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
#    win = dlib.image_window()
    
#    win.clear_overlay()
#    win.set_image(img)        

    d2 = io.BytesIO(data)
    result.photoage = checkPhotoAge(d2)
    print ("Photo age is OK: {}".format(result.photoage))

    img = misc.imread(d2, False, 'RGB')
    d2.close()
                   
    result.dimensions = checkPhotoDimensions(img)
    print ("Photo minimal dimensions OK: {}".format(result.dimensions))
            
    result.color = is_color(img) #checkPhotoColor(img)
    print ("Photo is color: {}".format(result.color)) 
    
    result.brightness = checkBrightness(img)
    print ("Photo brightness is OK: {}".format(result.brightness))

#            checkOverExposure(img)
    
    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    
    result.background = checkBackgroundObjects(img)
    print ("Background correct: {}".format(result.background))
   
    result.facequantity = checkFaceQuantity(dets)
    print ("Face quantity: {}".format(result.facequantity))

    for k, d in enumerate(dets): 
        print("\nDetected face No: {}".format(k))
        # Get the landmarks/parts for the face in box d.
        shape = predictor(img, d)

        result.facecenter = checkFaceCenterToImage(img,shape)
        print ("Face centering: {}".format(result.facecenter))
        
        result.vertical = checkFaceVerticalAxe(shape, d)
        print ("Face verticality: {}".format(result.vertical))
     
        result.straight = checkFaceStraight(shape)
        print ("Face is straight: {}".format(result.straight))
        
        result.eyesheight = checkEyesHeight(img,shape)
        print ("Eyes height correct: {}".format(result.eyesheight))
        
        result.mouthclosed = checkMouthClosed(shape, d)
        print ("Mouth is closed: {}".format(result.mouthclosed))
        
        result.facesmall = checkFaceTooSmall(img,d)
        print ("Face not small: {}".format(result.facesmall))        
        
        result.facelarge = checkFaceTooLarge(img,d)
        print ("Face not large: {}".format(result.facelarge)) 
        
#        eyesOpendB = checkEyesOpen(shape, d)
#        print ("Eyes are open: {}".format(eyesOpendB))
        
#        redEyesB = checkRedEyes(shape, d)
#        print ("Red eyes not detected: {}".format(redEyesB))
        
        # Draw the face landmarks on the screen.
#                win.add_overlay(shape)
#            win.add_overlay(dets)    
    #input("Press Enter to continue...")   
    if (result.background == False or result.brightness == False or
        result.color == False or result.dimensions == False or 
        result.eyesheight == False or result.facecenter == False or
        result.facelarge == False or result.facequantity == False or 
        result.facesmall == False or result.mouthclosed == False or
        result.photoage == False or result.straight == False or 
        result.vertical == False): 
        result.result = False
                
    return result.__dict__

def main():
    dir = os.path.dirname(__file__)
    for f in glob.glob(os.path.join(dir, 'images',"*.*")):
        extension = os.path.splitext(f)[1]
        if extension == ".jpg" or extension == ".jpeg" or extension == ".png" or extension == ".tif" or extension == ".tiff" or extension == ".bmp":
        #    print(f)
        #for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
            print("\nProcessing file: {}".format(f))
"""
            fi = open(f, "rb")
            data = fi.read()
            b64 = base64.b64encode(data)
            f2 = open("b64test.txt", "wb")
            f2.write(b64)
            fi.close()
            f2.close()
"""         
#            img = misc.imread(d2, False, 'RGB')
#            runDetect(data)

resource_fields = api.model('Resource', {
    'base64': fields.String,
})

@ns.route('/start')
class Detection(Resource):
    @ns.doc('Process image')
    @api.expect(resource_fields)
    def post(self):
        json_data = request.get_json(force=True)
        b64 = json_data['base64']
        data = base64.b64decode(b64)
        return runDetect(data)
    
if __name__ == '__main__':
    app.run() #Comment this line in, for running on localhost
    #app.run(host="0.0.0.0", port=int("80"),)
    main()
    timeLeft = (clock() - startTime) #arvutab kulunud aja
    print("Time left: {} sec".format(timeLeft))
