import microscope.cam_settings as
import subprocess
from Generic.filedialogs import load_filename, save_filename
from Generic.file_handling import load_dict_from_file, save_dict_to_file
from shutil import copyfile

import numpy as np



class CameraSettings:

    def __init__(self,cam_config_files='/opt/Microscope/ConfigFiles/'):
        self.cam_config_files = cam_config_files
        self.cam_cmds_file = cam_config_files + 'cam_cmds'
        self.cam_current_ccf_file = cam_config_files + 'current.ccf'
        self.cam_shell_script = cam_config_files + 'update_cam'
        self.load_ccf(filename=self.cam_current_ccf_file)

    def load_ccf(self, filename=None):
        if filename is None:
            filename = load_filename(directory=self.cam_config_files, file_filter='*.ccf')
        self.cam_dict = load_dict_from_file(filename)

    def save_ccf(self, filename=None):
        if filename is None:
            filename = save_filename(directory=self.cam_config_files, file_filter='*.ccf')
        save_dict_to_file(filename, self.cam_dict)

    def load_config(self):
        self._load_cam_config()
        self._load_fg_config()

    def _load_cam_config(self):
        self._write_cam_command_file()
        self._upload_cam_commands()

    def _load_fg_config(self):
        pass

    def _save_cam_config(self, filename=None):
        if filename is None:
            filename = save_filename(directory=self.cam_config_files, file_filter='*.ccf')

        with open(self.cam_current_ccf_file, "r") as fin:
            with open(filename, "w") as fout:
                for line in fin:
                    key = line.split('=')[0]
                    if key in cam_settings.cam_dict.keys():
                        output = self._write_single_cam_command(cam_settings.cam_dict[key])
                        new_line = key + '=' + output.split(': ')[1]

                    else:
                        fout.writelines(line)


    def reset_default_cam_config(self):
        copyfile(self.cam_config_files + 'default_backup.ccf', self.cam_current_ccf_file)
        self._load_cam_config(self.cam_current_ccf_file)

    def load_lut_cam(self):
        pass

    def save_lut_cam(self):
        pass

    def _write_single_cam_command(self, command, value=None):
        with open(self.cam_cmds_file, "w") as fout:
            fout.writelines('#N\n')
            fout.writelines('#N\n')
            if value is None:
                fout.writelines(command + '\n')
            else:
                fout.writelines(command + '(' + str(value) + ')\n')
            fout.writelines('##quit')
            output = self._upload_cam_commands()
            return output



    def _write_cam_command_file(self):
        with open(self.cam_cmds_file, "w") as fout:
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


    def _upload_cam_commands(self):
        p = subprocess.Popen([self.cam_shell_script], stdout=subprocess.PIPE)
        output = p.communicate()[0].split(b'\r\n')[1:-1]
        if b'>\x15' in output:
            raise CamSettingError(output)
        else:
            return output




    def _rewrite_mcf(self):
        pass

    def _write_value_camconfig(self, param, value):
        pass


class CamSettingError(Exception):
    def __init__(self):
        print('There was an issue setting 1 or more properties using .ccf file. '
              'Check the numbers in this file are allowed values. If in doubt reload '
              'the default config to get up and going again.')


if __name__ == '__main__':

    cam_set = CameraSettings()

    #cam_set.load_ccf()
    cam_set.load_config()
    #cam_set.reset_default_cam_config()
    #cam_set._save_cam_config()
