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

        self.led_hbox = QHBoxLayout()
        self.led_intensity_hbox = QHBoxLayout()
        self.upload_hbox = QHBoxLayout()
        self.display_hbox = QHBoxLayout()
        self.framerate_hbox = QHBoxLayout()


        self.red_led_checkbox()
        self.green_led_checkbox()
        self.blue_led_checkbox()
        self.intensity = 0
        self.led_intensity_slider()
        self.framerate = 100
        self.image_framerate_textbox()
        self.filename='test'
        self.upload_button()
        self.display=0
        self.display_off_toggle()
        self.display_on_toggle()
        self.display_cycle_toggle()

        self.led_hbox.addWidget(self.red_led)
        self.led_hbox.addWidget(self.green_led)
        self.led_hbox.addWidget(self.blue_led)
        self.led_intensity_hbox.addWidget(self.led_intensity_lblB)
        self.led_intensity_hbox.addWidget(self.led_intensity)
        self.framerate_hbox.addWidget((self.image_framerate))
        self.upload_hbox.addWidget(self.upload_images)
        self.display_hbox.addWidget(self.display_off)
        self.display_hbox.addWidget(self.display_on)
        self.display_hbox.addWidget(self.display_cycle)



        widget.setLayout(self.led_hbox)
        widget2.setLayout(self.led_intensity_hbox)
        widget5.setLayout(self.framerate_hbox)
        widget3.setLayout(self.upload_hbox)
        widget4.setLayout(self.display_hbox)

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

    def red_led_checkbox(self):
        self.red_led = QCheckBox("red")
        self.red_led.stateChanged.connect(self.red_led_callback)

    def red_led_callback(self):
        pass

    def green_led_checkbox(self):
        self.green_led = QCheckBox("green")
        self.green_led.stateChanged.connect(self.green_led_callback)

    def green_led_callback(self):
        pass

    def blue_led_checkbox(self):
        self.blue_led = QCheckBox("blue")
        self.blue_led.stateChanged.connect(self.blue_led_callback)

    def blue_led_callback(self):
        pass

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

    def display_off_toggle(self):
        #0
        self.display_off = QPushButton("Display Off")
        self.display_off.setCheckable(True)
        self.display_off.clicked[bool].connect(self.display_off_callback)

    def display_on_toggle(self):
        #1
        self.display_on = QPushButton("Display On")
        self.display_on.setCheckable(True)
        self.display_on.clicked[bool].connect(self.display_on_callback)

    def display_cycle_toggle(self):
        #2
        self.display_cycle = QPushButton("Display Cycle")
        self.display_cycle.setCheckable(True)
        self.display_cycle.clicked[bool].connect(self.display_cycle_callback)

    def display_off_callback(self, pressed):
        self.display_on.setChecked(False)
        self.display_cycle.setChecked(False)

    def display_on_callback(self):
        self.display_off.setChecked(False)
        self.display_cycle.setChecked(False)

    def display_cycle_callback(self):
        self.display_on.setChecked(False)
        self.display_off.setChecked(False)

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




if __name__ == '__main__':
    dmd = DMDGui()