import unittest 
import dlib

from skimage import io, color
from photoQualityChecker import *

class TestMethods(unittest.TestCase):

    @classmethod    
    def setUpClass(self):
        print("setup class")
        self.img = io.imread("images/Test/002.jpg")
        self.img2 = io.imread("images/Test/2017-03-13 11.05.44 1469482145957050217_selfie.jpg")
        self.imgHen = io.imread("images/Test/hendrix2.jpg")
        self.predictor_path = os.path.join(os.path.dirname(__file__), 'shape_predictor_68_face_landmarks.dat')
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.predictor_path)
    
    def test_checkPhotoDimensionsFalse(self):
        result = checkPhotoDimensions(self.img)
        self.assertFalse(result)
        
    def test_checkPhotoDimensionsTrue(self):
        img3 = io.imread("images/Test/2010_0213canada0002fx.jpg ")
        result = checkPhotoDimensions(img3)
        self.assertTrue(result)

    def test_is_colorTrue(self):
        result = is_color(self.img)
        self.assertTrue(result)

    def test_is_colorFalse(self):
        img3 = io.imread("images/moved/hendrix2.jpg")
        result = is_color(self.imgHen)
        self.assertFalse(result)

#   vaja on 1 kanaliga must-valget pilti       
    def test_is_colorFalse2(self):
        img3 = io.imread("images/Test/hendrix.jpg")
        result = is_color(img3)
        self.assertFalse(result)

    def test_checkFaceQuantityTrue(self):
        self.assertTrue(checkFaceQuantity(self.detector(self.img, 1)))

    def test_checkFaceQuantityFalse(self):
        img3 = io.imread("images/Test/ClosedEye.jpg");
        self.assertTrue(checkFaceQuantity(self.detector(img3, 1)))


    def test_checkFaceCenterToImageTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkFaceCenterToImage(self.img, self.predictor(self.img, d))
        self.assertTrue(result)

    def test_checkFaceCenterToImageFalse(self):
        dets = self.detector(self.img2, 1)
        for k, d in enumerate(dets):
           result = checkFaceCenterToImage(self.img2, self.predictor(self.img2, d))
        self.assertFalse(result)

    def test_checkFaceVerticalAxeTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkFaceVerticalAxe(self.predictor(self.img, d), d)
        self.assertTrue(result)

    def test_checkFaceVerticalAxeFalse(self):
        dets = self.detector(self.img2, 1)
        for k, d in enumerate(dets):
           result = checkFaceVerticalAxe(self.predictor(self.img2, d), d)
        self.assertFalse(result)

    def test_checkFaceStraightTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkFaceStraight(self.predictor(self.img, d))
        self.assertTrue(result)

    def test_checkFaceStraightFalse(self):
        dets = self.detector(self.img2, 1)
        for k, d in enumerate(dets):
           result = checkFaceStraight(self.predictor(self.img2, d))
        self.assertFalse(result)
 
    def test_checkEyesHeightTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkEyesHeight(self.img, self.predictor(self.img, d))
        self.assertTrue(result)

    def test_checkEyesHeightFalse(self):
        dets = self.detector(self.imgHen, 1)
        for k, d in enumerate(dets):
           result = checkEyesHeight(self.imgHen, self.predictor(self.imgHen, d))
        self.assertFalse(result)
        
    def test_checkMouthClosedTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkMouthClosed(self.predictor(self.img, d), d)
        self.assertTrue(result)

    def test_checkMouthClosedFalse(self):
        img3 = io.imread("images/Test/red_eye.jpg")
        dets = self.detector(img3, 1)
        for k, d in enumerate(dets):
           result = checkMouthClosed(self.predictor(img3, d), d)
        self.assertFalse(result)

    def test_checkFaceTooSmallTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkFaceTooSmall(self.img, d)
        self.assertTrue(result)
        
    def test_checkFaceTooSmallFalse(self):
        dets = self.detector(self.imgHen, 1)
        for k, d in enumerate(dets):
           result = checkFaceTooSmall(self.imgHen, d)
        self.assertFalse(result)
        
    def test_checkFaceTooLargeTrue(self):
        dets = self.detector(self.img, 1)
        for k, d in enumerate(dets):
           result = checkFaceTooLarge(self.img, d)
        self.assertTrue(result)
        
    def test_checkFaceTooLargeFalse(self):
        img3 = io.imread("images/Test/pO4QXG7RJAYK.jpg")
        dets = self.detector(img3, 1)
        for k, d in enumerate(dets):
           result = checkFaceTooLarge(img3, d)
        self.assertFalse(result)
    
    def test_checkBrightnessTrue(self):
        self.assertTrue(checkBrightness(self.img))
        
    def test_checkBrightnessFalse(self):
        img3 = io.imread("images/Test/overexposed2.jpg")
        self.assertFalse(checkBrightness(img3))
        
    def test_checkBackgroundObjectsTrue(self):
        self.assertTrue(checkBackgroundObjects(self.img))
        
    def test_checkBackgroundObjectsFalse(self):
        img3 = io.imread("images/Test/sester.jpg")
        self.assertFalse(checkBackgroundObjects(img3))
        
if __name__ == '__main__':
    unittest.main()