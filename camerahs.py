import microscope.cam_settings as cam_settings
import subprocess
from Generic.filedialogs import load_filename, save_filename
from shutil import copyfile




class CameraSettings:

    def __init__(self,cam_config_files='/opt/Microscope/ConfigFiles/'):
        self.cam_config_files = cam_config_files
        self.cam_cmds_file = cam_config_files + 'cam_cmds'
        self.cam_current_ccf_file = cam_config_files + 'current.ccf'
        self.cam_shell_script = cam_config_files + 'update_cam'

    def load_config(self, filename=None):
        if filename is None:
            filename = load_filename(directory=self.cam_config_files, file_filter='*.ccf')
        self._load_cam_config(filename)
        if filename != self.cam_current_ccf_file:
            copyfile(filename, self.cam_current_ccf_file)

    def save_config(self):
        pass

    def _load_cam_config(self, filename):
        self._write_cam_command_file(filename)
        self._upload_cam_commands()

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
                print(command + '\n')
                fout.writelines(command + '\n')
            else:
                fout.writelines(command + '(' + str(value) + ')\n')
            fout.writelines('##quit')
            output = self._upload_cam_commands()
            return output

    def _write_cam_command_file(self, filename):
        with open(filename, "r") as fin:
            with open(self.cam_cmds_file, "w") as fout:
                fout.writelines('#N\n')
                for line in fin:
                    input = line.strip().split('=')
                    if input[0] in cam_settings.cam_dict.keys():
                        fout.writelines(cam_settings.cam_dict[input[0]] + '(' + input[1] + ')\n')
                fout.writelines('##quit')


    def _upload_cam_commands(self):
        print(self.cam_shell_script)
        p = subprocess.Popen([self.cam_shell_script], stdout=subprocess.PIPE)
        output = p.communicate()[0].split(b'\r\n')
        print(output)
        return output




    def _rewrite_mcf(self):
        pass

    def _write_value_camconfig(self, param, value):
        pass





if __name__ == '__main__':

    cam_set = CameraSettings()
    #cam_set.reset_default_cam_config()
    cam_set.load_config()
    #cam_set.reset_default_cam_config()
    cam_set._save_cam_config()
