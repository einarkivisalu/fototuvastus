#import sys
import os
import dlib
import glob
from skimage import io

def checkFaceCenterToImage(img,shape,detection):
    imageWidth = (len((img)[0]))
#    print (detection.width()) #face rectangle width
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
        
def checkMouthClosed(shape, detection):
    upperLipY= shape.part(66).y
    lowerLipY= shape.part(62).y
    mouthOpenFactor= (upperLipY-lowerLipY)/detection.height()
#    print (mouthOpenFactor)
    if mouthOpenFactor <= 0.02:
        return True
    else:
        return False

#TODO        
def checkEyesOpen(shape, detection):
    leftEyeUpperOuterY = shape.part(37).y
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
#        return False
    return "Not checked yet"

#TODO
def checkRedEyes(shape, detection):
#    leftEyeRectangle = shape.part(37).y 
    return "Not checked yet"

#TODO    
def checkExtraObjects(img, detection):    
    return "Not checked yet"
    
def checkFaceTooSmall(img, detection):
    imageWidth = (len((img)[0]))
    imagesizeFactor = imageWidth/detection.width()
#    print ("imagesizeFactor: ",imagesizeFactor)
    if imagesizeFactor >=3:
        return True
    else:
        return False
        
def checkFaceTooLarge(img, detection):
    imageWidth = (len((img)[0]))
    imagesizeFactor = imageWidth/detection.width()
#    print ("imagesizeFactor: ",imagesizeFactor)
    if imagesizeFactor <=1.5:
        return True
    else:
        return False

dir = os.path.dirname(__file__)
print (dir)
predictor_path = os.path.join(dir, 'shape_predictor_68_face_landmarks.dat')

faces_folder_path = os.path.join(dir,'images')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
win = dlib.image_window()

for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("\nProcessing file: {}".format(f))
    img = io.imread(f)

    win.clear_overlay()
    win.set_image(img)

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
        
        faceCenterB =checkFaceCenterToImage(img,shape,d)
        print ("Face centering: {}".format(faceCenterB))
        
        faceVerticalAxeB = checkFaceVerticalAxe(shape, d)
        print ("Face verticality: {}".format(faceVerticalAxeB))
        
        mouthClosedB = checkMouthClosed(shape, d)
        print ("Mouth is closed: {}".format(mouthClosedB))
        
        faceTooSmallB= checkFaceTooSmall(img,d)
        print ("Face too small: {}".format(faceTooSmallB))        
        
        faceTooLargeB= checkFaceTooLarge(img,d)
        print ("Face too large: {}".format(faceTooLargeB)) 
        
        eyesOpendB = checkEyesOpen(shape, d)
        print ("Eyes are open: {}".format(eyesOpendB))
        
        redEyesB = checkRedEyes(shape, d)
        print ("Red eyes detected: {}".format(redEyesB))

        extraObjectsOnPictureB= checkExtraObjects(shape, d)
        print ("Extra objects detected: {}".format(redEyesB))
        
        rects = []
        dlib.find_candidate_object_locations(img, rects, min_size=10000)       
#        print("number of rectangles found {}".format(len(rects))) 
#        for k, d in enumerate(rects):
#            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
#            win.add_overlay(rects[k])

        # Draw the face landmarks on the screen.
        win.add_overlay(shape)        
    win.add_overlay(dets)    
    input("Press Enter to continue...")