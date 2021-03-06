import subprocess
from shutil import copyfile
import SiSoPyInterface as SISO
from SiSoPyInterface import FG_XOFFSET, FG_YOFFSET, FG_HEIGHT, FG_WIDTH,FG_FRAMESPERSEC,FG_EXPOSURE
import numpy as np
import time
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



cam_dict = {'gain':             ['#G', None,0, [0, 1]],
            'fpn' :             ['#F', None, 1, [0, 1]],
            'frameformat':      ['#R', ['FG_XOFFSET', 'FG_YOFFSET', 'FG_WIDTH', 'FG_HEIGHT'], [0, 0, 1280, 1024], [[0, 1280],[0, 1024], [1, 1280], [1, 1024]]],
            'framerate':        ['#r', 'FG_FRAMESPERSEC', 400, [20, None]],
            'exptime':          ['#e', 'FG_EXPOSURE', 1000, [1, None]],
            'dualslope':        ['#D', None, 0, [0, 1]],
            'dualslopetime':    ['#d', None, 1, [1, 1000]],
            'tripleslope':      ['#T', None, 0, [0, 1]],
            'tripleslopetime':  ['#t', None, 1, [1, 150]],
            'blacklevel':       ['#z', None, 100, [0,255]],
            'numpicsbuffer':    [None, None, 1000, [1, None]],
            'picsaftertrigger': [None, None, 0, [None, None]]
}
'''

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
    Class to handle the settings of both Optronis CL600x2camera and microenable IV-AD4 CL framegrabber
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

    def __init__(self, fg, cam_config_dir='/opt/Microscope/ConfigFiles/', ccf_file=None):
        self.fg = fg
        self.cam_config_dir = cam_config_dir
        self.cam_cmds = cam_config_dir + 'cam_cmds'
        if ccf_file is None:
            self.cam_current_ccf = cam_config_dir + 'current.ccf'
        else:
            self.cam_current_ccf = ccf_file
        self.fg_current_mcf = cam_config_dir + 'current.mcf'
        self.cam_shell_script = cam_config_dir + 'update_cam'
        self.lut_script = cam_config_dir + 'upload_lut'
        self.load_config(filename=self.cam_current_ccf)

    def load_config(self, filename=None, parent=None):
        if filename is None:
            filename = load_filename(directory=self.cam_config_dir, file_filter='*.ccf',parent=parent)
        self.cam_dict = load_dict_from_file(filename)
        self._load_cam_config()
        SISO.Fg_loadConfig(self.fg, filename[:-3]+'mcf')

        print('new config loaded')

    def save_config(self, filename=None, parent=None):
        if filename is None:
            filename = save_filename(directory=self.cam_config_dir, file_filter='*.ccf', parent=parent)
        save_dict_to_file(filename, self.cam_dict)
        SISO.Fg_saveConfig(self.fg, filename[:-3]+'mcf')
        print('config saved')

    def _load_cam_config(self):
        self._write_cam_command_file()
        self._upload_cam_commands()

    def reset_default_config(self):
        copyfile(self.cam_config_dir + 'default_backup.ccf', self.cam_current_ccf)
        copyfile(self.cam_config_dir + 'default_backup.mcf', self.fg_current_mcf)
        self._load_cam_config()
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

    def write_single_cam_command(self, command, value=None):
        with open(self.cam_cmds, "w") as fout:
            fout.writelines('#N\n')
            if value is None:
                fout.writelines(self.cam_dict[command][0] + '\n')
            else:
                if type(value) == list:
                    fout.writelines(self.cam_dict[command][0] + '(' + str(value)[1:-1].replace(" ","") + ')\n')
                else:
                    fout.writelines(self.cam_dict[command][0] + '(' + str(value) + ')\n')
            fout.writelines('##quit')
        output = self._upload_cam_commands()
        if output is not False and value is not None:
            self.cam_dict[command][2] = value
            print('Value uploaded')
            return True
        elif output is not False and value is None:
            return output
        else:
            print('value not allowed')
            return False

    def write_single_fg_command(self, command, value , paramnum = None):
        '''
        SDK Docs http://www.siliconsoftware.de/download/live_docu/RT5/en/documents/SDK/SDK.html#_2.3.1
        2.4.1 lists all parameters and values.
        '''
        if paramnum is None:
            parameter=self.cam_dict[command][1]
        else:
            parameter = self.cam_dict[command][1][paramnum]
        param = globals()[parameter]
        SISO.Fg_setParameterWithInt(self.fg, param, value, 0)

    def _upload_cam_commands(self):
        p = subprocess.Popen([self.cam_shell_script], stdout=subprocess.PIPE)
        output = p.communicate()[0].split(b'\r\n')[1:-1]
        if b'>\x15' in output:
            return False
        else:
            return output


class CamSettingError(Exception):
    def __init__(self):
        print('There was an issue setting 1 or more properties using .ccf file. '
              'Check the numbers in this file are allowed values. If in doubt reload '
              'the default config to get up and going again.')




if __name__ == '__main__':
    #filename = save_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.lut')
    # save_dict_to_file(filename, cam_dict)
    cam_config_dir = '/opt/Microscope/ConfigFiles/'
    fg = SISO.Fg_InitConfig(cam_config_dir + 'current.mcf', 0)
    camset = CameraSettings(fg)
    camset.write_single_cam_command('framerate', 100)


