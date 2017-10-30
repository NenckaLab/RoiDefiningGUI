#! /usr/bin/env python2.7
from Tkinter import Tk, BOTH
import Tkinter as tk
from ttk import Frame, Button, Style, Scale
from tkFileDialog import askopenfilename
import nibabel
import numpy as np
import matplotlib
import sys

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Example(Frame):

    global niftiName
    global niftiImg
    global rows
    global cols
    global slices
    global thisImg1
    global thisImg2
    global thisImg3
  
    def __init__(self, parent):
        self.rowVal = 0
        self.colVal = 0
        self.sliceVal = 0

        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        
        if len(sys.argv) > 1:
            self.niftiName = sys.argv[1] #'T2Wt_NonContactSport_Day8_03150001_05_11_16.nii.gz'
            self.loadNifti()
        else:
            self.niftiName = 'T2Wt_NonContactSport_Day8_03150001_05_11_16.nii.gz'
            self.loadNifti()
        self.roiIdx = 0
        
    def initUI(self):
      
        self.parent.title("Quit button")
        self.style = Style()
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)
        
        #first fig
        fig1 = matplotlib.figure.Figure()
        ax1 = fig1.add_subplot(111)
        self.thisImg1 = np.eye(256)
        self.fig1Drawing = ax1.imshow(self.thisImg1)
        self.canvas1=FigureCanvasTkAgg(fig1,master=self.parent)
        self.canvas1.show()
        self.canvas1.get_tk_widget().place(relx=0, rely=0,\
                                           relheight=0.7, \
                                           relwidth=0.3)
        #second fig
        fig2 = matplotlib.figure.Figure()
        ax2 = fig2.add_subplot(111)
        self.thisImg2 = np.eye(256)
        self.fig2Drawing = ax2.imshow(self.thisImg2)
        self.canvas2=FigureCanvasTkAgg(fig2,master=self.parent)
        self.canvas2.show()
        self.canvas2.get_tk_widget().place(relx=0.33, rely=0, \
                                           relheight=0.7, \
                                           relwidth=0.3)
        #Thrid fig
        fig3 = matplotlib.figure.Figure()
        ax3 = fig3.add_subplot(111)
        self.thisImg3 = np.eye(256)
        self.fig3Drawing = ax3.imshow(self.thisImg3)
        self.canvas3=FigureCanvasTkAgg(fig3,master=self.parent)
        self.canvas3.show()
        self.canvas3.get_tk_widget().place(relx=0.66, rely=0, \
                                           relheight=0.7, \
                                           relwidth=0.3)

        cid1 = self.canvas1.mpl_connect('button_press_event',self.firstUpdate)
        cid2 = self.canvas2.mpl_connect('button_press_event',self.secondUpdate)
        cid3 = self.canvas3.mpl_connect('button_press_event',self.thirdUpdate)
        
        cid4 = self.canvas1.mpl_connect('key_press_event',self.writeRoi2)
        cid4 = self.canvas2.mpl_connect('key_press_event',self.writeRoi2)
        cid5 = self.canvas3.mpl_connect('key_press_event',self.writeRoi2)

        #Make the sliders
        self.rowSlider = Scale(self, \
                                   command=self.updateRow, \
                                   orient=tk.HORIZONTAL, \
                                   from_=0, \
                                   to=500)
        self.rowSlider.place(relx=0.8, rely=0.8)
        self.colSlider = Scale(self, \
                                   command=self.updateCol, \
                                   orient=tk.HORIZONTAL, \
                                   from_=0, \
                                   to=500)
        self.colSlider.place(relx=.4, rely=0.8)
        self.sliceSlider = Scale(self, \
                                     command=self.updateSlice, \
                                     orient=tk.HORIZONTAL, \
                                   from_=0, \
                                   to=500)
        self.sliceSlider.place(relx=0.0, rely=0.8)

        openButton = Button(self, text="Open",
            command=self.pickFile)
        openButton.place(relx=0,rely=.9)

        loadButton = Button(self, text="Load",
            command=self.loadNifti)
        loadButton.place(relx=.4,rely=.9)

        quitButton = Button(self, text="Quit",
            command=self.quit)
        quitButton.place(relx=.8, rely=.9)

    def pickFile(self):
        filename = askopenfilename()
        print filename
        self.niftiName = filename

    def loadNifti(self):
        self.niftiImg = nibabel.load(self.niftiName)
        self.updateImage()

    def updateImage(self):
        #print "updateImage started..."

        self.dataArr = self.niftiImg.get_data()

        thisArr1Max = np.max(self.dataArr[::,::,self.sliceVal])
        if thisArr1Max == 0:
            thisArr1Max=1
        thisArr1 = self.dataArr[::,::,self.sliceVal].astype(np.float) \
                / thisArr1Max
        thisArr1Max = np.max(self.dataArr[::,self.colVal,::])
        if thisArr1Max == 0:
            thisArr1Max = 1
        thisArr2 = self.dataArr[::,self.colVal,::].astype(np.float) \
                / thisArr1Max
        thisArr1Max = np.max(self.dataArr[self.rowVal,::,::])
        if thisArr1Max == 0:
            thisArr1Max = 1
        thisArr3 = self.dataArr[self.rowVal,::,::].astype(np.float) \
                / thisArr1Max

        self.fig1Drawing.set_data(thisArr1)
        self.fig2Drawing.set_data(thisArr2)
        self.fig3Drawing.set_data(thisArr3)

        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        
        #print "updateImage done!"

    def updateRow(self,v1):
        sliderVal = float(v1)/500. #self.rowSlider.get()
        newRow = int(np.round(np.shape(self.dataArr)[0] * sliderVal))
        self.rowVal = newRow
        #print "newRow is %i"%(newRow,)
        self.updateImage()
    def updateCol(self,v1):
        sliderVal = float(v1)/500. #self.colSlider.get()
        newCol = int(np.round(np.shape(self.dataArr)[1] * sliderVal))
        self.colVal = newCol
        #print "newCol is %i"%(newCol,)
        self.updateImage()
    def updateSlice(self,v1):
        sliderVal = float(v1)/500. #self.sliceSlider.get()
        newSlice = int(np.round(np.shape(self.dataArr)[2] * sliderVal))
        self.sliceVal = newSlice
        #print "newSlice is %i"%(newSlice,)
        self.updateImage()

    def firstUpdate(self,event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % \
        #       (event.button, event.x, event.y, event.xdata, event.ydata)
        #print np.shape(self.dataArr)
        newCol = event.xdata/256.0 * np.shape(self.dataArr)[1]
        newRow = event.ydata/256.0 * np.shape(self.dataArr)[0]
        self.rowVal=int(np.round(newRow))
        self.colVal=int(np.round(newCol))
        #print 'rowVal=%i'%(self.rowVal)
        #print 'colVal=%i'%(self.colVal)
        self.updateImage()

    def secondUpdate(self,event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % \
        #       (event.button, event.x, event.y, event.xdata, event.ydata)
        #print np.shape(self.dataArr)
        newSlice = event.xdata/256.0 * np.shape(self.dataArr)[2]
        newRow = event.ydata/256.0 * np.shape(self.dataArr)[0]
        self.rowVal=int(np.round(newRow))
        self.sliceVal=int(np.round(newSlice))
        self.updateImage()
    
    def thirdUpdate(self,event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % \
        #       (event.button, event.x, event.y, event.xdata, event.ydata)
        #print np.shape(self.dataArr)
        newSlice = event.xdata/256.0 * np.shape(self.dataArr)[2]
        newCol = event.ydata/256.0 * np.shape(self.dataArr)[1]
        self.sliceVal=int(np.round(newSlice))
        self.colVal=int(np.round(newCol))
        self.updateImage()
        
    def writeRoi(self,event):
        print 'key=%s'%(event.key)
        halfWidth = 16
        sys.stdout.flush()
        if event.key is 'w':
            startRow = self.rowVal - halfWidth
            endRow = self.rowVal+halfWidth-1
            startCol = self.colVal - halfWidth
            endCol = self.colVal +halfWidth-1
            startSlice = self.sliceVal - halfWidth
            endSlice = self.sliceVal + halfWidth -1
            
            if startRow < 0:
                startRow = 0
                print "Truncated start row"
            if endRow >= np.shape(self.dataArr)[0]:
                endRow = np.shape(self.dataArr)[0]-1
                print "Truncated end row"
                
            if startCol < 0:
                startCol = 0
                print "Truncated start col"
            if endCol >= np.shape(self.dataArr)[1]:
                endCol = np.shape(self.dataArr)[1]-1
                print "Truncated end col"
                
            if startSlice < 0:
                startSlice = 0
                print "Truncated start slice"
            if endSlice >= np.shape(self.dataArr)[2]:
                endSlice = np.shape(self.dataArr)[2]-1
                print "Truncated end slice"
            
            tmpRoi = self.dataArr[startRow:endRow:, startCol:endCol:, startSlice:endSlice:]
            
            self.cleanNiftiName = self.niftiName.replace('/','_')
            
            fileName = 'roi_%i_%s_.pic'%(self.roiIdx, self.cleanNiftiName)
            self.roiIdx += 1
            
            np.save(fileName, tmpRoi)
            
            print "Saved %s" % (fileName,)
    
    def writeRoi2(self,event):
        print 'key=%s'%(event.key)
        halfWidth = 16
        randROIs = 10
        self.rows = np.shape(self.dataArr)[0]
        self.cols = np.shape(self.dataArr)[1]
        self.slices = np.shape(self.dataArr)[2]
        eyeOffsets = [-5, 0, 5]
        sys.stdout.flush()
        if event.key is 'w':
            for rowOffset in eyeOffsets:
                for colOffset in eyeOffsets:
                    for sliceOffset in eyeOffsets:
                        for reverseIdx in xrange(0,4,1):
                            startRow = self.rowVal - halfWidth + rowOffset
                            endRow = self.rowVal+halfWidth-1 + rowOffset
                            startCol = self.colVal - halfWidth + colOffset
                            endCol = self.colVal +halfWidth-1 + colOffset
                            startSlice = self.sliceVal - halfWidth + sliceOffset 
                            endSlice = self.sliceVal + halfWidth -1 + sliceOffset
                
                            if startRow < 0:
                                startRow = 0
                                print "Truncated start row"
                            if endRow >= np.shape(self.dataArr)[0]:
                                endRow = np.shape(self.dataArr)[0]-1
                                print "Truncated end row"
                    
                            if startCol < 0:
                                startCol = 0
                                print "Truncated start col"
                            if endCol >= np.shape(self.dataArr)[1]:
                                endCol = np.shape(self.dataArr)[1]-1
                                print "Truncated end col"
                                
                            if startSlice < 0:
                                startSlice = 0
                                print "Truncated start slice"
                            if endSlice >= np.shape(self.dataArr)[2]:
                                endSlice = np.shape(self.dataArr)[2]-1
                                print "Truncated end slice"
                
                            tmpRoi = self.dataArr[startRow:endRow:, startCol:endCol:, startSlice:endSlice:]
                            if reverseIdx > 0:
                                tmpRoi = np.flip(tmpRoi,reverseIdx-1)
                
                            self.cleanNiftiName = self.niftiName.replace('/','_')
                
                            fileName = 'roi_%i_anat_%s_.pic'%(self.roiIdx, self.cleanNiftiName)
                            self.roiIdx += 1
                
                            np.save(fileName, tmpRoi)
                
                            print "Saved %s" % (fileName,)
    
                            #Make the random ROIs
                            randCentRow=self.rowVal
                            randCentCol=self.colVal
                            randCentSlice=self.sliceVal
    
                            while np.abs(randCentRow-self.rowVal) < halfWidth:
                                randCentRow = np.random.random_integers(0, self.rows - 2*halfWidth)+halfWidth
                            randStartRow = randCentRow-halfWidth
                            randEndRow = randStartRow + 2*halfWidth
                            randStartCol = np.random.random_integers(0, self.cols - 2*halfWidth)
                            
                            while np.abs(randCentCol-self.colVal) < halfWidth:
                                randCentCol = np.random.random_integers(0, self.cols - 2*halfWidth)+halfWidth
                            randStartCol = randCentCol-halfWidth
                            randEndCol = randStartCol + 2*halfWidth
    
                            while np.abs(randCentSlice-self.sliceVal) < halfWidth:
                                randCentSlice = np.random.random_integers(0, self.slices - 2*halfWidth)+halfWidth
                            randStartSlice = randCentSlice-halfWidth
                            randEndSlice = randStartSlice + 2*halfWidth
    
                            tmpRoi = self.dataArr[randStartRow:randEndRow:, \
                                                  randStartCol:randEndCol:, \
                                                  randStartSlice:randEndSlice:]
                            if reverseIdx > 0:
                                tmpRoi = np.flip(tmpRoi,reverseIdx-1)
                            
                            fileName = 'roi_%i_rand_%s_.pic'%(self.roiIdx, self.cleanNiftiName)
                            self.roiIdx += 1
            
                            np.save(fileName, tmpRoi)
            
                            print "Saved %s" % (fileName,)

def main():
  
    root = Tk()
    root.geometry("750x450+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
