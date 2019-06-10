import microscope.cam_settings as cam_settings
import subprocess





class CameraSettings:

    def __init__(self):
        self.cmd_dict = cam_settings.param_dict
        self._write_camera()



    def _rewrite_mcf(self):
        pass

    def _write_value_camconfig(self, param, value):
        pass


    def _write_camera(self, shell_script=''):
        p = subprocess.Popen([cam_settings.cam_shell], stdout=subprocess.PIPE)
        output=p.communicate()[0].split(b'\r\n')[1:]



if __name__ == '__main__':
    cam_set = CameraSettings()
