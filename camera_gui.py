from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton)
import qimage2ndarray as qim
import sys
from Generic.pyqt5_widgets import QtImageViewer
from Generic.images import hstack
from Generic.filedialogs import save_filename

from microscope.camerahs import Camera
from microscope.camerasettings_gui import CameraSettingsGUI



class CameraControlGui:
    def __init__(self):
        self.cam = Camera()
        self.cam.initialise()

        self.init_ui()


    def init_ui(self):
        # Create window and layout
        app = QApplication(sys.argv)

        self.win = QWidget()
        self.vbox = QVBoxLayout(self.win)

        self.saveas = SaveAs(self.win)
        self.record = RecordControls(self.win, self.cam)


        self.camset = QPushButton("Camera Settings")
        self.camset.clicked.connect(self.camset_callback)

        self.vbox.addWidget(self.camset)
        self.vbox.addWidget(self.saveas)
        self.vbox.addWidget(self.record)


        # Finalise window
        self.win.setWindowTitle('VideoEditGui')
        self.screen_size = app.primaryScreen().size()

        self.win.setGeometry(int(self.screen_size.width()*7/8), int(self.screen_size.height()*1/4), 200, 100)
        self.camsettings_pos = (int(self.screen_size.width()*7/8),int(self.screen_size.height()*1/4)+400, 350,400)
        self.win.setLayout(self.vbox)
        self.win.show()
        sys.exit(app.exec_())

    def camset_callback(self):
        self.camsettings_gui = CameraSettingsGUI(self.camsettings_pos, parent=self.win)


class SaveAs(QWidget):
    def __init__(self, parent):
        self.parent=parent
        self.saveas_filename = "DUmmy"
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.saveas_button=QPushButton("Save as")
        self.saveas_button.clicked.connect(self.saveas_callback)
        self.saveas_lbl=QLabel(self.saveas_filename)
        self.layout().addWidget(self.saveas_button)
        self.layout().addWidget(self.saveas_lbl)

    def saveas_callback(self):
        full_filename = save_filename(caption="Choose base pathname",
                                     directory="", parent=self.parent)
        self.filename = full_filename.split('.')[0]
        print(self.filename)


class RecordControls(QWidget):
    def __init__(self, parent, cam):
        self.cam = cam
        self.saveas_filename = "DUmmy"
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())

        self.snap = QPushButton("Snap")
        self.snap.clicked.connect(self.snap_callback)
        self.trigger = QPushButton("Grab")
        self.trigger.setCheckable(True)
        self.trigger.clicked.connect(self.trigger_callback)
        self.layout().addWidget(self.snap)
        self.layout().addWidget(self.trigger)

    def snap_callback(self):
        pass

    def trigger_callback(self):
        self.cam.grab()


class CameraVidEditGui:
    def __init__(self, cam, num_imgs=2):
        self.num_imgs = num_imgs
        self.cam=cam
        self.first_frame = 1
        self.last_frame = self.cam.max_img_num
        self.edit_first_frame = self.first_frame
        self.edit_last_frame = self.last_frame
        self.imgA = self.get_img(num=self.first_frame)
        self.imgB = self.get_img(num=self.last_frame)
        self._display_img(self.imgA, self.imgB)
        self.init_ui()

    def _display_img(self, *imgs):
        self.img = hstack(*imgs)

    def _update_img(self):
        pixmap = QPixmap.fromImage(qim.array2qimage(self.img))
        self.viewer.setImage(pixmap)

    def get_img(self, num=1):
        img_ptr = SISO.Fg_getImagePtrEx(self.cam.fg, num, 0, self.cam.memHandle)
        nImg = SISO.getArrayFrom(img_ptr, self.cam.set.cam_dict['frameformat'][2][3],
                                 self.cam.set.cam_dict['frameformat'][2][2])
        return nImg

    def init_ui(self):
        # Create window and layout
        app = QApplication(sys.argv)
        self.win = QWidget()
        self.vbox = QVBoxLayout(self.win)

        # Create Image viewer
        self.viewer = QtImageViewer()
        self.viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.viewer.leftMouseButtonPressed.connect(self.get_coords)
        self.viewer.canZoom = True
        self.viewer.canPan = True
        self._update_img()
        self.vbox.addWidget(self.viewer)

        # Add sliders
        self.add_sliderA(text='first')
        self.add_sliderB(text='last', initial_val=self.last_frame)

        self.add_button()


        # Finalise window
        self.win.setWindowTitle('VideoEditGui')
        self.win.setLayout(self.vbox)
        self.win.show()
        sys.exit(app.exec_())

    def add_sliderA(self, text='', initial_val=1):
        widget = QWidget()
        hbox = QHBoxLayout()
        self.frame_lblA = QLabel()
        self.frame_lblA.setText(text + ' frame: ' + str(initial_val))

        self.frame_sliderA = QSlider(Qt.Horizontal)
        self.frame_sliderA.setRange(self.first_frame, self.last_frame)
        self.frame_sliderA.setValue(initial_val)
        self.frame_sliderA.valueChanged.connect(self._update_sliderA)
        hbox.addWidget(self.frame_lblA)
        hbox.addWidget(self.frame_sliderA)
        widget.setLayout(hbox)
        self.vbox.addWidget(widget)

    def add_sliderB(self, text='', initial_val=1):
        widget = QWidget()
        hbox = QHBoxLayout()
        self.frame_lblB = QLabel()
        self.frame_lblB.setText(text + ' frame: ' + str(initial_val))
        self.frame_sliderB = QSlider(Qt.Horizontal)
        self.frame_sliderB.setRange(self.first_frame, self.last_frame)
        self.frame_sliderB.setValue(initial_val)
        self.frame_sliderB.valueChanged.connect(self._update_sliderB)
        hbox.addWidget(self.frame_lblB)
        hbox.addWidget(self.frame_sliderB)
        widget.setLayout(hbox)
        self.vbox.addWidget(widget)

        #for key in sorted(self.param_dict.keys()):
        #widget = QWidget()
        #hbox = QHBoxLayout()

    def add_button(self):
        # Add Save Button
        widget = QWidget()
        hbox = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.on_click)
        hbox.addWidget(self.saveButton)
        widget.setLayout(hbox)
        self.vbox.addWidget(widget)


    def _update_sliderA(self):
        frameno = self.frame_sliderA.value()
        self.frame_lblA.setText('frame: ' + str(frameno))
        self.imgA = self.get_img(num=frameno)
        self.update()

    def _update_sliderB(self):
        frameno = self.frame_sliderB.value()
        self.frame_lblB.setText('frame: ' + str(frameno))
        self.imgB = self.get_img(num=frameno)
        self.update()

    def update(self):
        self._display_img(self.imgA, self.imgB)
        self._update_img()

    def get_coords(self, x, y):
        print('cursor position (x, y) = ({}, {})'.format(int(x), int(y)))

    def on_click(self, event):
        #print('test')
        self.cam.save(first=self.edit_first_frame, last=self.edit_last_frame)

if __name__ == '__main__':
    cam = CameraControlGui()