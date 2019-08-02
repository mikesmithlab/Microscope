import subprocess
from shutil import copyfile
import SiSoPyInterface as SISO
import numpy as np
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton, QLineEdit, QCheckBox)

from Generic.filedialogs import load_filename, save_filename, open_directory
from Generic.file_handling import load_dict_from_file, save_dict_to_file
from Generic.pyqt5_widgets import CheckedSlider, CheckBox, Slider, LblEdit

''''
Reference for camera commmands can be found in cl600x2-SU-07-D_manual.pdf in microscope folder

The dictionary values are (cam command, framegrabber command if appropriate)
'''


cam_dict = {'gain':             ['#G', None,0, [0, 1]],
            'fpn' :             ['#F', None, 1, [0, 1]],
            'frameformat':      ['#R', ['FG_XOFFSET', 'FG_YOFFSET', 'FG_HEIGHT', 'FG_WIDTH'], [0, 0, 1280, 1024], [[0, 1280], [0, 1024], [200, 1280], [1, 1024]]],
            'framerate':        ['#r', 'FG_FRAMESPERSEC', 400, [20, None]],
            'exptime':          ['#e', 'FG_EXPOSURE', 1000, [1, None]],
            'dualslope':        ['#D', None, 0, [0, 1]],
            'dualslopetime':    ['#d', None, 1, [1, 1000]],
            'tripleslope':      ['#T', None, 0, [0, 1]],
            'tripleslopetime':  ['#t', None, 1, [1, 150]],
            'blacklevel':       ['#z', None, 100, [0,255]]
}


def lut_file(lut_array, filename=None):
    #lut_np array must be 1024 long with numbers between 0 and 255
    if filename is None:
        filename = save_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.lut')

    with open(filename, mode="w") as fout:
        fout.writelines('#N\n')
        fout.writelines('#l\n')
        for i in range(np.size(lut_array)):
            fout.writelines(str(int(lut_array[i])) + '\n')
        fout.writelines('##quit')

class CameraSettings:
    '''
    Class to handl e the settings of both Optronis CL600x2camera and microenable IV-AD4 CL framegrabber
    Settings files (.ccf) can be created using cam_settings.py. This is a dictionary with the following format:

    {key: [command code camera, command mcf file, value, valid range}

    Where a value is not applicable it is set to None.

    Communication with camera proceeds via writing a list of commands to cam_cmds.
    This is executed via a shell script 'update_cam' which points to the clshell in
    /opt/SiliconSoftware/Runtime5.7.0/siso-rt5-5.7.0.76321-linux-amd64/bin
    Details of the commands can be found in
    /media/NAS/MikeSmithLabSharedFolder/Manuals and guides/MicroscopeTechManuals/CL600x2-SU-07-D_Manual.pdf

    Communication with framegrabber uses SiliconSoftware python functions.


    '''

    def __init__(self, fg, cam_config_dir):
        self.fg = fg
        self.cam_config_dir = cam_config_dir
        self.cam_cmds = cam_config_dir + 'cam_cmds'
        self.cam_current_ccf = cam_config_dir + 'current.ccf'
        self.fg_current_mcf = cam_config_dir + 'current.mcf'
        self.cam_shell_script = cam_config_dir + 'update_cam'
        self.lut_script = cam_config_dir + 'upload_lut'
        self.load_config()

    def load_config(self, filename=None):
        if filename is None:
            filename = load_filename(directory=self.cam_config_dir, file_filter='*.ccf')
        self.cam_dict = load_dict_from_file(filename)
        self._load_cam_config()
        SISO.Fg_loadConfig(self.fg, filename[:-3]+'mcf')
        #self._check_new_max_vals()

    def save_config(self, filename=None):
        if filename is None:
            filename = save_filename(directory=self.cam_config_dir, file_filter='*.ccf')
        save_dict_to_file(filename, self.cam_dict)
        self.fg_saveConfig(filename[:-3]+'mcf')

    def _load_cam_config(self):
        self._write_cam_command_file()
        self._upload_cam_commands()

    def reset_default_config(self):
        copyfile(self.cam_config_dir + 'default_backup.ccf', self.cam_current_ccf)
        copyfile(self.cam_config_dir + 'default_backup.mcf', self.fg_current_mcf)
        self._load_cam_config(self.cam_current_ccf)
        SISO.Fg_loadConfig(self.fg, self.cam_config_dir + 'current.mcf')

    def load_lut(self, filename=None):
        if filename is None:
            load_filename(directory=self.cam_config_dir, file_filter='*.lut')
        self._upload_cam_commands(self.lut_script)

    def _write_cam_command_file(self):
        with open(self.cam_cmds, "w") as fout:
            fout.writelines('#N\n')
            for key in self.cam_dict.keys():
                if self.cam_dict[key][0] is not None:
                    if self.cam_dict[key][3] is None:
                        fout.writelines(self.cam_dict[key][0] + '\n')
                    elif self.cam_dict[key][0] == '#R':
                        fout.writelines(self.cam_dict[key][0] + '(' +
                                        str(self.cam_dict[key][2][0]) + ',' +
                                        str(self.cam_dict[key][2][1]) + ',' +
                                        str(self.cam_dict[key][2][2]) + ',' +
                                        str(self.cam_dict[key][2][3]) + ')\n')
                    else:
                        fout.writelines(self.cam_dict[key][0] + '(' + str(self.cam_dict[key][2]) + ')\n')
            fout.writelines('##quit')

    def _check_new_max_vals(self):
        output = self.write_single_cam_command('#A')
        self.cam_dict['framerate'][3][1] = str(int(output[0][1:-1]))
        output = self.write_single_cam_command('#a')
        self.cam_dict['exptime'][3][1] = str(int(output[0][1:-1]))

    def write_single_cam_command(self, command, value=None):
        with open(self.cam_cmds, "w") as fout:
            fout.writelines('#N\n')
            if value is None:
                fout.writelines(command + '\n')
            else:
                fout.writelines(command + '(' + str(value) + ')\n')
            fout.writelines('##quit')
        output = self._upload_cam_commands()
        return output

    def write_single_fg_command(self, parameter, value):
        '''
        SDK Docs http://www.siliconsoftware.de/download/live_docu/RT5/en/documents/SDK/SDK.html#_2.3.1
        2.4.1 lists all parameters and values.
        '''
        SISO.Fg_SetParameter(self.fg, parameter, value, 0)

    def _upload_cam_commands(self):
        p = subprocess.Popen([self.cam_shell_script], stdout=subprocess.PIPE)
        output = p.communicate()[0].split(b'\r\n')[1:-1]

        if b'>\x15' in output:
            raise CamSettingError(output)
        else:
            return output

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

class CamSettingError(Exception):
    def __init__(self):
        print('There was an issue setting 1 or more properties using .ccf file. '
              'Check the numbers in this file are allowed values. If in doubt reload '
              'the default config to get up and going again.')






if __name__ == '__main__':
    #filename = save_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.lut')
    # save_dict_to_file(filename, cam_dict)



    lut_file(np.floor(np.linspace(0, 255, 1024)))
