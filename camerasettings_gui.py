
import numpy as np
import sys
import SiSoPyInterface as SISO
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from microscope.ROIfigure import ROIGraphDialog
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication, QDialog,
                             QSlider, QHBoxLayout, QPushButton, QLineEdit, QCheckBox)
from Generic.pyqt5_widgets import CheckedSlider, CheckBox, Slider, LblEdit, MatplotlibFigure
import time


class CameraSettingsGUI(QDialog):

    def __init__(self, cam, parent=None):

        gui_pos = (int(1500), int(450), 300, 100)
        self.gui_pos=gui_pos
        self.cam = cam
        self.mcf_filename = self.cam.cam_config_dir + 'current.mcf'
        self.init_ui(parent)

    def init_ui(self, parent):
        # Create window and layout
        QDialog.__init__(self, parent)
        if parent is None:
            app = QApplication(sys.argv)
        # self.win = QWidget()

        # self.setLayout(QVBoxLayout())
        self.vbox = QVBoxLayout(self)

        roi_chooser = ROISelector(self, self.cam)
        rate_chooser = RateSelector(self, self.cam)
        level_chooser = LevelSelector(self, self.cam.camset)
        lut_chooser = LUTSelector(self, self.cam.camset)
        config_chooser = CONFIG(self, self.cam)
        mcf_label = QLabel(self.mcf_filename)

        self.vbox.addWidget(roi_chooser)
        self.vbox.addWidget(rate_chooser)
        self.vbox.addWidget(level_chooser)
        self.vbox.addWidget(lut_chooser)
        self.vbox.addWidget(config_chooser)
        self.vbox.addWidget(mcf_label)

        # Finalise window
        self.setWindowTitle('Camera Settings Gui')
        self.setGeometry(self.gui_pos[0],self.gui_pos[1],self.gui_pos[2], self.gui_pos[3])
        self.setLayout(self.vbox)
        self.show()
        if parent is None:
            sys.exit(app.exec_())


class LevelSelector(QWidget):

    def __init__(self, parent, cam):
        self.camset=cam

        self.gainval = self.camset.cam_dict['gain'][2]
        self.fpnval = self.camset.cam_dict['fpn'][2]
        self.blackval = self.camset.cam_dict['blacklevel'][2]
        self.doubleval = self.camset.cam_dict['dualslope'][2]
        self.tripleval = self.camset.cam_dict['tripleslope'][2]


        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())

        self.gain_level = Slider(parent, "Gain", self.gain_callback, start=self.camset.cam_dict['gain'][3][0], end=self.camset.cam_dict['gain'][3][1], dpi=1, initial=self.camset.cam_dict['gain'][2], update_delay=10, on_release= True)
        self.black_level = Slider(parent, "black", self.black_level_val, start=self.camset.cam_dict['blacklevel'][3][0],
                                  end=self.camset.cam_dict['blacklevel'][3][1], dpi=1,
                                  initial=self.camset.cam_dict['blacklevel'][2], on_release= True)
        self.fpn_cb = CheckBox(parent, "FPN", self.fpn_callback)
        self.double_level = CheckedSlider(parent,"double", self.double_level_val, start=self.camset.cam_dict['dualslopetime'][3][0], end=self.camset.cam_dict['dualslopetime'][3][1], dpi=1, initial=self.camset.cam_dict['dualslopetime'][2], on_release= True)
        self.double_level.slider.setEnabled(False)
        self.triple_level = CheckedSlider(parent,"triple", self.triple_level_val, start=self.camset.cam_dict['tripleslopetime'][3][0], end=self.camset.cam_dict['tripleslopetime'][3][1], dpi=1, initial=self.camset.cam_dict['tripleslopetime'][2], on_release= True)
        self.triple_level.slider.setEnabled(False)
        self.layout().addWidget(self.gain_level)
        self.layout().addWidget(self.black_level)
        self.layout().addWidget(self.fpn_cb)
        self.layout().addWidget(self.double_level)
        self.layout().addWidget(self.triple_level)

    def gain_callback(self, gainval):
        self.camset.write_single_cam_command('gain', int(gainval))
        self.gainval=gainval

    def fpn_callback(self):
        self.fpnval = bool(self.fpn_cb.checkState())
        if self.fpnval:
            self.camset.write_single_cam_command('fpn', int(1))
        else:
            self.camset.write_single_cam_command('fpn', int(0))


    def black_level_val(self, blackval):
        self.camset.write_single_cam_command('blacklevel', int(blackval))
        self.blackval = int(blackval)

    def double_level_val(self, doubleval):
        if self.double_level.check:
            self.double_level.slider.setEnabled(True)
            self.camset.write_single_cam_command('dualslope', int(1))
            self.camset.write_single_cam_command('dualslopetime', int(doubleval))
            self.doubleval = doubleval
        else:
            self.camset.write_single_cam_command('dualslope', int(0))
            self.double_level.slider.setEnabled(False)



    def triple_level_val(self, tripleval):
        if self.triple_level.check:
            self.tripleval = int(tripleval)
            self.triple_level.slider.setEnabled(True)
            self.camset.write_single_cam_command('tripleslope', int(1))
            self.camset.write_single_cam_command('tripleslopetime', int(tripleval))
        else:
            self.camset.write_single_cam_command('tripleslope', int(0))
            self.triple_level.slider.setEnabled(False)



