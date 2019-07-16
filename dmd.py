from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QPainterPath, QCloseEvent
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication,
                             QSlider, QHBoxLayout, QPushButton, QCheckBox, QLineEdit)

import sys

class DMDGui:
    def __init__(self):
        self.init_ui()

    def init_ui(self):
        # Create window and layout
        app = QApplication(sys.argv)
        self.win = QWidget()
        self.vbox = QVBoxLayout(self.win)

        widget=QWidget()
        widget2=QWidget()
        widget3=QWidget()
        widget4=QWidget()
        widget5=QWidget()


        self.led_intensity_hbox = QHBoxLayout()
        self.upload_hbox = QHBoxLayout()
        self.display_hbox = QHBoxLayout()
        self.framerate_hbox = QHBoxLayout()

        led_chooser = LEDselector(self.win, self.led_chooser_callback)
        self.vbox.addWidget(led_chooser)

        self.intensity = 0
        self.led_intensity_slider()
        self.framerate = 100
        self.image_framerate_textbox()
        self.filename='test'
        self.upload_button()
        self.display=0

        display_chooser = DisplaySelector(self.win, self.display_chooser_callback)
        self.vbox.addWidget(display_chooser)


        self.led_intensity_hbox.addWidget(self.led_intensity_lblB)
        self.led_intensity_hbox.addWidget(self.led_intensity)
        self.framerate_hbox.addWidget((self.image_framerate))
        self.upload_hbox.addWidget(self.upload_images)


        widget2.setLayout(self.led_intensity_hbox)
        widget5.setLayout(self.framerate_hbox)
        widget3.setLayout(self.upload_hbox)


        self.vbox.addWidget(widget)
        self.vbox.addWidget(widget2)
        self.vbox.addWidget(widget5)
        self.vbox.addWidget(widget3)
        self.vbox.addWidget(widget4)
        # Finalise window
        self.win.setWindowTitle('DMD Control Gui')
        self.win.setLayout(self.vbox)
        self.win.show()
        sys.exit(app.exec_())

    def led_chooser_callback(self, red, green, blue):
        print(red, green, blue)

    def led_intensity_slider(self):
        self.led_intensity_lblB = QLabel()
        self.led_intensity_lblB.setText('Led intensity : ' + str(self.intensity))
        self.led_intensity = QSlider(Qt.Horizontal)
        self.led_intensity.setRange(0, 100)
        self.led_intensity.setValue(self.intensity)
        self.led_intensity.valueChanged.connect(self.led_intensity_callback)
        
    def led_intensity_callback(self):
        self.intensity = self.led_intensity.value()
        self.led_intensity_lblB.setText('Led intensity : ' + str(self.intensity))

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

    def __init__(self, parent, function):
        self.red = False
        self.green = False
        self.blue = False

        self.function = function
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())

        red_led = QCheckBox("red")
        red_led.stateChanged.connect(self.red_led_callback)

        green_led = QCheckBox("green")
        green_led.stateChanged.connect(self.green_led_callback)

        blue_led = QCheckBox("blue")
        blue_led.stateChanged.connect(self.blue_led_callback)

        self.layout().addWidget(red_led)
        self.layout().addWidget(green_led)
        self.layout().addWidget(blue_led)

    def blue_led_callback(self, state):
        if state == Qt.Checked:
            self.blue = True
        else:
            self.blue = False
        self.call_function()

    def red_led_callback(self, state):
        if state == Qt.Checked:
            self.red = True
        else:
            self.red = False
        self.call_function()

    def green_led_callback(self, state):
        if state == Qt.Checked:
            self.green = True
        else:
            self.green = False
        self.call_function()

    def call_function(self):
        self.function(self.red, self.green, self.blue)


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

if __name__ == '__main__':
    dmd = DMDGui()