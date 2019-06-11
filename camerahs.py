import microscope.cam_settings as cam_settings
import subprocess
from Generic.filedialogs import load_filename





class CameraSettings:

    def __init__(self,CamCmdsFile='/opt/Microscope/ConfigFiles/CamCmds'):
        self.CamCmdsFile = CamCmdsFile

    def load_config(self, filename=None):

        #if filename is None:
        filename = load_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.ccf')
        print(filename)
        #self._load_cam_config(filename)

    def save_config(self):
        pass

    def _load_cam_config(self, filename):
        self._write_cam_command_file(filename)
        self._upload_cam_commands()

    def update_cam_param(self, param, value=None):
        with open(self.CamCmdsFile, "w") as fout:
            fout.writelines('#N')
            if value is None:
                fout.writelines(cam_settings.cam_dict[param])
            else:
                fout.writelines(cam_settings.cam_dict[param] + value)


    def load_lut_cam(self):
        pass

    def save_lut_cam(self):
        pass

    def _write_cam_command_file(self, filename):
        print(filename)
        with open(filename, "r") as fin:
            with open(self.CamCmdsFile, "w") as fout:
                fout.writelines('#N')
                for line in fin:
                    input = line.split('=')
                    print(input)
                    if input[0] in cam_settings.cam_dict.keys():
                        fout.writelines(cam_settings.cam_dict[input[0]] + input[1])


    def _upload_cam_commands(self):
        p = subprocess.Popen([cam_settings.cam_shell], stdout=subprocess.PIPE)
        output = p.communicate()[0].split(b'\r\n')[1:]




    def _rewrite_mcf(self):
        pass

    def _write_value_camconfig(self, param, value):
        pass





if __name__ == '__main__':
    cam_set = CameraSettings()
    cam_set.load_config()
