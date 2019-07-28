from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton, QCheckBox, QLineEdit)
from Generic.pyqt5_widgets import CheckedSlider

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
        display_chooser = DisplaySelector(self.win, self.display_chooser_callback)
        file_chooser = FileSelector(self.win, self.file_chooser_callback)

        self.vbox.addWidget(led_chooser)
        self.vbox.addWidget(display_chooser)
        self.vbox.addWidget(file_selecter)



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

        self.red_led = CheckedSlider(parent,"red", self.red_led_val, 0, 100, 1, self.redval)
        self.green_led = CheckedSlider(parent,"green", self.green_led_val, 0, 100, 1, self.greenval)
        self.blue_led = CheckedSlider(parent,"blue", self.blue_led_val, 0, 100, 1, self.blueval)

        self.layout().addWidget(self.red_led)
        self.layout().addWidget(self.green_led)
        self.layout().addWidget(self.blue_led)

    def red_led_val(self, redval):
        if self.red_led.checked:
            self.redval = redval
        else:
            self.redval = 0
            self.red_led.slider.setSliderPosition(0)

    def green_led_val(self, greenval):
        if self.green_led.checked:
            self.greenval = greenval
        else:
            self.greenval = 0
            self.green_led.slider.setSliderPosition(0)

    def blue_led_val(self, blueval):
        if self.blue_led.checked:
            self.blueval = blueval
        else:
            self.blueval = 0
            self.blue_led.slider.setSliderPosition(0)


    def change_led_settings(self, colour, value):
        pass


class DisplaySelector(QWidget):

    def __init__(self, parent, function):
        self.off = True
        self.on = False
        self.cycle = False

        self.function = function
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
        self.function(self.off, self.on, self.cycle)

class FileSelector:
    def __init__(self, parent, function):
        

if __name__ == '__main__':
    dmd = DMDGui()