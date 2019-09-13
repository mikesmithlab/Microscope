from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton)
import qimage2ndarray as qim
import sys
import os
import cv2

import SiSoPyInterface as SISO

from Generic.filedialogs import save_filename
from Generic.video import WriteVideo
from Generic.pyqt5_widgets import QtImageViewer
from Generic.images import hstack
from microscope.cam_settings import CameraSettings
from microscope.camerasettings_gui import CameraSettingsGUI
import time
from threading import Timer

class Camera:
    def __init__(self, cam_config_dir='/opt/Microscope/ConfigFiles/', filename=None):
        self.cam_config_dir = cam_config_dir
        self.fg = SISO.Fg_InitConfig(cam_config_dir + 'current.mcf', 0)
        self.camset = CameraSettings(self.fg, cam_config_dir)
        if filename is None:
            filename = save_filename(caption='Select filename base', directory='/home/ppzmis/Videos/')
        self.filename_base = filename.split('.')[0]
        self.autosave=False

    def initialise(self):
        totalBufferSize = self.camset.cam_dict['frameformat'][2][2] * self.camset.cam_dict['frameformat'][2][3] * self.camset.cam_dict['numpicsbuffer'][2]
        self.memHandle = SISO.Fg_AllocMemEx(self.fg, totalBufferSize, self.camset.cam_dict['numpicsbuffer'][2])
        self.display = SISO.CreateDisplay(8, self.camset.cam_dict['frameformat'][2][2],
                                          self.camset.cam_dict['frameformat'][2][3])
        SISO.SetBufferWidth(self.display, self.camset.cam_dict['frameformat'][2][2],
                            self.camset.cam_dict['frameformat'][2][3])

    def grab(self, numpics=0):
        if numpics == 0:
            self.numpics = SISO.GRAB_INFINITE
        else:
            self.numpics=numpics

        err = SISO.Fg_AcquireEx(self.fg, 0, self.numpics, SISO.ACQ_STANDARD, self.memHandle)

        if (err != 0):
            print('Fg_AcquireEx() failed:', SISO.Fg_getLastErrorDescription(self.fg))
            self.resource_cleanup()

        self.display_timer = DisplayTimer(0.03, self.display_img)
        self.display_timer.start()
        if self.numpics != SISO.GRAB_INFINITE:
            while self.display_timer.is_running:
                time.sleep(0.1)
            #self.stop()
            if self.autosave:
                self.save_vid(1, self.numpics)
                self.resource_cleanup()

    def trigger(self):
        picsaftertrigger = self.camset.cam_dict['picsaftertrigger'][2]
        framerate = self.camset.cam_dict['framerate'][2]
        if picsaftertrigger != 0:
            time.sleep(picsaftertrigger/framerate)
        self.display_timer.stop()
        self.stop()

    def snap(self, filename=None, ext='.png'):
        if filename is not None:
            self.filename_base =filename.split('.')[0]
        date_time = self.datetimestr()
        cur_pic_nr = SISO.Fg_getLastPicNumberEx(self.fg, 0, self.memHandle)
        img_ptr = SISO.Fg_getImagePtrEx(self.fg, cur_pic_nr, 0, self.memHandle)
        nImg = SISO.getArrayFrom(img_ptr, self.camset.cam_dict['frameformat'][2][3],
                                 self.camset.cam_dict['frameformat'][2][2])
        cv2.imwrite(self.filename_base+date_time+ext, nImg)

    def snap_max_array(self):
        cur_pic_nr = SISO.Fg_getLastPicNumberEx(self.fg, 0, self.memHandle)
        img_ptr = SISO.Fg_getImagePtrEx(self.fg, cur_pic_nr, 0, self.memHandle)
        nImg = SISO.getArrayFrom(img_ptr, self.camset.cam_dict['frameformat'][3][0][1],
                                 self.camset.cam_dict['frameformat'][3][1][1])
        return nImg

    def get_pixmap_image(self, frame):
        img_ptr = SISO.Fg_getImagePtrEx(self.fg, int(frame), 0, self.memHandle)
        nImg = SISO.getArrayFrom(img_ptr, self.camset.cam_dict['frameformat'][2][3],
                                 self.camset.cam_dict['frameformat'][2][2])
        pixmap = QPixmap.fromImage(array2qimage(nImg))
        return pixmap



    def display_img(self):
        cur_pic_nr = SISO.Fg_getLastPicNumberEx(self.fg, 0, self.memHandle)
        if cur_pic_nr == self.numpics:
            self.display_timer.stop()
            if self.autosave:
                self.save_vid(self.filename_base, 1, 250)
                self.resource_cleanup()
        else:
            win_name_img = "Source Image (SiSo Runtime)"
            # get image pointer
            img_ptr = SISO.Fg_getImagePtrEx(self.fg, cur_pic_nr, 0, self.memHandle)
            SISO.DrawBuffer(self.display, img_ptr, cur_pic_nr, win_name_img)

    def stop(self):
        #self.max_img_num = SISO.Fg_getLastPicNumberEx(self.fg, self.last_pic_nr, 0, 5, self.memHandle)
        SISO.Fg_stopAcquire(self.fg, 0)

    def datetimestr(self):
        now = time.gmtime()
        return time.strftime("%Y%m%d_%H%M%S", now)

    def save_vid(self, startframe, stopframe, ext='.mp4', filename=None):
        if startframe == 0:
            print('Frame numbers start from 1 setting startframe to 1')
            startframe = 1
        if filename is None:
            date_time = self.datetimestr()
            filename_op = self.filename_base+str(date_time)+ext
        else:
            filename_op=filename + ext
        writevid = WriteVideo(filename=filename_op, frame_size=(
                                self.camset.cam_dict['frameformat'][2][2], self.camset.cam_dict['frameformat'][2][3]))
        for frame in range(startframe, stopframe, 1):
            img_ptr = SISO.Fg_getImagePtrEx(self.fg, int(frame), 0, self.memHandle)
            nImg = SISO.getArrayFrom(img_ptr, self.camset.cam_dict['frameformat'][2][3],
                                 self.camset.cam_dict['frameformat'][2][2])
            writevid.add_frame(nImg)
        writevid.close()

    def set_autosave(self, autosave=False, filename=None):
        self.autosave = autosave
        if self.autosave:
            if filename is not None:
                self.filename_base = filename.split('.')[0]

    def resource_cleanup(self):
        SISO.CloseDisplay(self.display)
        print('Resources released')


    def close_display(self):
        SISO.CloseDisplay(self.display)
        os.system('wmctrl -a "Display"')
        os.system('wmctrl -c "Display"')


    def reset_display(self):
        self.stop()
        self.display_timer.stop()
        self.close_display()
        time.sleep(0.1)






class DisplayTimer(object):
    def __init__(self, interval, startfunction):
        self._timer     = None
        self.interval   = interval
        self.startfunction   = startfunction
        #self.stopfunction = stopfunction
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()


    def start(self):
        self.startfunction()
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False




if __name__ == '__main__':
    cam=Camera(filename='/home/ppzmis/Videos/test.mp4')
    cam.initialise()
    #cam.set_autosave(True)

    #cam.grab(numpics=100)