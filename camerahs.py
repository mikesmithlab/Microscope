import subprocess
from Generic.filedialogs import load_filename, save_filename
from Generic.file_handling import load_dict_from_file, save_dict_to_file
from shutil import copyfile


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

    def __init__(self,cam_config_dir='/opt/Microscope/ConfigFiles/'):
        self.cam_config_dir = cam_config_dir
        self.cam_cmds = cam_config_dir + 'cam_cmds'
        self.cam_current_ccf = cam_config_dir + 'current.ccf'
        self.cam_shell_script = cam_config_dir + 'update_cam'
        self.lut_script = cam_config_dir + 'upload_lut'
        self.load_ccf(filename=self.cam_current_ccf)

    def load_ccf(self, filename=None):
        if filename is None:
            filename = load_filename(directory=self.cam_config_dir, file_filter='*.ccf')
        self.cam_dict = load_dict_from_file(filename)

    def save_ccf(self, filename=None):
        if filename is None:
            filename = save_filename(directory=self.cam_config_dir, file_filter='*.ccf')
        save_dict_to_file(filename, self.cam_dict)

    def load_config(self):
        self._load_cam_config()
        self._load_fg_config()

    def _load_cam_config(self):
        self._write_cam_command_file()
        self._upload_cam_commands(self.cam_shell_script)

    def _load_fg_config(self):
        pass

    def reset_default_cam_config(self):
        copyfile(self.cam_config_files + 'default_backup.ccf', self.cam_current_ccf)
        self._load_cam_config(self.cam_current_ccf)

    def load_lut(self, filename=None):
        if filename is None:
            load_filename(directory=self.cam_config_dir, file_filter='*.lut')
        self._upload_cam_commands(self.lut_script)


    def _write_single_cam_command(self, command, value=None):
        with open(self.cam_cmds, "w") as fout:
            fout.writelines('#N\n')
            fout.writelines('#N\n')
            if value is None:
                fout.writelines(command + '\n')
            else:
                fout.writelines(command + '(' + str(value) + ')\n')
            fout.writelines('##quit')
            output = self._upload_cam_commands(self.cam_shell_script)
            return output



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


    def _upload_cam_commands(self, script):
        p = subprocess.Popen([script], stdout=subprocess.PIPE)
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
    #cam_set.load_config()
    cam_set.load_lut()
    #cam_set.reset_default_cam_config()
    #cam_set._save_cam_config()
