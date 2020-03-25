## This is the abstract class that the students should implement  

from modesEnum import Modes
import numpy as np
import cv2 as cv
class ImageModel():

    """
    A class that represents the ImageModel"
    """

    # def __init__(self):
        # pass

    def __init__(self, imgPath: str):
        self.imgPath = imgPath
        ###
        # ALL the following properties should be assigned correctly after reading imgPath 
        ###
        self.imgByte = cv.imread(self.imgPath, cv.IMREAD_GRAYSCALE)
        self.dft = cv.dft(np.float32(self.imgByte), flags=cv.DFT_COMPLEX_OUTPUT)
        self.real = self.dft[:, :, 0]
        self.imaginary = self.dft[:, :, 1]
        self.magnitude = np.abs(self.dft[:, :, 0] + 1j * self.dft[:, :, 1])
        self.phase = np.angle(self.dft[:, :, 0] + 1j * self.dft[:, :, 1])

    def mix(self, imageToBeMixed: 'ImageModel', magnitudeOrRealRatio: float, phaesOrImaginaryRatio: float, mode: 'Modes') -> np.ndarray:
        """
        a function that takes ImageModel object mag ratio, phase ration 
        """
        ### 
        # implement this function
        ###
        if mode == Modes.magnitudeAndPhase:
            mix = (
                (magnitudeOrRealRatio * self.magnitude) + ((1 - magnitudeOrRealRatio) * imageToBeMixed.magnitude)
            ) * np.exp(
                1j
                * (
                    ((phaesOrImaginaryRatio) * self.phase)
                    + ((1 - phaesOrImaginaryRatio) * imageToBeMixed.phase)
                )
            )

            img = np.fft.ifft2(mix)
            return np.real(img)
        elif mode == Modes.realAndImaginary:
            mix = (
                (magnitudeOrRealRatio * self.real) + ((1 - magnitudeOrRealRatio) * imageToBeMixed.real)
            ) + 1j * (
                ((phaesOrImaginaryRatio) * self.imaginary) + ((1 - phaesOrImaginaryRatio) * imageToBeMixed.imaginary)
            )
            img = np.fft.ifft2(mix)
            return np.real(img)
        else:
            print("error in mixer")

    def showImg(self,widget):
        widget.show()
        widget.setImage(self.imgByte.T)
        self.__scaleImage(widget, self.imgByte.shape)

    def __scaleImage(self,widget,shape):
        widget.view.setAspectLocked(False)
        widget.view.setRange(xRange=[0, shape[1]], yRange=[0, shape[0]], padding=0)
