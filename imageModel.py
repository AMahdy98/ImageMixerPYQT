## This is the abstract class that the students should implement

from modesEnum import Modes
import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QMessageBox
import logging

class ImageModel:

    """
    A class that represents the ImageModel"
    """

    def __init__(self):
        pass

    def __init__(self, imgPath: str):
        self.imgPath = imgPath
        ###
        # ALL the following properties should be assigned correctly after reading imgPath
        ###
        self.imgByte = cv.imread(self.imgPath, cv.IMREAD_GRAYSCALE)
        self.dft = cv.dft(np.float32(self.imgByte), flags=cv.DFT_COMPLEX_OUTPUT)
        self.real = self.dft[:, :, 0]
        self.imaginary = self.dft[:, :, 1]
        self.dft = self.dft[:, :, 0] + 1j * self.dft[:, :, 1]
        self.magnitude = np.abs(self.dft)
        self.phase = np.angle(self.dft)
        logging.debug("Initilaizing ImageModule")

    def mix(self, imageToBeMixed: "ImageModel", magnitudeOrRealRatio: float, phaesOrImaginaryRatio: float, mode: "Modes") -> np.ndarray:
        """
        a function that takes ImageModel object mag ratio, phase ration 
        """
        ###
        # implement this function
        ###
        if self.imgByte.shape != imageToBeMixed.imgByte.shape:
            logging.debug("can't mix different sizes")
            self.showMessage("Warning", "You can't mix images with different sizes , Please load an image with the same size", QMessageBox.Ok, QMessageBox.Warning)
            return False
        else:
            if mode == Modes.magnitudeAndPhase:
                logging.debug("Mixing in Mag and Phase mode")
                mix = (
                (magnitudeOrRealRatio * self.magnitude)
                + ((1 - magnitudeOrRealRatio) * imageToBeMixed.magnitude)
                ) * np.exp(
                    1j
                    * (
                        ((phaesOrImaginaryRatio) * self.phase)
                        + ((1 - phaesOrImaginaryRatio) * imageToBeMixed.phase)
                    )
                )

                img = np.fft.ifft2(mix)
                return np.abs(img)
            elif mode == Modes.realAndImaginary:
                logging.debug("Mixing in Complex mode")
                mix = (
                    (magnitudeOrRealRatio * self.real)
                    + ((1 - magnitudeOrRealRatio) * imageToBeMixed.real)
                ) + 1j * (
                    ((phaesOrImaginaryRatio) * self.imaginary)
                    + ((1 - phaesOrImaginaryRatio) * imageToBeMixed.imaginary)
                )
                img = np.fft.ifft2(mix)
                return np.abs(img)
            else:
                pass

    def showImg(self, widget):
        logging.debug("Showing image from ImageModule")
        widget.show()
        widget.setImage(self.imgByte.T)
        self.__scaleImage(widget, self.imgByte.shape)

    def __scaleImage(self, widget, shape):
        widget.view.setAspectLocked(False)
        widget.view.setRange(xRange=[0, shape[1]], yRange=[0, shape[0]], padding=0)
    
    def showMessage(self, header,message, button, icon):
        msg = QMessageBox()
        msg.setWindowTitle(header)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(button)
        x = msg.exec_()
