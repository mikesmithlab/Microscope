

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton, QLineEdit, QCheckBox)
from Generic.pyqt5_widgets import CheckedSlider, CheckBox, Slider, LblEdit


class CameraSettingsGUI(QWidget):

    def __init__(self, gui_pos=(1000, 500,350,400), parent=None):
        self.gui_pos=gui_pos
        self.mcf_filename = "Blah.mcf"
        self.init_ui(parent)

    def init_ui(self, parent):
        # Create window and layout
        if parent is None:
            app = QApplication(sys.argv)
        self.win = QWidget()#parent
        self.vbox = QVBoxLayout(self.win)



        roi_chooser = ROISelector(self.win)
        rate_chooser = RateSelector(self.win)
        level_chooser = LevelSelector(self.win)
        lut_chooser = LUTSelector(self.win)
        config_chooser = CONFIG(self.win)
        mcf_label = QLabel(self.mcf_filename)

        self.vbox.addWidget(roi_chooser)
        self.vbox.addWidget(rate_chooser)
        self.vbox.addWidget(level_chooser)
        self.vbox.addWidget(lut_chooser)
        self.vbox.addWidget(config_chooser)
        self.vbox.addWidget(mcf_label)

        # Finalise window
        self.win.setWindowTitle('Camera Settings Gui')
        self.win.setGeometry(self.gui_pos[0],self.gui_pos[1],self.gui_pos[2], self.gui_pos[3])
        self.win.setLayout(self.vbox)
        self.win.show()
        if parent is None:
            sys.exit(app.exec_())


class LevelSelector(QWidget):

    def __init__(self, parent):
        self.gainval = 1
        self.fpnval = False
        self.blackval = 0
        self.doubleval = 0
        self.tripleval = 0


        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())

        self.gain_level = Slider(parent, "Gain", self.gain_callback, start=1, end=5, dpi=1, initial=1)
        self.fpn_cb = CheckBox(parent, "FPN", self.fpn_callback)
        self.black_level = CheckedSlider(parent,"black", self.black_level_val, start=0, end=100, dpi=1.0, initial=self.blackval)
        self.double_level = CheckedSlider(parent,"double", self.double_level_val, start=0, end=100, dpi=1.0, initial=self.doubleval)
        self.triple_level = CheckedSlider(parent,"triple", self.triple_level_val, start=0, end=100, dpi=1.0, initial=self.tripleval)

        self.layout().addWidget(self.gain_level)
        self.layout().addWidget(self.fpn_cb)
        self.layout().addWidget(self.black_level)
        self.layout().addWidget(self.double_level)
        self.layout().addWidget(self.triple_level)

    def gain_callback(self, gainval):
        self.gainval=gainval

    def fpn_callback(self, state):
        self.fpnval = bool(self.fpn_cb.checkState())

    def black_level_val(self, blackval):
        if self.black_level.check:
            self.blackval = blackval
        else:
            self.blackval = 0
            self.black_level.slider.setSliderPosition(0)

    def double_level_val(self, doubleval):
        if self.double_level.check:
            self.doubleval = doubleval
        else:
            self.doubleval = 0
            self.double_level.slider.setSliderPosition(0)

    def triple_level_val(self, tripleval):
        if self.triple_level.check:
            self.tripleval = tripleval
        else:
            self.tripleval = 0
            self.triple_led.slider.setSliderPosition(0)


    def change_led_settings(self, colour, value):
        pass

class ROISelector(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())
        self.width_box = LblEdit(parent, "Width", 1024, self.width_callback)
        self.height_box = LblEdit(parent, "Height", 1024, self.height_callback)
        self.xoffset_box = LblEdit(parent, "Xoffset", 0, self.xoffset_callback)
        self.yoffset_box = LblEdit(parent, "Yoffset", 0, self.yoffset_callback)
        self.roi_button = QPushButton("Select ROI")
        self.roi_button.setCheckable(True)
        self.roi_button.clicked[bool].connect(self.roi_callback)

        self.layout().addWidget(self.width_box)
        self.layout().addWidget(self.height_box)
        self.layout().addWidget(self.xoffset_box)
        self.layout().addWidget(self.yoffset_box)
        self.layout().addWidget(self.roi_button)

    def width_callback(self):
        pass

    def height_callback(self):
        pass

    def yoffset_callback(self):
        pass

    def xoffset_callback(self):
        pass

    def roi_callback(self):
        pass

class RateSelector(QWidget):
    def __init__(self, parent):
        self.fps = 100
        self.exp = 100
        self.buffer = 1000
        self.afttrigger = 100
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout(parent)
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        self.framerate = LblEdit(parent, "Frame Rate (Hz)", str(self.fps), self.framerate_callback)
        self.exposure = LblEdit(parent, "Exposure (us)", str(self.exp), self.exposure_callback)
        self.buffersize = LblEdit(parent, "Num Frames Buffer", str(self.buffer), self.buffer_callback)
        self.aftertrigger = LblEdit(parent, "Num Frames After Trigger", str(self.afttrigger), self.aftertrigger_callback)
        hbox1.addWidget(self.framerate)
        hbox1.addWidget(self.exposure)
        hbox2.addWidget(self.buffersize)
        hbox2.addWidget(self.aftertrigger)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

    def framerate_callback(self):
        pass

    def exposure_callback(self):
        pass

    def buffer_callback(self):
        pass

    def aftertrigger_callback(self):
        pass

class LUTSelector(QWidget):
    def __init__(self, parent):
        self.lut_filename = "Lut File"
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())
        self.lut_lbl = QLabel(self.lut_filename)
        self.lut_button = QPushButton("Load LUT")

        self.layout().addWidget(self.lut_button)
        self.layout().addWidget(self.lut_lbl)
        self.lut_button.clicked.connect(self.lut_callback)


    def lut_callback(self):
        pass

class CONFIG(QWidget):
    def __init__(self, parent):
        self.lut_filename = "Lut File"
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())
        self.load_config = QPushButton("Load Config")
        self.load_config.clicked.connect(self.load_callback)
        self.save_config = QPushButton("Save Config")
        self.save_config.clicked.connect(self.save_callback)
        self.reset_config = QPushButton("Reset Config")
        self.reset_config.clicked.connect(self.reset_callback)

        self.layout().addWidget(self.load_config)
        self.layout().addWidget(self.save_config)
        self.layout().addWidget(self.reset_config)

    def load_callback(self):
        pass

    def save_callback(self):
        pass

    def reset_callback(self):
        pass

if __name__ == '__main__':
    camsettings = CameraSettingsGUI()


