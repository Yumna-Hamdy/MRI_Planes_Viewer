from task import Ui_MainWindow
import os
from PyQt5 import QtWidgets,QtGui,QtCore
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pydicom as dicom
import numpy as np
import matplotlib.lines as lines
import itertools

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.browseButton=self.ui.browseButton
        self.browseButton.clicked.connect(self.Browse)
        self.fig,self.ax1 = plt.subplots(1,1)
        plt.axis('off')
        self.axial=self.ui.axial
        self.lay = QtWidgets.QVBoxLayout(self.axial) #
        self.plotWidget = FigureCanvas(self.fig)
        self.fig2,self.ax2 = plt.subplots(1,1)
        plt.axis('off')
        self.sagital=self.ui.sagital
        self.lay2 = QtWidgets.QVBoxLayout(self.sagital) #
        self.plotWidget2 = FigureCanvas(self.fig2)
        
        

        self.fig4,self.ax4 = plt.subplots(1,1)
        plt.axis('off')
        self.threeD=self.ui.threeD
        self.lay4 = QtWidgets.QVBoxLayout(self.threeD) #
        self.plotWidget4 = FigureCanvas(self.fig4)
        
        self.fig3,self.ax3 = plt.subplots(1,1)
        plt.axis('off')
        self.coronal=self.ui.sa
        self.lay3 = QtWidgets.QVBoxLayout(self.coronal) #
        self.plotWidget3 = FigureCanvas(self.fig3)
        self.images = [None,None,None,None]
        self.ui.dial.setValue(90)
        self.angel=45
        self.ui.dial.valueChanged.connect(self.changeAngel)
        self.clicked=0
    def changeAngel(self):
        c=self.diagonal_line.get_ydata()[0]-(np.tan(self.angel)*self.diagonal_line.get_xdata()[1])
        print(c)
        self.angel=self.ui.dial.value()/2
        print(self.angel)
        if self.angel==90:
            self.angel=89
        if self.angel==0:
            self.angel=1
        angel_cosine=np.tan(self.angel)

        if (angel_cosine<0):
            angel_cosine=-1*angel_cosine
        val=(self.diagonal_line.get_xdata()[1]+1)*angel_cosine
        

        self.diagonal_line.set_ydata([val,0])
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
    def Browse(self):
        filenames = QtWidgets.QFileDialog().getExistingDirectory(options=QtWidgets.QFileDialog.DontUseNativeDialog)
        ctImages=os.listdir(filenames)
        # Load the Dicom files
        slices = [dicom.read_file(filenames+'/'+s,force=True) for s in ctImages]
        slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])
        #create 3D  array
        imgShape = list(slices[0].pixel_array.shape)
        imgShape.append(len(slices))
        self.volume3d=np.zeros(imgShape)

        #fill 3D array with  the images from the files
        for i,s in enumerate(slices):
            array2D=s.pixel_array
            self.volume3d[:,:,i]= array2D
        print(i)
        self.images[0] = self.volume3d[:,:,i//2]
        self.images[1] = np.rot90(self.volume3d[:,i,:])
        self.images[2] = np.rot90(self.volume3d[i,:,:],1)
        
        #self.images[3] = self.volume3d[:,:,i]
        self.lay.addWidget(self.plotWidget)
        self.ax1.imshow(self.images[0], cmap='gray')
        # self.ax1.axhline(y = 100, color = 'r', linestyle = '-')
        # self.ax1.axvline(y = 100, color = 'r', linestyle = '-')
        self.lay2.addWidget(self.plotWidget2)
        self.ax2.imshow(self.images[1], cmap='gray')
        self.lay3.addWidget(self.plotWidget3)
        self.ax3.imshow(self.images[2], cmap='gray')
        self.lay4.addWidget(self.plotWidget4)
        ##self.fig.canvas.draw()
        self.show()
        
        
        self.horizintal_line = lines.Line2D((0,512),(256,256),picker=2)
        self.vertical_line = lines.Line2D((256,256),(0,512),picker=2)
        self.diagonal_line = lines.Line2D((0,512),(512,0),picker=2)

        self.ax1.add_line(self.horizintal_line)
        self.ax1.add_line(self.vertical_line)
        self.ax1.add_line(self.diagonal_line)

        self.horizintal_line2 = lines.Line2D((0,512),(128,128),picker=2)
        self.vertical_line2 = lines.Line2D((256,256),(0,512),picker=2)

        self.ax2.add_line(self.horizintal_line2)
        self.ax2.add_line(self.vertical_line2)
        self.horizintal_line3 = lines.Line2D((0,512),(128,128),picker=2)
        self.vertical_line3 = lines.Line2D((256,256),(0,512),picker=2)

        self.ax3.add_line(self.horizintal_line3)
        self.ax3.add_line(self.vertical_line3)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.sid = self.fig.canvas.mpl_connect('pick_event', self.clickonline)

        self.fig2.canvas.draw_idle()
        self.fig2.canvas.flush_events()
        self.sid2 = self.fig2.canvas.mpl_connect('pick_event', self.clickonline)
        self.fig3.canvas.draw_idle()
        self.fig3.canvas.flush_events()
        self.sid3 = self.fig3.canvas.mpl_connect('pick_event', self.clickonline)

    def clickonline(self, event):
        self.o=event.artist
        # if event.artist == self.line:
        #     print("line selected ", event.artist)
        if self.o==self.vertical_line or self.o==self.horizintal_line or self.o==self.diagonal_line:
            self.follower = self.fig.canvas.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser = self.fig.canvas.mpl_connect("button_press_event", self.releaseonclick)
        if self.o==self.vertical_line2 or self.o==self.horizintal_line2 :
            self.follower2 = self.fig2.canvas.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser2 = self.fig2.canvas.mpl_connect("button_press_event", self.releaseonclick)
        if self.o==self.vertical_line3 or self.o==self.horizintal_line3 :
            self.follower3 = self.fig3.canvas.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser3 = self.fig3.canvas.mpl_connect("button_press_event", self.releaseonclick)

        # self.follower = self.fig2.canvas.mpl_connect("motion_notify_event", self.followmouse)
        # self.releaser = self.fig2.canvas.mpl_connect("button_press_event", self.releaseonclick)


    def followmouse(self, event):
        if self.o == self.horizintal_line:
            self.horizintal_line.set_ydata([event.ydata, event.ydata])
            self.coronal=np.rot90(self.volume3d[round(event.ydata),:,:])
            self.ax3.imshow(self.coronal,cmap='gray')
            self.fig3.canvas.draw_idle()
            self.fig3.canvas.flush_events()
        if self.o == self.vertical_line:
            self.vertical_line.set_xdata([event.xdata, event.xdata])
            self.sagital=np.rot90(self.volume3d[:,round(event.xdata),:])
            self.ax2.imshow(self.sagital,cmap='gray')
            self.fig2.canvas.draw_idle()
            self.fig2.canvas.flush_events()
        if self.o == self.diagonal_line:
            #self.diagonal_line.set_alpha(self.angel/180)
            coor=(event.xdata+event.ydata)

            print("xdata",event.xdata)
            print("ydata",event.ydata)
            self.diagonal_line.set_xdata([0, coor])
            self.diagonal_line.set_ydata([coor, 0])
            c=self.diagonal_line.get_ydata()[0]-(np.tan(self.angel)*self.diagonal_line.get_xdata()[1])
            print(c)

            self.angel=self.ui.dial.value()/2
            print(self.angel)
            if self.angel==90:
                self.angel=89
            if self.angel==0:
                self.angel=1
            angel_cosine=np.tan(self.angel)

            if (angel_cosine<0):
                angel_cosine=-1*angel_cosine
            val=(self.diagonal_line.get_xdata()[1]+1)*angel_cosine
            

            self.diagonal_line.set_ydata([val,0])
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        if self.o == self.horizintal_line2:
            self.horizintal_line2.set_ydata([event.ydata, event.ydata])
            #not sure of 115
            self.axial=(self.volume3d[:,:,round(event.ydata)-115])
            self.ax1.imshow(self.axial,cmap='gray')
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        elif self.o == self.vertical_line2:
            self.vertical_line2.set_xdata([event.xdata, event.xdata])
            self.sagital2=np.rot90(self.volume3d[round(event.xdata),:,:])
            self.ax3.imshow(self.sagital2,cmap='gray')
            self.fig3.canvas.draw_idle()
            self.fig3.canvas.flush_events()
        if self.o == self.horizintal_line3:
            self.horizintal_line3.set_ydata([event.ydata, event.ydata])
            self.axial2=(self.volume3d[:,:,self.volume3d.shape[2]-round(event.ydata)-1])
            self.ax1.imshow(self.axial2,cmap='gray')
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        elif self.o == self.vertical_line3:
            self.vertical_line3.set_xdata([event.xdata, event.xdata])
            self.coronal2=np.rot90((self.volume3d[:,round(event.xdata),:]))
            self.ax2.imshow(self.coronal2,cmap='gray')
            self.fig2.canvas.draw_idle()
            self.fig2.canvas.flush_events()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.fig2.canvas.draw_idle()
        self.fig2.canvas.flush_events()
        self.fig3.canvas.draw_idle()
        self.fig3.canvas.flush_events()

        # self.fig2.canvas.draw_idle()
        # self.fig2.canvas.flush_events()
        # self.update_image(self.horizintal_line.get_ydata()[1])
    def get_line(self,x1, y1, x2, y2):
        points = []
        issteep = abs(y2-y1) > abs(x2-x1)
        if issteep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        deltax = x2 - x1
        deltay = abs(y2-y1)
        error = int(deltax / 2)
        y = y1
        ystep = None
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax
    # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points
    def releaseonclick(self, event):
        if self.o == self.horizintal_line:
            self.XorY = self.horizintal_line.get_ydata()[0]
        elif self.o ==self.vertical_line:
            self.XorY = self.vertical_line.get_xdata()[0]
        elif self.o ==self.diagonal_line:
            #self.diagonal_line.set_alpha(self.angel/180)

            self.X1 = round(self.diagonal_line.get_xdata()[0])
            self.X2 = round(self.diagonal_line.get_xdata()[1])
            self.Y1 = round(self.diagonal_line.get_ydata()[0])
            self.Y2 = round(self.diagonal_line.get_ydata()[1])
            
            self.m=(self.Y2-self.Y1)/(self.X2-self.X1)
            self.c=self.Y1-self.m*self.X1
            #self.Y=self.m*self.X+self.c
            self.val=self.get_line(self.X1,self.Y1,self.X2,self.Y2)
            self.rowArray=[]
            self.obliquImage=np.zeros((len(self.val),self.volume3d.shape[2]))
            print(self.obliquImage.shape)
            #print(self.volume3d.shape)
            for z in range(self.volume3d.shape[2]):
                for i in range(len(self.val)):
                    if self.val[i][0]<=512 and self.val[i][1]<=512:
                        self.obliquImage[i,z]=int(self.volume3d[self.val[i][1]-1,self.val[i][0]-1,z])
                    
            print(type(self.obliquImage))
            self.ax4.imshow(np.rot90(self.obliquImage),cmap='gray')
            self.fig4.canvas.draw_idle()
            self.fig4.canvas.flush_events()
           


            #print(self.val)
        if self.o==self.horizintal_line or self.o==self.vertical_line or self.o==self.diagonal_line:
            self.fig.canvas.mpl_disconnect(self.releaser)
            self.fig.canvas.mpl_disconnect(self.follower)
        elif self.o==self.horizintal_line2 or self.o== self.vertical_line2:
            self.fig2.canvas.mpl_disconnect(self.releaser2)
            self.fig2.canvas.mpl_disconnect(self.follower2)
        elif self.o==self.horizintal_line3 or self.o== self.vertical_line3:
            self.fig3.canvas.mpl_disconnect(self.releaser3)
            self.fig3.canvas.mpl_disconnect(self.follower3)

        # self.ax1.canvas.mpl_disconnect(self.releaser)
        # self.ax1.canvas.mpl_disconnect(self.follower)
        
        
    def update_image(self,value):
        pass
        # self.images[2] = np.rot90(self.volume3d[value,:,:])
        # self.ax3.imshow(self.images[2], cmap='gray')
        # self.fig3.canvas.draw_idle()
        # self.fig3.canvas.flush_events()

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
