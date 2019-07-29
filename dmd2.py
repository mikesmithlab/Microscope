from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton, QCheckBox, QLineEdit)
from Generic.pyqt5_widgets import CheckedSlider
from Generic.filedialogs import open_directory

import sys

class DMDGui:
    def __init__(self):
        self.init_ui()

    def init_ui(self):
        # Create window and layout
        app = QApplication(sys.argv)
        self.win = QWidget()
        self.vbox = QVBoxLayout(self.win)

        led_chooser = LEDselector(self.win)
        display_chooser = DisplaySelector(self.win)
        rate_chooser = PatternRateSelector(self.win)
        file_chooser = FileSelector(self.win)

        self.vbox.addWidget(led_chooser)
        self.vbox.addWidget(display_chooser)
        self.vbox.addWidget(rate_chooser)
        self.vbox.addWidget(file_chooser)



        # Finalise window
        self.win.setWindowTitle('DMD Control Gui')
        self.win.setLayout(self.vbox)
        self.win.show()
        sys.exit(app.exec_())

    def upload_button(self):
        self.upload_filename_lblB = QLabel()
        self.upload_filename_lblB.setText(self.filename)
        self.upload_images = QPushButton("Upload Images")
        self.upload_images.clicked.connect(self.upload_callback)

    def upload_callback(self):
        pass

    def display_chooser_callback(self, display_off, display_on, display_cycle):
        print(display_off, display_on, display_cycle)



    def image_framerate_textbox(self):
        self.image_framerate = QLineEdit()
        self.image_framerate.setText("Framerate")
        self.image_framerate.textChanged[str].connect(self.image_framerate_callback)

    def image_framerate_callback(self):
        self.framerate = int(self.image_framerate.text())




    def add_button(self):
        # Add Save Button
        widget = QWidget()
        hbox = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.on_click)
        hbox.addWidget(self.saveButton)
        widget.setLayout(hbox)
        self.vbox.addWidget(widget)

class LEDselector(QWidget):

    def __init__(self, parent):
        self.redval = 0
        self.greenval = 0
        self.blueval = 0

        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())

        self.red_led = CheckedSlider(parent,"red", self.red_led_val, start=0, end=100, dpi=1, initial=self.redval)
        self.green_led = CheckedSlider(parent,"green", self.green_led_val, start=0, end=100, dpi=1, initial=self.greenval)
        self.blue_led = CheckedSlider(parent,"blue", self.blue_led_val, start=0, end=100, dpi=1, initial=self.blueval)

        self.layout().addWidget(self.red_led)
        self.layout().addWidget(self.green_led)
        self.layout().addWidget(self.blue_led)

    def red_led_val(self, redval):
        if self.red_led.check:
            self.red_led.slider.setEnabled(True)
            self.redval = redval
        else:
            self.red_led.slider.setEnabled(False)

    def green_led_val(self, greenval):
        if self.green_led.check:
            self.green_led.slider.setEnabled(True)
            self.greenval = greenval
        else:
            self.green_led.slider.setEnabled(False)

    def blue_led_val(self, blueval):
        if self.blue_led.check:
            self.blue_led.slider.setEnabled(True)
            self.blueval = blueval
        else:
            self.blue_led.slider.setEnabled(False)




class DisplaySelector(QWidget):

    def __init__(self, parent):
        self.off = True
        self.on = False
        self.cycle = False

        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())

        self.display_off = QPushButton("off")
        self.display_off.setCheckable(True)
        self.display_off.clicked[bool].connect(self.display_off_callback)

        self.display_on = QPushButton("on")
        self.display_on.setCheckable(True)
        self.display_on.clicked[bool].connect(self.display_on_callback)

        self.display_cycle = QPushButton("cycle")
        self.display_cycle.setCheckable(True)
        self.display_cycle.clicked[bool].connect(self.display_cycle_callback)

        self.call_function()

        self.layout().addWidget(self.display_off)
        self.layout().addWidget(self.display_on)
        self.layout().addWidget(self.display_cycle)

    def display_off_callback(self, state):
        self.off = True
        self.on = False
        self.cycle = False
        self.call_function()

    def display_on_callback(self, state):
        self.on = True
        self.off = False
        self.cycle = False
        self.call_function()

    def display_cycle_callback(self, state):
        self.cycle = True
        self.off = False
        self.on = False
        self.call_function()

    def call_function(self):
        self.display_off.setChecked(self.off)
        self.display_on.setChecked(self.on)
        self.display_cycle.setChecked(self.cycle)
        #self.function(self.off, self.on, self.cycle)

class PatternRateSelector(QWidget):
    def __init__(self, parent, rate=100, exposure=10, triggered=False):
        QWidget.__init__(self, parent)
        self.rate_val=str(rate)
        self.exposure_val=str(exposure)
        self.triggered_val=triggered

        self.directory = 'None Selected'
        self.parent = parent
        hbox = QHBoxLayout()

        self.rate = QLineEdit()
        self.rate.setText(self.rate_val)
        self.rate.returnPressed.connect(self.rate_callback)
        self.rate_lbl = QLabel('Rate (Hz)')
        self.exposure = QLineEdit()
        self.exposure.setText(self.exposure_val)
        self.exposure.returnPressed.connect(self.exposure_callback)
        self.exposure_lbl = QLabel('Exposure (us)')
        self.triggered = QCheckBox()
        self.triggered.setChecked(self.triggered_val)
        self.triggered.stateChanged.connect(self.triggered_callback)
        self.triggered_lbl = QLabel('Triggered')

        layout_rate = QVBoxLayout()
        layout_exposure = QVBoxLayout()
        layout_triggered = QVBoxLayout()
        hbox.addLayout(layout_rate)
        hbox.addLayout(layout_exposure)
        hbox.addLayout(layout_triggered)

        layout_rate.addWidget(self.rate_lbl)
        layout_rate.addWidget(self.rate)
        layout_exposure.addWidget(self.exposure_lbl)
        layout_exposure.addWidget(self.exposure)
        layout_triggered.addWidget(self.triggered_lbl)
        layout_triggered.addWidget(self.triggered)

        self.setLayout(hbox)

    def rate_callback(self):
        value = self.rate.text()
        print(value)

    def exposure_callback(self):
        value = self.exposure.text()
        print(value)

    def triggered_callback(self, state):
        self.triggered_val = bool(self.triggered.checkState())
        print(self.triggered_val)
        if self.triggered_val:
            self.rate.setEnabled(False)
        else:
            self.rate.setEnabled(True)

        

class FileSelector(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.directory = 'None Selected'
        self.parent = parent
        self.setLayout(QHBoxLayout())

        self.load_file_button = QPushButton("Load Patterns")
        self.load_file_button.clicked[bool].connect(self.load_file_callback)
        self.load_file_label = QLabel(self)
        self.load_file_label.setText(self.directory)

        self.layout().addWidget(self.load_file_button)
        self.layout().addWidget(self.load_file_label)

    def load_file_callback(self):
        directory = open_directory(caption='Select images', directory='/opt/Microscope/DMD/', parent=self.parent)
        self.directory = directory
        print(self.directory)
        self.load_file_label.setText(self.directory)




if __name__ == '__main__':
    dmd = DMDGui()