from task import Ui_MainWindow
import os
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QComboBox, QMainWindow, QApplication
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pydicom as dicom
import numpy as np
import matplotlib.lines as lines
import math
import itertools
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from math import pi


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.browseButton=self.ui.browseButton
        
        self.browseButton.clicked.connect(self.Browse)
        #self.ui.combobox.currentIndexChanged.connect(self.changeAction)
        self.ui.spin.setValue(3)
        self.ui.spin.valueChanged.connect(self.changePointsNumber)
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
        
        
        self.res=0
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


        self.painter = QPainter()
        self.path = QPainterPath()
        self.count=0
        self.x2=0
    
    def changePointsNumber(self):
        if self.ui.spin.value() <3:
            self.ui.spin.setValue(3)


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
        
        self.res=slices[0].PixelSpacing
        
        print(self.res)
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
        self.fig.canvas.mpl_connect("button_press_event", self.changeAction)
        self.x1=False
        self.y1=False

        self.clicknum=0

        self.Pol_x_coords=[]
        self.Pol_y_coords=[]

        self.ang_clicknum=0
        self.ang_x_coords=[]
        self.ang_y_coords=[]
        
        self.fig2.canvas.draw_idle()
        self.fig2.canvas.flush_events()
        self.sid2 = self.fig2.canvas.mpl_connect('pick_event', self.clickonline)
        self.fig3.canvas.draw_idle()
        self.fig3.canvas.flush_events()
        self.sid3 = self.fig3.canvas.mpl_connect('pick_event', self.clickonline)
    

    def changeAction(self,event):
        value=self.ui.combobox.currentIndex()
        print(value)
        if value == 0:
            self.drawLine(event)
        elif value==1:
            self.angleOf2Lines(event)
        elif value==2:
            self.drawPol(event)
        elif value == 3:
            self.drawElipse(event)


    def drawElipse(self,event):
       if self.count==0:
            print('first click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
        
            self.ax1.plot(event.xdata, event.ydata, ',')
            self.x1=round(event.xdata)
            self.y1=round(event.ydata)
            self.count+=1
       elif self.count==1 : 
            print('second click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
        
            self.ax1.plot(event.xdata, event.ydata, ',')
            self.x2=round(event.xdata)
            #print(x2)
            y2=round(event.ydata)
            self.count+=1
       elif self.count==2 : 
            print('third click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
        
            self.ax1.plot(event.xdata, event.ydata, ',')
            x3=round(event.xdata)
            y3=round(event.ydata)     
            self.fig.canvas.draw()
            u=self.x1     #x-position of the center
            v=self.y1    #y-position of the center
            a=abs(self.x2-u)     #radius on the x-axis
            b=abs(y3-v)    #radius on the y-axis
            area=a*b*pi
            print("ellipse area =")
            text="area: "+str(area)
            self.ui.results.setText(text)
            t = np.linspace(0, 2*pi, 100)
            plt.plot( u+a*np.cos(t) , v+b*np.sin(t) )
            plt.grid(color='lightgray',linestyle='--')
            self.count=0
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()


    def angleOf2Lines(self,event):
        n=3
        #self.clicknum=0
        if self.ang_clicknum < n:
            print(str(self.ang_clicknum+1)+' click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
            self.ax1.plot(event.xdata, event.ydata, ',')
            self.ang_x_coords.append(int(event.xdata))
            self.ang_y_coords.append(int(event.ydata))
            
            self.ang_clicknum=self.ang_clicknum+1

            if self.ang_clicknum>1:
                line = lines.Line2D((self.ang_x_coords[self.ang_clicknum-2],self.ang_x_coords[self.ang_clicknum-1]),(self.ang_y_coords[self.ang_clicknum-2],self.ang_y_coords[self.ang_clicknum-1]),picker=2,color='r')
                self.ax1.add_line(line)
                
                
            if self.ang_clicknum==n:
                lineA = ((self.ang_x_coords[1], self.ang_y_coords[1]), (self.ang_x_coords[0], self.ang_y_coords[0]))
                lineB = ((self.ang_x_coords[1], self.ang_y_coords[1]), (self.ang_x_coords[2], self.ang_y_coords[2]))

                # slope1 = self.slope(lineA[0][0], lineA[0][1], lineA[1][0], lineA[1][1])
                # slope2 = self.slope(lineB[0][0], lineB[0][1], lineB[1][0], lineB[1][1])

                # ang = self.angle(slope1, slope2)
                ang = self.ang(lineB,lineA)
                self.ang_clicknum=0
                self.ang_x_coords=[]
                self.ang_y_coords=[]
                print('Angle in degrees = ', ang)
                text="Angle: "+str(ang)
                self.ui.results.setText(text)
                

        self.fig.canvas.draw()

    def dot(self,vA, vB):
        return vA[0]*vB[0]+vA[1]*vB[1]

    def ang(self,lineA, lineB):
        # Get nicer vector form
        vA = [(lineA[0][0]-lineA[1][0]), (lineA[0][1]-lineA[1][1])]
        vB = [(lineB[0][0]-lineB[1][0]), (lineB[0][1]-lineB[1][1])]
        # Get dot prod
        dot_prod = self.dot(vA, vB)
        # Get magnitudes
        magA = self.dot(vA, vA)**0.5
        magB = self.dot(vB, vB)**0.5
        # Get cosine value
        cos_ = dot_prod/magA/magB
        # Get angle in radians and then convert to degrees
        angle = math.acos(dot_prod/magB/magA)
        # Basically doing angle <- angle mod 360
        ang_deg = math.degrees(angle)%360
        
        if ang_deg-180>=0:
            # As in if statement
            return 360 - ang_deg
        else: 
            
            return ang_deg


    def slope(self,x1, y1, x2, y2): # Line slope given two points:
        return (y2-y1)/(x2-x1)

    def angle(self,s1, s2): 
        return math.degrees(math.atan((s2-s1)/(1+(s2*s1))))

    def drawPol(self,event):
        n=self.ui.spin.value()
        #self.clicknum=0
        if self.clicknum<n:
            print(str(self.clicknum+1)+' click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
            self.ax1.plot(event.xdata, event.ydata, ',')
            self.Pol_x_coords.append(int(event.xdata))
            self.Pol_y_coords.append(int(event.ydata))
            print(len(self.Pol_y_coords))
            self.clicknum=self.clicknum+1
        
            if self.clicknum>1:
                
                line = lines.Line2D((self.Pol_x_coords[self.clicknum-2],self.Pol_x_coords[self.clicknum-1]),(self.Pol_y_coords[self.clicknum-2],self.Pol_y_coords[self.clicknum-1]),picker=2,color='r')
                self.ax1.add_line(line)
                
            if self.clicknum==n:
                line = lines.Line2D((self.Pol_x_coords[self.clicknum-1],self.Pol_x_coords[0]),(self.Pol_y_coords[self.clicknum-1],self.Pol_y_coords[0]),picker=2,color='r')
                self.ax1.add_line(line)
                area = self.polygonArea(self.Pol_x_coords,self.Pol_y_coords,n)
                self.clicknum=0
                self.Pol_x_coords=[]
                self.Pol_y_coords=[]
                print("area of polygon is "+str(area))
                text="Area: "+str(area)
                self.ui.results.setText(text)

        self.fig.canvas.draw()



    def polygonArea(self,X, Y, n):
 
        # Initialize area
        area = 0.0
    
        # Calculate value of shoelace formula
        j = n - 1
        for i in range(0,n):
            area += (X[j] + X[i]) * (Y[j] - Y[i])
            j = i   # j is previous vertex to i
        
    
        # Return absolute value
        return int(abs(area / 2.0))

    
    def drawLine(self,event):
        if self.x1==False:
            print('first click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
        
            self.ax1.plot(event.xdata, event.ydata, ',')
            self.x1=round(event.xdata)
            self.y1=round(event.ydata)
        else: 
            print('second click button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            (event.button, event.x, event.y, event.xdata, event.ydata))
        
            self.ax1.plot(event.xdata, event.ydata, ',')
            x2=round(event.xdata)
            y2=round(event.ydata)
            line = lines.Line2D((self.x1,x2),(self.y1,y2),picker=2,color='r')

            self.ax1.add_line(line)
            length=math.sqrt(((x2-self.x1)*self.res[0])**2+((y2-self.y1)*self.res[1])**2)
            print("the line length = "+str(length)+" mm/pixel")
            text="Length: "+str(length)+"mm/pixel"
            self.ui.results.setText(text)
            self.x1=False
            self.y1=False
        
        self.fig.canvas.draw()

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
        # if self.o==self.vertical_line3 or self.o==self.horizintal_line3 :
        #     self.follower3 = self.fig4.canvas.mpl_connect("motion_notify_event", self.followmouse)
        #     self.releaser3 = self.fig4.canvas.mpl_connect("button_press_event", self.releaseonclick)

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
