from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton)
import qimage2ndarray as qim
import sys
from Generic.pyqt5_widgets import QtImageViewer
from Generic.images import hstack
from Generic.filedialogs import save_filename
from microscope.video_cutter import VideoCutter
import SiSoPyInterface as SISO

from PyQt5.QtGui import QCloseEvent

from microscope.camerahs import Camera
from microscope.camerasettings_gui import CameraSettingsGUI

class QWidgetMod(QWidget):
    """
    Overrides the closeEvent method of QWidget to clean up the camera resources on gui exit
    """
    def __init__(self, cam):
        QWidget.__init__(self)
        self.cam = cam


    def closeEvent(self, a0: QCloseEvent) -> None:
        print('Camera stopped and resources cleaned up')
        self.cam.stop()
        self.cam.resource_cleanup()



class CameraControlGui(QWidgetMod):
    def __init__(self, parent=None):
        self.cam = Camera()
        self.cam.initialise()

        self.init_ui(parent)


    def init_ui(self, parent):
        # Create window and layout
        if parent is None:
            app = QApplication(sys.argv)

        self.win = QWidgetMod(self.cam)
        self.vbox = QVBoxLayout(self.win)
        self.camset = CamSet(self.win, self.cam)
        self.saveas = SaveAs(self.win, self.cam)
        self.record = RecordControls(self.win, self.cam)


        self.vbox.addWidget(self.camset)
        self.vbox.addWidget(self.saveas)
        self.vbox.addWidget(self.record)

        # Finalise window
        self.win.setWindowTitle('VideoEditGui')
        self.screen_size = app.primaryScreen().size()

        self.win.setGeometry(int(self.screen_size.width()*7/8), int(self.screen_size.height()*1/8), 200, 100)

        self.win.setLayout(self.vbox)
        self.win.show()

        self.record.grab_callback()
        if parent is None:
            sys.exit(app.exec_())

class CamSet(QWidget):
    def __init__(self, parent, cam):
        self.parent = parent
        self.cam=cam
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.camset_button = QPushButton("Camera Settings")
        self.camset_button.clicked.connect(self.camset_callback)
        self.layout().addWidget(self.camset_button)

    def camset_callback(self):
        self.camset = CameraSettingsGUI(self.cam, parent=self.parent)


class SaveAs(QWidget):
    def __init__(self, parent, cam):
        self.parent=parent
        self.cam = cam
        QWidget.__init__(self, parent)
        self.saveas_filename = self.cam.filename_base
        self.setLayout(QVBoxLayout())
        self.saveas_button=QPushButton("Save as")
        self.save_button = QPushButton("Save")
        self.saveas_button.clicked.connect(self.saveas_callback)
        self.save_button.clicked.connect(self.save_callback)
        self.saveas_lbl=QLabel(self.saveas_filename)
        self.layout().addWidget(self.saveas_button)
        self.layout().addWidget(self.saveas_lbl)
        self.layout().addWidget(self.save_button)


    def saveas_callback(self):
        full_filename = save_filename(caption="Choose base pathname",
                                     directory="", parent=self.parent)
        self.saveas_filename = full_filename.split('.')[0]
        self.cam.filename_base = self.saveas_filename

    def save_callback(self):
        vid=VideoCutter(self.parent, self.cam, filename=self.cam.filename_base)


class RecordControls(QWidget):
    def __init__(self, parent, cam):
        self.cam = cam
        self.saveas_filename = self.cam.filename_base
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())

        self.snap = QPushButton("Snap")
        self.snap.clicked.connect(self.snap_callback)
        self.grab = QPushButton("Grab")
        self.grab.clicked.connect(self.grab_callback)
        self.grab.setCheckable(True)
        self.trigger = QPushButton("Trigger")
        self.trigger.setCheckable(True)
        self.trigger.clicked.connect(self.trigger_callback)
        self.layout().addWidget(self.snap)
        self.layout().addWidget(self.grab)
        self.layout().addWidget(self.trigger)

    def snap_callback(self):
        self.cam.snap()

    def grab_callback(self):
        self.cam.grab()
        self.grab.setChecked(True)
        self.trigger.setChecked(False)

    def trigger_callback(self):
        self.cam.trigger()
        self.trigger.setChecked(True)
        self.grab.setChecked(False)


if __name__ == '__main__':
    cam = CameraControlGui()