class ROISelector(QWidget):
    def __init__(self, parent, cam):
        QWidget.__init__(self, parent)
        self.cam = cam
        self.camset = cam.camset
        self.setLayout(QHBoxLayout())
        self.width_box = LblEdit(parent, "Width", self.camset.cam_dict['frameformat'][2][2], self.width_callback)
        self.height_box = LblEdit(parent, "Height", self.camset.cam_dict['frameformat'][2][3], self.height_callback)
        self.xoffset_box = LblEdit(parent, "Xoffset", self.camset.cam_dict['frameformat'][2][0], self.xoffset_callback)
        self.yoffset_box = LblEdit(parent, "Yoffset", self.camset.cam_dict['frameformat'][2][1], self.yoffset_callback)
        self.roi_button = QPushButton("Select ROI", default = False, autoDefault = False)
        self.roi_button.setCheckable(True)
        self.roi_button.clicked[bool].connect(self.roi_callback)

        self.layout().addWidget(self.width_box)
        self.layout().addWidget(self.height_box)
        self.layout().addWidget(self.xoffset_box)
        self.layout().addWidget(self.yoffset_box)
        self.layout().addWidget(self.roi_button)

    def width_callback(self,wid):
        remainder = wid%16
        wid = wid - remainder
        self.frameform_input(wid,2)

    def height_callback(self,hei):
        self.frameform_input(hei, 3)

    def yoffset_callback(self,yoff):
        self.frameform_input(yoff,1)

    def xoffset_callback(self,xoff):
        remainder = xoff % 16
        xoff = xoff - remainder
        self.frameform_input(xoff, 0)

    def roi_callback(self):
        print('ROI Button Called')
        ROIGraphDialog(self,self.cam)

    def frameform_input(self,val,ind):
        frameform = self.camset.cam_dict['frameformat'][2].copy()
        frameform[ind] = val

        if self.camset.write_single_cam_command('frameformat', frameform):
            self.cam.resource_cleanup()
            self.cam.reset_display()
            if ind in [2,3]:
                self.camset.write_single_fg_command('frameformat',val, paramnum=ind)
            self.cam.initialise()
            self.cam.grab()

        self.width_box.edit.setText(str(self.camset.cam_dict['frameformat'][2][2]))
        self.height_box.edit.setText(str(self.camset.cam_dict['frameformat'][2][3]))
        self.xoffset_box.edit.setText(str(self.camset.cam_dict['frameformat'][2][0]))
        self.yoffset_box.edit.setText(str(self.camset.cam_dict['frameformat'][2][1]))



class RateSelector(QWidget):
    def __init__(self, parent, cam):
        self.camset = cam.camset
        self.cam = cam
        self.fps = self.camset.cam_dict['framerate'][2]
        self.exp = self.camset.cam_dict['exptime'][2]
        self.buffer = self.camset.cam_dict['numpicsbuffer'][2]
        self.afttrigger = self.camset.cam_dict['picsaftertrigger'][2]
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

    def framerate_callback(self,framerate):
        if self.camset.write_single_cam_command('framerate', framerate):
            self.cam.resource_cleanup()
            self.cam.reset_display()
            self.camset.write_single_fg_command('framerate', framerate)
            self.cam.initialise()
            self.cam.grab()
        else:
            self.framerate.edit.setText(str(self.camset.cam_dict['framerate'][2]))


    def exposure_callback(self,exposure):
        if self.camset.write_single_cam_command('exptime', exposure):
            self.cam.resource_cleanup()
            self.cam.reset_display()
            self.camset.write_single_fg_command('exptime', exposure)
            self.cam.initialise()
            self.cam.grab()
        else:
            self.exposure.edit.setText(str(self.camset.cam_dict['exptime'][2]))


    def buffer_callback(self,buffer):
        if type(buffer) is int and buffer > 0 :
            self.camset.cam_dict['numpicsbuffer'][2] = buffer
            self.cam.resource_cleanup()
            self.cam.reset_display()
            self.cam.initialise()
            self.cam.grab()
        else:
            self.buffersize.edit.setText(str(self.camset.cam_dict['exptime'][2]))


    def aftertrigger_callback(self,aftrig):
        self.camset.cam_dict['picsaftertrigger'][2] = aftrig


class LUTSelector(QWidget):
    def __init__(self, parent, cam):
        self.camset=cam
        self.lut_filename = self.camset.cam_dict['lutfilename'][2]
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
    def __init__(self, parent, cam):
        self.cam=cam
        self.parent=parent
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
        self.cam.resource_cleanup()
        self.cam.reset_display()
        self.cam.camset.load_config(parent=self.parent)
        self.cam.initialise()
        self.cam.grab()

    def save_callback(self):
        self.cam.camset.save_config(parent=self.parent)

    def reset_callback(self):
        self.cam.resource_cleanup()
        self.cam.reset_display()
        self.cam.camset.reset_default_config()
        self.cam.initialise()
        self.cam.grab()

if __name__ == '__main__':
    cam_config_dir = '/opt/Microscope/ConfigFiles/'
    fg = SISO.Fg_InitConfig(cam_config_dir + 'current.mcf', 0)
    camsettings = CameraSettingsGUI()


