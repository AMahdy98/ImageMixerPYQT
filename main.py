import sys
import numpy as np
import cv2 as cv
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import imageMixerUI as mw
from imageModel import ImageModel
from modesEnum import Modes
import logging

# logger config.
logging.basicConfig(
    filename="logs.log",
    format="%(asctime)s %(message)s",
    filemode="w",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class mixerApp(mw.Ui_MainWindow):
    def __init__(self, starterWindow):
        """
        Main loop of the UI
        :param mainWindow: QMainWindow Object
        """
        super(mixerApp, self).setupUi(starterWindow)
        self.images = [ImageModel, ImageModel]
        # Flags for loading fun.
        self.img1Loaded = False
        self.img2Loaded = False
        self.__epsilon = 10 ** -8

        self.modes = [
            self.imgMag,
            self.imgPhase,
            self.imgReal,
            self.imgImaginry,
            self.uniMag,
            self.uniPhase,
        ]
        # Widgets encapsulations
        self.img1Widgets = [self.img1Original, self.img1Component]
        self.img2Widgets = [self.img2Original, self.img2Component]
        self.outputWidgets = [self.output1Img, self.output2Img]
        self.comboChoice = [self.comp1ChoiceComboBox, self.comp2ChoiceComboBox]
        # Hide unnecessery btns in imageView widget
        for encap in zip(self.img1Widgets, self.img2Widgets, self.outputWidgets):
            for widget in encap:
                widget.ui.histogram.hide()
                widget.ui.roiPlot.hide()
                widget.ui.roiBtn.hide()
                widget.ui.menuBtn.hide()

        # Connections
        self.actionLoadImage1.triggered.connect(lambda: self.loadImg(1))
        self.actionLoadImage2.triggered.connect(lambda: self.loadImg(2))
        self.img1ComboBox.currentIndexChanged.connect(
            lambda: self.modeCheck(
                self.img1ComboBox.currentIndex(), self.img1Widgets[1], 0
            )
        )
        self.img2ComboBox.currentIndexChanged.connect(
            lambda: self.modeCheck(
                self.img2ComboBox.currentIndex(), self.img2Widgets[1], 1
            )
        )
        self.comp1HorizontalSlider.valueChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
        )
        self.comp2HorizontalSlider.valueChanged.connect(
            lambda: self.comboChecker(self.comp2ChoiceComboBox.currentIndex(), 1)
        )
        self.comp1CompoBox.currentIndexChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
        )
        self.comp2CompoBox.currentIndexChanged.connect(
            lambda: self.comboChecker(self.comp2ChoiceComboBox.currentIndex(), 1)
        )
        self.comp1ChoiceComboBox.currentIndexChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
        )
        self.comp2ChoiceComboBox.currentIndexChanged.connect(
            lambda: self.comboChecker(self.comp2ChoiceComboBox.currentIndex(), 1)
        )
        self.outputComboBox.currentIndexChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
        )

    def autoSelect(self, index):
        """
            Adds 1 if even number and substracts 1 if odd number
        """
        if index % 2 == 0:
            return index + 1
        else:
            return index - 1

    def comboChecker(self, choice, id):
        """
            Check for mode and auto select from other comboBox
        """
        # Check selected component
        if choice in [2, 3]:  # Real or imaginary components
            mode = Modes.realAndImaginary
            self.comboChoice[self.autoSelect(id)].setCurrentIndex(
                self.autoSelect(choice)
            )
        else:  # phase components
            mode = Modes.magnitudeAndPhase
            otherChoice = self.comboChoice[self.autoSelect(id)].currentIndex()
            if (choice in [0, 4]) and (otherChoice in [0, 2, 3, 4]):
                self.comboChoice[self.autoSelect(id)].setCurrentIndex(1)
            if (choice in [1, 5]) and (otherChoice in [1, 2, 3, 5]):
                self.comboChoice[self.autoSelect(id)].setCurrentIndex(0)
        # Call mixer initializer
        self.mixCheck(mode)

    def mixCheck(self, mode):
        """
            Pre-Mixer steps
        """
        # getting necessery values
        w1 = self.comp1HorizontalSlider.value() / 100
        w2 = self.comp2HorizontalSlider.value() / 100
        choice1 = self.comp1CompoBox.currentIndex()
        choice2 = self.comp2CompoBox.currentIndex()
        component1 = self.comp1ChoiceComboBox.currentIndex()
        component2 = self.comp2ChoiceComboBox.currentIndex()

        # weight check
        if choice1 == 1:
            w1 = 1 - w1
        if choice2 == 1:
            w2 = 1 - w2

        print("Mixing")
        # Checking for unimag or uni phase mode (yep bad code)
        if component1 in [4, 5]:
            if component1 == 4:
                temp = self.images[choice1].magnitude
                self.images[choice1].magnitude = self.uniMag(choice1)
                output = self.images[0].mix(self.images[1], float(w1), float(w2), mode)
                self.images[choice1].magnitude = temp
            else:
                temp = self.images[choice1].phase
                self.images[choice1].phase = self.uniPhase(choice1)
                output = self.images[0].mix(self.images[1], float(w1), float(w2), mode)
                self.images[choice1].phase = temp
        elif component2 in [4, 5]:
            if component2 == 4:
                temp = self.images[choice2].magnitude
                self.images[choice2].magnitude = self.uniMag(choice2)
                output = self.images[0].mix(self.images[1], float(w1), float(w2), mode)
                self.images[choice2].magnitude = temp
            else:
                temp = self.images[choice2].phase
                self.images[choice2].phase = self.uniPhase(choice2)
                output = self.images[0].mix(self.images[1], float(w1), float(w2), mode)
                self.images[choice2].phase = temp
        else:
            output = self.images[0].mix(self.images[1], float(w1), float(w2), mode)

        # Check if mixing happend then show image
        if type(output) != bool :
            self.showImg(self.outputWidgets[self.outputComboBox.currentIndex()], output)

    def modeCheck(self, mode, widget, data):
        print(mode)
        logger.debug("Mode changed to index : %d", mode)
        image = self.modes[mode](data)
        self.showImg(widget, image)

    def showImg(self, widget, image):
        logger.debug("Showing Image wit shape : %s", str(image.shape))
        widget.show()
        widget.setImage(image.T)
        self.scaleImage(widget, image.shape)

    def uniMag(self, dft):
        logger.debug("Getting uni Magnitude")
        return np.ones(self.images[dft].magnitude.shape)

    def uniPhase(self, dft):
        logger.debug("Getting uni Phase")
        return np.zeros(self.images[dft].phase.shape)

    def imgReal(self, dft):
        logger.debug("Getting Real component for showing it")
        return 20 * np.log(self.images[dft].magnitude + self.__epsilon)

    def imgImaginry(self, dft):
        logger.debug("Getting Imaginary component for showing it")
        return 20 * np.log(self.images[dft].imaginary + self.__epsilon)

    def imgPhase(self, dft):
        logger.debug("Getting Phase for showing it")
        return self.images[dft].phase

    def imgMag(self, dft):
        """
        Takes image and returns magnitude
        """
        logger.debug("Getting Magnitude for showing it")
        dftShift = np.fft.fftshift(self.images[dft].magnitude)
        magSpectrum = 20 * np.log(dftShift)
        return magSpectrum

    def loadImg(self, id):
        """
        Load the image and add it to desired obiject(id)
        """
        # Open file
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.fileName, self.format = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Load Image",
            "",
            "Images (*.png *.xpm *.jpg);;",
            options=QtWidgets.QFileDialog.DontUseNativeDialog,
        )

        # if (cancel loading)
        if self.fileName == "":
            pass
        else:
            if id == 1:
                logger.debug("Load Image 1 from path : %s", self.fileName)
                self.images[0] = ImageModel(self.fileName)
                self.images[0].showImg(self.img1Widgets[0])
                self.img1ComboBox.setEnabled(True)
                self.modeCheck(self.img1ComboBox.currentIndex(), self.img1Widgets[1], 0)
                # Enable Mixer
                self.img1Loaded = True
                self.mixerLayout.setEnabled(self.img1Loaded and self.img2Loaded)
            elif id == 2:
                logger.debug("Load Image 2 from path : %s", self.fileName)
                self.images[1] = ImageModel(self.fileName)
                self.images[1].showImg(self.img2Widgets[0])
                self.img2ComboBox.setEnabled(True)
                self.modeCheck(self.img2ComboBox.currentIndex(), self.img2Widgets[1], 1)
                # Enable Mixer
                self.img2Loaded = True
                self.mixerLayout.setEnabled(self.img1Loaded and self.img2Loaded)
            else:
                logger.error("erorr during loading")
                print("load error in id")

    def scaleImage(self, widget, shape):
        widget.view.setAspectLocked(False)
        widget.view.setRange(xRange=[0, shape[1]], yRange=[0, shape[0]], padding=0)


def main():
    """
    the application startup functions
    :return:
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Image Mixer")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    MainWindow = QtWidgets.QMainWindow()
    ui = mixerApp(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
