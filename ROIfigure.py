from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
from PyQt5.QtWidgets import (QVBoxLayout, QDialog,QPushButton)
from Generic.pyqt5_widgets import MatplotlibFigure
import time


class ROIGraphDialog(QDialog):
    def __init__(self, parent,cam):
        self.cam = cam
        QDialog.__init__(self, parent)
        self.vbox = QVBoxLayout(self)
        self.mpl = ROIGraph(self,self.cam)
        self.roi_region_button = QPushButton("Select ROI Region", default = False, autoDefault = False)
        self.roi_region_button.setCheckable(True)
        self.roi_region_button.clicked[bool].connect(self.roi_region_callback)
        self.vbox.addWidget(self.mpl)
        self.vbox.addWidget(self.roi_region_button)
        self.setWindowTitle('Draw an ROI')
        self.setLayout(self.vbox)
        self.show()

    def roi_region_callback(self):
        frame = [self.mpl.RoiFig.xoff,self.mpl.RoiFig.yoff,self.mpl.RoiFig.width,self.mpl.RoiFig.height]
        self.roi_full_input(frame)
        print('ROI region callback')

    def roi_full_input(self,frame):
        if self.cam.camset.write_single_cam_command('frameformat', frame):
            self.cam.resource_cleanup()
            self.cam.reset_display()
            for i in [2,3]:
                self.cam.camset.write_single_fg_command('frameformat',frame[i],i)
            self.cam.initialise()
            self.cam.grab()

class ROIGraph(MatplotlibFigure):
    def __init__(self, parent,cam):
        MatplotlibFigure.__init__(self, parent)
        self.cam = cam
        self.setup_axes()
        self.initial_plot()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(111)

    def initial_plot(self):
        max = [0 ,0 , self.cam.camset.cam_dict['frameformat'][3][2][1],self.cam.camset.cam_dict['frameformat'][3][3][1]]
        ROIGraphDialog.roi_full_input(self,max)
        time.sleep(0.1)
        nImg = self.cam.snap_max_array()
        self.ax.imshow(nImg,cmap='gray')
        self.RoiFig = ROIfigure(self.ax)




class ROIfigure():

    def __init__(self,axes):
        self.ax = axes
        self.rec = self.CreateRectangle()
        self.rec.to_draw.set_visible(True)

    def CreateRectangle(self):
        rec = RectangleSelector(self.ax, self.rectangle_callback, drawtype= 'box'
                                , useblit= False, button= [1,3], minspanx=5, minspany=5,
                                spancoords='data', interactive = True)
        return rec

    def rectangle_callback(self,eclick,erelease):
        self.x1, self.y1 = eclick.xdata, eclick.ydata
        self.x2, self.y2 = erelease.xdata, erelease.ydata
        self.width = self.roundx(16,self.x2 - self.x1)
        self.height = int(self.y2 - self.y1)
        self.xoff = self.roundx(8,self.x1)
        self.yoff = int(self.y1)
        self.rec.extents = (self.xoff, self.xoff + self.width, self.yoff, self.yoff + self.height)
        print(self.xoff,self.yoff,self.width,self.height)

    def roundx(self,rnum,num):
        res = int(round(num/rnum)*rnum)
        return res




if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111)
    arr = np.random.rand(1024,1280)
    ax.imshow(arr,cmap='gray')
    roi = ROIfigure(ax)
    plt.show()