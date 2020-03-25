import sys
import numpy as np
import cv2 as cv
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import imageMixerUI as mw
from imageModel import ImageModel
from modesEnum import Modes

class mixerApp(mw.Ui_MainWindow):
    def __init__(self, starterWindow):
        """
        Main loop of the UI
        :param mainWindow: QMainWindow Object
        """

        super(mixerApp, self).setupUi(starterWindow)
        self.images = [ImageModel ,ImageModel]

        self.img1 = ...
        self.img2 = ...
        self.img1Loaded = False
        self.img2Loaded = False
        self.fouriers = [..., ...]
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
                self.img1ComboBox.currentIndex(), self.img1Widgets[1], 0 #self.fouriers[0]
            )
        )
        self.img2ComboBox.currentIndexChanged.connect(
            lambda: self.modeCheck(
                self.img2ComboBox.currentIndex(), self.img2Widgets[1],1 # self.fouriers[1]
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
        if index % 2 == 0:
            return index + 1
        else:
            return index - 1

    def comboChecker(self, choice, id):
        # component1 = self.comp1ChoiceComboBox.currentIndex()
        # component2 = self.comp2ChoiceComboBox.currentIndex()
        if choice in [2, 3]:
            mode = Modes.realAndImaginary
            #  mode = "cmplx"
            self.comboChoice[self.autoSelect(id)].setCurrentIndex(
                self.autoSelect(choice)
            )
        else:
            mode = Modes.magnitudeAndPhase
            # mode = "phase"
            otherChoice = self.comboChoice[self.autoSelect(id)].currentIndex()
            if (choice in [0, 4]) and (otherChoice in [0, 2, 3, 4]):
                self.comboChoice[self.autoSelect(id)].setCurrentIndex(1)
            if (choice in [1, 5]) and (otherChoice in [1, 2, 3, 5]):
                self.comboChoice[self.autoSelect(id)].setCurrentIndex(0)

        self.mixCheck(mode)

    def mixCheck(self, mode):
        w1 = self.comp1HorizontalSlider.value() / 100
        w2 = self.comp2HorizontalSlider.value() / 100
        choice1 = self.comp1CompoBox.currentIndex()
        choice2 = self.comp2CompoBox.currentIndex()
        component1 = self.comp1ChoiceComboBox.currentIndex()
        component2 = self.comp2ChoiceComboBox.currentIndex()
        img1Components = [..., ...]
        img2Components = [..., ...]
        # weight check
        if choice1 == 1:
            w1 = 1 - w1
        if choice2 == 1:
            w2 = 1 - w2
        # # Get components
        # img1Components[component1 % 2] = self.modes[component1](
        #     self.fouriers[0], "mixer"
        # )
        # img1Components[component2 % 2] = self.modes[component2](
        #     self.fouriers[0], "mixer"
        # )
        # img2Components[component1 % 2] = self.modes[component1](
        #     self.fouriers[1], "mixer"
        # )
        # img2Components[component2 % 2] = self.modes[component2](
        #     self.fouriers[1], "mixer"
        # )
        print("Mixing")
        output = self.images[0].mix(self.images[1],float(w1),float(w2),mode)
        # output = self.mixer(w1, w2, mode, img1Components, img2Components)
        self.showImg(self.outputWidgets[self.outputComboBox.currentIndex()], output)

    def mixer(self, weight1, weight2, mode, img1Components, img2Components):
        if mode == "phase":
            print("phase mixer")
            mix = (
                (weight1 * img1Components[0]) + ((1 - weight1) * img2Components[0])
            ) * np.exp(
                1j
                * (
                    ((weight2) * img1Components[1])
                    + ((1 - weight2) * img2Components[1])
                )
            )

            img = np.fft.ifft2(mix)
            # img = cv.idft(np.float32(mix))
            return np.real(img)
        elif mode == "cmplx":
            print("cmplx mixer")
            mix = (
                (weight1 * img1Components[0]) + ((1 - weight1) * img2Components[0])
            ) + 1j * (
                ((weight2) * img1Components[1]) + ((1 - weight2) * img2Components[1])
            )
            img = np.fft.ifft2(mix)
            # img = cv.idft(np.float32(mix))
            return np.real(img)
        else:
            print("error in mixer")

    def modeCheck(self, mode, widget, data , image=None):
        print(mode)
        image = self.modes[mode](data)
        self.showImg(widget, image)

    def showImg(self, widget, image):
        print(image.shape)
        widget.show()
        widget.setImage(image.T)
        self.scaleImage(widget, image.shape)

    def uniMag(self, dft, mode = "mix"):
        # return np.ones(dft[:, :, 0].shape)
        return np.ones(self.images[dft].magnitude.shape)

    def uniPhase(self, dft, mode = "mix"):
        # return np.zeros(dft[:, :, 1].shape)
        return np.zeros(self.images[dft].phase.shape)

    def imgReal(self, dft, mode="show"):
        print("Real")
        if mode == "mixer":
            pass
            # return dft[:, :, 0]
        else:
            return 20 *np.log(self.images[dft].magnitude + self.__epsilon)
            # return 20 * np.log(dft[:, :, 0] + self.__epsilon)

    def imgImaginry(self, dft, mode="show"):
        print("Imaginry")
        if mode == "mixer":
            # return dft[:, :, 1]
            pass
        else:
            return 20 * np.log(self.images[dft].imaginary + self.__epsilon)
            # return 20 * np.log(dft[:, :, 1] + self.__epsilon)

    def imgPhase(self, dft, mode=None):
        print("Phase")
        # print(dft[:,:,0])
        # print(dft[:,:,1])
        # angle = np.angle(dft[:, :, 0] + 1j * dft[:, :, 1])
        # return angle
        return self.images[dft].phase

    def imgMag(self, dft, mode="show"):
        """
        Takes image and returns magnitude
        :param: dft 
        :return: npArray
        """
        print("mag")
        if mode == "mixer":
            # magSpectrum = np.abs(dft[:, :, 0] + 1j * dft[:, :, 1])
            # return magSpectrum
            pass
        else:
            dftShift = np.fft.fftshift(self.images[dft].magnitude)
            print(dftShift.shape)
            # magSpectrum = 20*np.log(cv.magnitude(dftShift[0],dftShift[1]))
            magSpectrum = 20 * np.log( dftShift)
            #     np.abs(dftShift[:, :, 0] + 1j * dftShift[:, :, 1])
            # )
            # return magSpectrum
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
                self.images[0]=ImageModel(self.fileName)
                # img1 = cv.imread(self.fileName, cv.IMREAD_GRAYSCALE)
                # print(img1.shape)
                self.images[0].showImg(self.img1Widgets[0])
                # self.showImg(self.img1Widgets[0], img1)
                self.img1ComboBox.setEnabled(True)
                # self.fouriers[0] = cv.dft(np.float32(img1), flags=cv.DFT_COMPLEX_OUTPUT)
                self.modeCheck(
                    self.img1ComboBox.currentIndex(),
                    self.img1Widgets[1],
                    0
                )
                # Enable Mixer
                self.img1Loaded = True
                self.mixerLayout.setEnabled(self.img1Loaded and self.img2Loaded)
            elif id == 2:
                self.images[1]=ImageModel(self.fileName)
                # img2 = cv.imread(self.fileName, cv.IMREAD_GRAYSCALE)
                self.images[1].showImg(self.img2Widgets[0])
                # self.showImg(self.img2Widgets[0], img2)
                self.img2ComboBox.setEnabled(True)
                # self.fouriers[1] = cv.dft(np.float32(img2), flags=cv.DFT_COMPLEX_OUTPUT)
                self.modeCheck(
                    self.img2ComboBox.currentIndex(),
                    self.img2Widgets[1],
                    1
                )
                # Enable Mixer
                self.img2Loaded = True
                self.mixerLayout.setEnabled(self.img1Loaded and self.img2Loaded)
            else:
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
