import sys
import numpy as np
import cv2 as cv
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import imageMixerUI as mw

# widget.view.setAspectLocked(False)
#         widget.view.setRange(xRange=[0, imageInst.imageShape[1]]
#                              , yRange=[0, imageInst.imageShape[0]], padding=0)


class mixerApp(mw.Ui_MainWindow):
    def __init__(self, starterWindow):
        """
        Main loop of the UI
        :param mainWindow: QMainWindow Object
        """

        super(mixerApp, self).setupUi(starterWindow)

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
                self.img1ComboBox.currentIndex(), self.img1Widgets[1], self.fouriers[0]
            )
        )
        self.img2ComboBox.currentIndexChanged.connect(
            lambda: self.modeCheck(
                self.img2ComboBox.currentIndex(), self.img2Widgets[1], self.fouriers[1]
            )
        )
        self.comp1HorizontalSlider.valueChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
        )
        self.comp2HorizontalSlider.valueChanged.connect(
            lambda: self.comboChecker(self.comp1ChoiceComboBox.currentIndex(), 0)
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
            mode = "cmplx"
            self.comboChoice[self.autoSelect(id)].setCurrentIndex(
                self.autoSelect(choice)
            )
        else:
            mode = "phase"
        self.mixCheck(mode)

    def mixCheck(self, mode):
        w1 = self.comp1HorizontalSlider.value()
        w2 = self.comp2HorizontalSlider.value()
        choice1 = self.comp1CompoBox.currentIndex()
        choice2 = self.comp2CompoBox.currentIndex()
        component1 = self.comp1ChoiceComboBox.currentIndex()
        component2 = self.comp2ChoiceComboBox.currentIndex()
        components = []

        # Get components
        components.append(self.modes[component1](self.fouriers[choice1], "mixer"))
        components.append(self.modes[component2](self.fouriers[choice1], "mixer"))
        components.append(self.modes[component1](self.fouriers[choice2], "mixer"))
        components.append(self.modes[component2](self.fouriers[choice2], "mixer"))
        print("Mixing")
        output = self.mixer(w1, w2, mode, components)
        self.showImg(self.outputWidgets[self.outputComboBox.currentIndex()], output)

    def mixer(self, weight1, weight2, mode, component):
        if mode == "phase":
            print("phase mixer")
            mix = np.multiply(
                ((weight1 * component[0]) + ((1 - weight1) * component[2])),
                np.exp2(1j * ((1 - weight2) * component[1]) + (weight2 * component[3])),
            )
            img = np.fft.ifft2(mix)
            # img = cv.idft(np.float32(mix))
            return np.real(img)
        elif mode == "cmplx":
            print("cmplx mixer")
            mix = ((weight1 * component[0]) + ((1 - weight1) * component[2])) + 1j * (
                ((1 - weight2) * component[1]) + (weight2 * component[3])
            )
            img = np.fft.ifft2(mix)
            # img = cv.idft(np.float32(mix))
            return np.real(img)
        else:
            print("error in mixer")

    def modeCheck(self, mode, widget, data, image=None):
        print(mode)
        image = self.modes[mode](data)
        self.showImg(widget, image)

    def showImg(self, widget, image):
        print(image.shape)
        widget.show()
        widget.setImage(image.T)
        self.scaleImage(widget, image.shape)

    def uniMag(self, dft):
        return np.ones(dft[:,:,0].shape)

    def uniPhase(self, dft):
        return np.zeros(dft[:,:,1].shape)

    def imgReal(self, dft, mode="show"):
        print("Real")
        if mode == "mixer":
            return dft[:, :, 0]
        else:
            return 20 * np.log(dft[:, :, 0] + self.__epsilon)

    def imgImaginry(self, dft, mode="show"):
        print("Imaginry")
        if mode == "mixer":
            return dft[:, :, 1]
        else:
            return 20 * np.log(dft[:, :, 1] + self.__epsilon)

    def imgPhase(self, dft, mode=None):
        print("PHase")
        angle = cv.phase(dft[:, :, 0], dft[:, :, 1])
        return angle

    def imgMag(self, dft, mode="show"):
        """
        Takes image and returns magnitude
        :param: dft 
        :return: npArray
        """
        print("mag")
        if mode == "mixer":
            magSpectrum = cv.magnitude(dft[:, :, 0], dft[:, :, 1])
            return magSpectrum
        else:
            dftShift = np.fft.fftshift(dft)
            print(dftShift.shape)
            # magSpectrum = 20*np.log(cv.magnitude(dftShift[0],dftShift[1]))
            magSpectrum = 20 * np.log(
                cv.magnitude(dftShift[:, :, 0], dftShift[:, :, 1])
            )
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
                img1 = cv.imread(self.fileName, cv.IMREAD_GRAYSCALE)
                print(img1.shape)
                self.showImg(self.img1Widgets[0], img1)
                self.img1ComboBox.setEnabled(True)
                self.fouriers[0] = cv.dft(np.float32(img1), flags=cv.DFT_COMPLEX_OUTPUT)
                self.modeCheck(
                    self.img1ComboBox.currentIndex(),
                    self.img1Widgets[1],
                    self.fouriers[0],
                )
                # Enable Mixer
                self.img1Loaded = True
                self.mixerLayout.setEnabled(self.img1Loaded and self.img2Loaded)
            elif id == 2:
                img2 = cv.imread(self.fileName, cv.IMREAD_GRAYSCALE)
                self.showImg(self.img2Widgets[0], img2)
                self.img2ComboBox.setEnabled(True)
                self.fouriers[1] = cv.dft(np.float32(img2), flags=cv.DFT_COMPLEX_OUTPUT)
                self.modeCheck(
                    self.img2ComboBox.currentIndex(),
                    self.img2Widgets[1],
                    self.fouriers[1],
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
