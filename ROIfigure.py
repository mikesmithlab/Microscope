from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np


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