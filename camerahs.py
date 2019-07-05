import subprocess
from Generic.filedialogs import load_filename, save_filename
from Generic.file_handling import load_dict_from_file, save_dict_to_file
from shutil import copyfile
import SiSoPyInterface as SISO

class Camera:
    def __init__(self, cam_config_dir='/opt/Microscope/ConfigFiles/'):
        self.cam_config_dir = cam_config_dir
        self.fg = SISO.Fg_InitConfig(cam_config_dir + 'current.mcf', 0)
        self.set = CameraSettings(self.fg, cam_config_dir)

    def initialise(self, nrOfPicturesToGrab, nbBuffers=10):
        self.fg = SISO.Fg_InitConfig(self.cam_config_dir + 'current.mcf', 0)
        self.nrOfPicturesToGrab = nrOfPicturesToGrab
        self.display = SISO.CreateDisplay(8, self.set.cam_dict['frameformat'][2][2], self.set.cam_dict['frameformat'][2][3])
        SISO.SetBufferWidth(self.display, self.set.cam_dict['frameformat'][2][2], self.set.cam_dict['frameformat'][2][3])
        totalBufferSize = self.set.cam_dict['frameformat'][2][2] * self.set.cam_dict['frameformat'][2][3] * nbBuffers
        self.memHandle = SISO.Fg_AllocMemEx(self.fg, totalBufferSize, nbBuffers)

    def start(self):
        err = SISO.Fg_AcquireEx(self.fg, 0, self.nrOfPicturesToGrab, SISO.ACQ_STANDARD, self.memHandle)
        if (err != 0):
            print('Fg_AcquireEx() failed:', s.Fg_getLastErrorDescription(fg))
            SISO.Fg_FreeMemEx(self.fg, self.memHandle)
            SISO.CloseDisplay(self.display)
            SISO.Fg_FreeGrabber(self.fg)
            exit(err)

        cur_pic_nr = 0
        last_pic_nr = 0
        img = "will point to last grabbed image"
        nImg = "will point to Numpy image/matrix"

        win_name_img = "Source Image (SiSo Runtime)"
        win_name_res = "Result Image (openCV)"

        print("Acquisition started")

        # RUN PROCESSING LOOP for nrOfPicturesToGrab images
        while cur_pic_nr < self.nrOfPicturesToGrab:

            cur_pic_nr = SISO.Fg_getLastPicNumberBlockingEx(self.fg, last_pic_nr + 1, 0, 5, self.memHandle)

            if (cur_pic_nr < 0):
                print("Fg_getLastPicNumberBlockingEx(", (last_pic_nr + 1), ") failed: ",
                      (SISO.Fg_getLastErrorDescription(self.fg)))
                SISO.Fg_stopAcquire(self.fg, 0)
                SISO.Fg_FreeMemEx(self.fg, self.memHandle)
                SISO.CloseDisplay(self.display)
                SISO.Fg_FreeGrabber(self.fg)
                exit(cur_pic_nr)

            last_pic_nr = cur_pic_nr

            # get image pointer
            img = SISO.Fg_getImagePtrEx(self.fg, last_pic_nr, 0, self.memHandle)

            # handle this as Numpy array (using same memory, NO copy)
            # nImg = s.getArrayFrom(img, width, height)

            # display source image
            SISO.DrawBuffer(self.display, img, last_pic_nr, win_name_img)

        SISO.CloseDisplay(self.display)

        print("Acquisition stopped")

    def stop(self):
        pass


    def release(self):
        SISO.Fg_FreeGrabber(self.fg)

    def _view(self, numpics=100):
        width = self.set.cam_dict['frameformat'][2][3]
        height = self.set.cam_dict['frameformat'][2][2]
        self.display = SISO.CreateDisplay(8, width, height)
        SISO.SetBufferWidth(self.display, width, height)

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
        self._check_new_max_vals()

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


class CamSettingError(Exception):
    def __init__(self):
        print('There was an issue setting 1 or more properties using .ccf file. '
              'Check the numbers in this file are allowed values. If in doubt reload '
              'the default config to get up and going again.')


if __name__ == '__main__':
    import SiSoPyInterface

    cam = Camera()

    cam.initialise(100)
    cam.start()
    cam.release()


    #cam_set._check_new_max_vals()
    #cam_set.load_lut()
    #cam_set.reset_default_cam_config()
    #cam_set._save_cam_config()
