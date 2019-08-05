from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton)
import qimage2ndarray as qim
import sys

import SiSoPyInterface as SISO

from Generic.filedialogs import save_filename
from Generic.video import WriteVideo
from Generic.pyqt5_widgets import QtImageViewer
from Generic.images import hstack
from microscope.cam_settings import CameraSettings
from microscope.camerasettings_gui import CameraSettingsGUI

class Camera:
    def __init__(self, cam_config_dir='/opt/Microscope/ConfigFiles/'):
        self.cam_config_dir = cam_config_dir
        self.fg = SISO.Fg_InitConfig(cam_config_dir + 'current.mcf', 0)
        self.camset = CameraSettings(self.fg, cam_config_dir)



    def initialise(self):
        self.fg = SISO.Fg_InitConfig(self.cam_config_dir + 'current.mcf', 0)
        totalBufferSize = self.camset.cam_dict['frameformat'][2][2] * self.camset.cam_dict['frameformat'][2][3] * self.camset.cam_dict['numpicsbuffer'][2]
        self.memHandle = SISO.Fg_AllocMemEx(self.fg, totalBufferSize, self.camset.cam_dict['numpicsbuffer'][2])
        self.display = SISO.CreateDisplay(8, self.camset.cam_dict['frameformat'][2][2],
                                          self.camset.cam_dict['frameformat'][2][3])
        SISO.SetBufferWidth(self.display, self.camset.cam_dict['frameformat'][2][2],
                            self.camset.cam_dict['frameformat'][2][3])

    def preview(self):

        err = SISO.Fg_AcquireEx(self.fg, 0, SISO.GRAB_INFINITE, SISO.ACQ_STANDARD, self.memHandle)

        if (err != 0):
            print('Fg_AcquireEx() failed:', SISO.Fg_getLastErrorDescription(self.fg))
            SISO.Fg_FreeMemEx(self.fg, self.memHandle)
            SISO.CloseDisplay(self.display)
            SISO.Fg_FreeGrabber(self.fg)
            exit(err)

        while True:
            pic_num = self.collect_img()

    def collect_img(self):
        cur_pic_nr = SISO.Fg_getLastPicNumberEx(self.fg, 0, self.memHandle)
        #cur_pic_nr = SISO.Fg_getLastPicNumberBlockingEx(self.fg, last_pic_nr + 1, 0, 5, self.memHandle)

        win_name_img = "Source Image (SiSo Runtime)"

        if (cur_pic_nr < 0):
            print('here')
            #print("Fg_getLastPicNumber", (last_pic_nr + 1), ") failed: ",
            #      (SISO.Fg_getLastErrorDescription(self.fg)))
            SISO.Fg_stopAcquire(self.fg, 0)
            SISO.Fg_FreeMemEx(self.fg, self.memHandle)
            SISO.CloseDisplay(self.display)
            SISO.Fg_FreeGrabber(self.fg)
            exit(cur_pic_nr)

        last_pic_nr = cur_pic_nr

        # get image pointer
        img_ptr = SISO.Fg_getImagePtrEx(self.fg, cur_pic_nr, 0, self.memHandle)

        # display source image
        SISO.DrawBuffer(self.display, img_ptr, cur_pic_nr, win_name_img)
        return cur_pic_nr


    def grab(self, numpics=20):
        if numpics is None:
            numpics = self.numPicsBuffer
        self.numpics = numpics

        err = SISO.Fg_AcquireEx(self.fg, 0, numpics, SISO.ACQ_STANDARD, self.memHandle)

        if (err != 0):
            print('Fg_AcquireEx() failed:', SISO.Fg_getLastErrorDescription(self.fg))
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

        # RUN PROCESSING LOOP for numpics images

        while cur_pic_nr < numpics:

            #cur_pic_nr = SISO.Fg_getLastPicNumberEx(self.fg, 0, self.memHandle)
            cur_pic_nr = SISO.Fg_getLastPicNumberBlockingEx(self.fg, last_pic_nr+1, 0, 5, self.memHandle)

            if (cur_pic_nr < 0):
                print('here')
                print("Fg_getLastPicNumber", (last_pic_nr + 1), ") failed: ",
                      (SISO.Fg_getLastErrorDescription(self.fg)))
                SISO.Fg_stopAcquire(self.fg, 0)
                SISO.Fg_FreeMemEx(self.fg, self.memHandle)
                SISO.CloseDisplay(self.display)
                SISO.Fg_FreeGrabber(self.fg)
                exit(cur_pic_nr)

            last_pic_nr = cur_pic_nr

            # get image pointer
            img_ptr = SISO.Fg_getImagePtrEx(self.fg, last_pic_nr, 0, self.memHandle)

            # display source image
            SISO.DrawBuffer(self.display, img_ptr, last_pic_nr, win_name_img)

        self.last_pic_nr = last_pic_nr
        SISO.CloseDisplay(self.display)

        print("Acquisition stopped")

        #self.save()
        self.stop()

    def stop(self):
        self.max_img_num = self.numpics#SISO.Fg_getLastPicNumberEx(self.fg, self.last_pic_nr, 0, 5, self.memHandle)
        SISO.Fg_stopAcquire(self.fg, 0)
        self.edit()

    def save(self, filename=None, first=0, last=None):
        if filename is None:
            filename = save_filename(directory='/home/ppzmis/Videos/')
        writevid = WriteVideo(filename=filename, frame_size=(self.set.cam_dict['frameformat'][2][2], self.set.cam_dict['frameformat'][2][3]))

        if last is None:
            last = self.max_img_num

        for i in range(1, last, 1):
            print(i)
            img_ptr = SISO.Fg_getImagePtrEx(self.fg, i, 0, self.memHandle)
            nImg = SISO.getArrayFrom(img_ptr, self.set.cam_dict['frameformat'][2][3],
                                     self.set.cam_dict['frameformat'][2][2])
            #write_img(nImg, filename + str(i) + '.png')
            # print(np.shape(nImg))
            # display(nImg)
            writevid.add_frame(nImg)

        writevid.close()

    def release(self):
        SISO.Fg_FreeGrabber(self.fg)

    def _view(self, numpics=100):
        width = self.set.cam_dict['frameformat'][2][3]
        height = self.set.cam_dict['frameformat'][2][2]
        self.display = SISO.CreateDisplay(8, width, height)
        SISO.SetBufferWidth(self.display, width, height)







if __name__ == '__main__':
    #import SiSoPyInterface

    #camGUI = CameraControlGui()

    #camSettings = CameraSettingsGUI()
    cam = Camera()
    print(cam.camset.cam_dict)
    cam.initialise()
    cam.preview()
    #cam.save()
    #cam.release()


    #cam_set._check_new_max_vals()
    #cam_set.load_lut()
    #cam_set.reset_default_cam_config()
    #cam_set._save_cam_config()
