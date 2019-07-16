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
        print(output)
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

class CameraSettingsGUI:

    def __init__(self):
        self.init_ui()

    def init_ui(self):
        # Create window and layout
        app = QApplication(sys.argv)
        self.win = QWidget()
        self.vbox = QVBoxLayout(self.win)

        self.width_box()
        self.height_box()
        self.xoffset_box()
        self.yoffset_box()
        self.select_roi_button()
        self.framerate_box()
        self.exposure_box()

        self.gain_value_slider()
        self.blacklevel_slider()
        self.duallevel_slider()
        self.triplelevel_slider()
        self.fpn_checkbox()
        self.lut_button()
        self.lut_file_label()
        self.load_config_button()
        self.save_config_button()
        self.reset_config_button()
        self.cam_settings_label()

        #widget=QWidget()
        picture_label_group = QHBoxLayout()
        picture_group = QHBoxLayout()
        select_group = QHBoxLayout()
        fps_group=QHBoxLayout()

        picture_label_group.addWidget(self.widthlbl)
        picture_label_group.addWidget(self.heightlbl)
        picture_label_group.addWidget(self.xoffsetlbl)
        picture_label_group.addWidget(self.yoffsetlbl)
        picture_group.addWidget(self.width_text)
        picture_group.addWidget(self.height_text)
        picture_group.addWidget(self.xoffset_text)
        picture_group.addWidget(self.yoffset_text)
        select_group.addWidget(self.select_roi)
        fps_group.addWidget(self.framerate_text)
        fps_group.addWidget(self.exposure_text)

        gain_group = QHBoxLayout()

        gain_box = QVBoxLayout()
        gain_box.addWidget(self.gain_lbl)
        gain_box.addWidget(self.gain_slider)
        gain_box.addWidget(self.gain_slider)
        gain_box.addWidget(self.black_val_lbl)
        gain_box.addWidget(self.black_val)
        gain_box.addWidget(self.dual_val_lbl)
        gain_box.addWidget(self.dual_val)
        gain_box.addWidget(self.triple_val_lbl)
        gain_box.addWidget(self.triple_val)
        gain_box.addWidget(self.fpn_cb)


        lut_box = QHBoxLayout()
        lut_box.addWidget(self.upload_lut)
        lut_box.addWidget(self.lut_label)

        cam_settings_file_box = QHBoxLayout()
        cam_settings_file_box.addWidget(self.load_config)
        cam_settings_file_box.addWidget(self.save_config)
        cam_settings_file_box.addWidget(self.reset_config)

        cam_settings_file_box = QHBoxLayout()

        cam_settings_file_box.addWidget(self.cam_settings)


        #self.vbox.stretch(1)
        gain_group.addLayout(gain_box)
        self.vbox.addLayout(picture_label_group)
        self.vbox.addLayout(picture_group)
        self.vbox.addLayout(select_group)
        self.vbox.addLayout(fps_group)
        self.vbox.addLayout(gain_group)
        self.vbox.addLayout(lut_box)
        self.vbox.addLayout(cam_settings_file_box)


        #self.win.setLayout(self.vbox)



        # Finalise window
        self.win.setWindowTitle('Camera Settings Gui')
        self.win.setGeometry(300,600,300,600)
        self.win.setLayout(self.vbox)
        self.win.show()
        sys.exit(app.exec_())

    def width_box(self, initial_value=1000):
        self.widthlbl = QLabel()
        self.widthlbl.setText('Width')
        self.width_text = QLineEdit()
        self.width_text.setText(str(initial_value))
        self.width_text.textChanged[str].connect(self.width_callback)

    def width_callback(self):
        pass

    def height_box(self, initial_value=1000):
        self.heightlbl = QLabel()
        self.heightlbl.setText('Height')
        self.height_text = QLineEdit()
        self.height_text.setText(str(initial_value))
        self.height_text.textChanged[str].connect(self.height_callback)

    def height_callback(self):
        pass

    def xoffset_box(self, initial_value=1000):
        self.xoffsetlbl = QLabel()
        self.xoffsetlbl.setText('Xoffset')
        self.xoffset_text = QLineEdit()
        self.xoffset_text.setText(str(initial_value))
        self.xoffset_text.textChanged[str].connect(self.xoffset_callback)

    def xoffset_callback(self):
        pass

    def yoffset_box(self, initial_value=1000):
        self.yoffsetlbl = QLabel()
        self.yoffsetlbl.setText('Yoffset')
        self.yoffset_text = QLineEdit()
        self.yoffset_text.setText(str(initial_value))
        self.yoffset_text.textChanged[str].connect(self.yoffset_callback)

    def yoffset_callback(self):
        pass


    def select_roi_button(self):
        self.select_roi = QPushButton("Select ROI")

    def framerate_box(self, initial_value=1000):
        self.frameratelbl = QLabel()
        self.frameratelbl.setText('Framerate')
        self.framerate_text = QLineEdit()
        self.framerate_text.setText(str(initial_value))
        self.framerate_text.textChanged[str].connect(self.framerate_callback)

    def framerate_callback(self):
        pass

    def exposure_box(self, initial_value=1000):
        self.exposurelbl = QLabel()
        self.exposurelbl.setText('texp (s)')
        self.exposure_text = QLineEdit()
        self.exposure_text.setText(str(initial_value))
        self.exposure_text.textChanged[str].connect(self.exposure_callback)

    def exposure_callback(self):
        pass


    def gain_value_slider(self, initial_value=1):
        self.gain_lbl = QLabel()
        self.gain_lbl.setText('Gain : '  + str(initial_value))
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(1, 5)
        self.gain_slider.setTickInterval(1)
        self.gain_slider.setTickPosition(QSlider.TicksBelow)
        self.gain_slider.setValue(initial_value)
        self.gain_slider.valueChanged.connect(self._gain_callback)

    def _gain_callback(self):
        gain_val = self.gain_slider.value()
        self.gain_lbl.setText('Gain : ' + str(gain_val))



    def blacklevel_slider(self, initial_value=100):
        self.blacklevel = initial_value
        self.black_val_lbl = QLabel()
        self.black_val_lbl.setText("Black Level: " + str(self.blacklevel))
        self.black_val = QSlider(Qt.Horizontal)
        self.black_val.setRange(1, 255)
        self.black_val.setTickInterval(1)
        self.black_val.setTickPosition(QSlider.TicksBelow)
        self.black_val.setValue(self.blacklevel)
        self.black_val.valueChanged.connect(self._black_val_callback)

    def _black_val_callback(self):
        self.blacklevel = self.black_val.value()
        self.black_val_lbl.setText("Black Level: " + str(self.blacklevel))

    def duallevel_slider(self, initial_value=100):
        self.duallevel = initial_value
        self.dual_val_lbl = QLabel()
        self.dual_val_lbl.setText("Dual Level: " + str(self.duallevel))
        self.dual_val = QSlider(Qt.Horizontal)
        self.dual_val.setRange(1, 255)
        self.dual_val.setTickInterval(1)
        self.dual_val.setTickPosition(QSlider.TicksBelow)
        self.dual_val.setValue(self.duallevel)
        self.dual_val.valueChanged.connect(self._dual_val_callback)

    def _dual_val_callback(self):
        self.duallevel = self.dual_val.value()
        self.dual_val_lbl.setText("Dual Level: " + str(self.duallevel))

    def triplelevel_slider(self, initial_value=100):
        self.triplelevel = initial_value
        self.triple_val_lbl = QLabel()
        self.triple_val_lbl.setText("Triple Level: " + str(self.triplelevel))
        self.triple_val = QSlider(Qt.Horizontal)
        self.triple_val.setRange(1, 255)
        self.triple_val.setTickInterval(1)
        self.triple_val.setTickPosition(QSlider.TicksBelow)
        self.triple_val.setValue(self.triplelevel)
        self.triple_val.valueChanged.connect(self._triple_val_callback)

    def _triple_val_callback(self):
        self.triplelevel = self.triple_val.value()
        self.triple_val_lbl.setText("Triple Level: " + str(self.triplelevel))

    def fpn_checkbox(self, initial_value=2):
        self.fpn_cb = QCheckBox('FPN')
        if initial_value == 2:
            #A ticked checkbox = 2 and unchecked = 0
            self.fpn_cb.toggle()
        self.fpn_cb.stateChanged.connect(self._fpn_callback)

    def _fpn_callback(self, state):
        self.fpn_val = state
        print(state)

    def lut_button(self):
        widget = QWidget()
        self.upload_lut = QPushButton("Update LUT")
        self.upload_lut.clicked.connect(self.lut_callback)

    def lut_callback(self):
        pass

    def lut_file_label(self, label="lut _ test"):
        #widget = QWidget()
        self.lut_label = QLabel(label)

    def load_config_button(self):
        # Add Save Button
        #widget = QWidget()
        self.load_config = QPushButton("Load Config")
        self.load_config.clicked.connect(self.load_config_callback)


    def load_config_callback(self):
        pass

    def save_config_button(self):
        # Add Save Button
        widget = QWidget()
        self.save_config = QPushButton("Save Config")
        self.save_config.clicked.connect(self.save_config_callback)


    def save_config_callback(self):
        pass

    def reset_config_button(self):
        widget = QWidget()
        self.reset_config = QPushButton("Reset Config")
        self.reset_config.clicked.connect(self.reset_config_callback)


    def reset_config_callback(self):
        pass

    def cam_settings_label(self, label='mcf test'):
        widget = QWidget()
        self.cam_settings = QLabel(label)

    def add_edit_text(self):
        self.lbl = QLabel(self)
        qle = QLineEdit(self)
        qle.textChanged[str].connect(self.onChanged)


class CamSettingError(Exception):
    def __init__(self):
        print('There was an issue setting 1 or more properties using .ccf file. '
              'Check the numbers in this file are allowed values. If in doubt reload '
              'the default config to get up and going again.')






if __name__ == '__main__':
    #filename = save_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.lut')
    # save_dict_to_file(filename, cam_dict)



    lut_file(np.floor(np.linspace(0, 255, 1024)))
