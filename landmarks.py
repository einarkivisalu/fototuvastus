#import sys
import os
import dlib
import glob
import numpy as np
from skimage import io, color
#from skimage.filters import gaussian
#from skimage.segmentation import active_contour

def checkPhotoDimensions(img):
    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    if imageWidth >= 600 and imageHeight >= 750:
        return True
    else:
        return False
           
def is_color(img):
    r1,g1,b1 = 0,0,0
    if len(img.shape)==2:
        return False
    else:
        imageHeight = (img.shape[0])
        imageWidth = (img.shape[1])
        for i in range(imageHeight):
            for j in range(imageWidth):
                r,g,b = img[i,j]
                r1 += r
                g1 += g
                b1 += b
        if r1 == g1 == b1:            
            return False
    return True
        
        
def checkFaceCenterToImage(img,shape):
    imageWidth = (len((img)[0]))
    axeCoeff = (imageWidth/shape.part(27).x) #nose upper point
    if 1.7 <= axeCoeff <=2.3:
        return True
    else:
        return False

def checkFaceQuantity(dets):
    if len(dets) == 1:
        return True
    else:
        return False

def checkFaceVerticalAxe(shape, detection):
    chinBottomPoint = shape.part(8).x # (l6ug)
    noseUpperPoint = shape.part(27).x
    faceAxe = abs(chinBottomPoint - noseUpperPoint)/detection.width()
    if faceAxe <= 0.05:
        return True
    else:
        return False
        
def checkFaceStraight(shape):
    leftSideDistance = shape.part(28).x-shape.part(1).x #Distance betveen nose and left side
    rightSideDistance = shape.part(15).x - shape.part(28).x ##Distance betveen nose and right side
    faceWeight = shape.part(15).x - shape.part(1).x
    faceAssymmetry = abs(leftSideDistance - rightSideDistance)
    faceAssymmetryConstant = 0.15    
    faceStraightFactor = faceAssymmetry / faceWeight
    if faceStraightFactor <= faceAssymmetryConstant:
        return True
    else:
        return False
    return "Not checked yet"

# height of 50–70% of the total vertical length of the photo
def checkEyesHeight(img,shape,detection):
    leftEyeLeftPoint = shape.part(36).y
    rightEyeRightPoint = shape.part(45).y
    eyesHeightLine = (leftEyeLeftPoint + rightEyeRightPoint)/2
    imageHeight = (img.shape[0])    
    eyesHeightFactor = (1-eyesHeightLine/imageHeight)
    if 0.5 <= eyesHeightFactor <= 0.7:
        return True
    else:
        return False
    
        
def checkMouthClosed(shape, detection):
    upperLipY= shape.part(66).y
    lowerLipY= shape.part(62).y
    mouthOpenFactor= (upperLipY-lowerLipY)/detection.height()
#    print (mouthOpenFactor)
    if mouthOpenFactor <= 0.02:
        return True
    else:
        return False

#TODO Kuna silmade detekteerimine ei ole väga hea, siis see lahendus ei toimi.
def checkEyesOpen(shape, detection):
    """    leftEyeUpperOuterY = shape.part(37).y
    leftEyeUpperInnerY = shape.part(38).y
    leftEyeUpperMidY=(leftEyeUpperOuterY+leftEyeUpperInnerY)/2
    leftEyeLowerOuterY = shape.part(41).y
    leftEyeLowerInnerY = shape.part(40).y
    leftEyeLowerMidY=(leftEyeLowerOuterY+leftEyeLowerInnerY)/2
    leftEyeOpenFactor= (leftEyeLowerInnerY - leftEyeUpperInnerY)/detection.height()
#    print("leftEyeOpenFactor: ", leftEyeOpenFactor)    
    leftEyeOpenFactor2= (leftEyeLowerMidY - leftEyeUpperMidY)/detection.height()
#    print("leftEyeOpenFactor2: ", leftEyeOpenFactor2)
    rightEyeUpperOuterY = shape.part(44).y
    rightEyeUpperInnerY = shape.part(43).y
    rightEyeUpperMidY=(leftEyeUpperOuterY+leftEyeUpperInnerY)/2
    rightEyeLowerOuterY = shape.part(46).y
    rightEyeLowerInnerY = shape.part(47).y
    rightEyeLowerMidY=(rightEyeLowerOuterY+rightEyeLowerInnerY)/2
    rightEyeOpenFactor= (rightEyeLowerMidY - rightEyeUpperMidY)/detection.height()
#    print("rightEyeOpenFactor: ", rightEyeOpenFactor)
#    rightEyeOpenFactor= (rightEyeLowerY - rightEyeUpperY)/detection.height()    
#    print("rightEyeOpenFactor: ", rightEyeOpenFactor)
#    if rightEyeOpenFactor <= 0.02:
#        return True
#    else:
            return False"""
    return "Not checked yet"

#TODO
def checkRedEyes(shape, detection):
#    leftEyeRectangle = shape.part(37).y 
    return "Not checked yet"

#TODO    
def checkExtraObjects(img,shape,detection): 

    imageHeight = (img.shape[0])    
    imageWidth = (img.shape[1])
    
    s = np.linspace(0, 2*np.pi, 400)
    x = imageWidth/2 + imageWidth/2.3*np.cos(s)
    y = imageHeight/2.1 + imageHeight/2.1*np.sin(s)
    init = np.array([x, y]).T
                              
#    print("\nImage: Width: {} Height: {}".format(imageWidth, imageHeight))
#    print("Detection: Left: {} Top: {} Right: {} Bottom: {}".format(detection.left(), detection.top(), detection.right(), detection.bottom()))
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
    
    PhotoDimensionsB = checkPhotoDimensions(img)
    print ("Photo minimal dimensions OK: {}".format(PhotoDimensionsB))
    
    PhotoColorityB = is_color(img) #checkPhotoColor(img)
    print ("Photo is color: {}".format(PhotoColorityB))    

    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets): 
        print("\nDetection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
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
        
        eyesHeightB =checkEyesHeight(img,shape,d)
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

        extraObjectsOnPictureB= checkExtraObjects(img, shape, d)
        print ("Extra objects not detected: {}".format(extraObjectsOnPictureB))
        
#        rects = []
#        dlib.find_candidate_object_locations(img, rects, min_size=10000)       
#        print("number of rectangles found {}".format(len(rects))) 
#        for k, d in enumerate(rects):
#            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
#            win.add_overlay(rects[k])

        # Draw the face landmarks on the screen.
        win.add_overlay(shape) 
    det2 = dlib.rectangle()
    det2.top = 30
    det2.bottom = 80
    det2.left = 30
    det2.right = 80
    
    win.add_overlay(det2)
    win.add_overlay(dets)    
    input("Press Enter to continue...")