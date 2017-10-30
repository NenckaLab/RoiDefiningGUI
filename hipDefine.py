#! /usr/bin/env python2.7
from Tkinter import Tk, IntVar, Toplevel
from ttk import Frame, Button, Style, Checkbutton, Label
from Tkconstants import W, E
from tkFileDialog import askopenfilename
import numpy as np
import matplotlib
import dicom
import os

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Global variables
outputs = []
gridLayout = []
roiCounter = 0
prevRoi = 0
init = False

rowVal = []
localRow = 0
colVal = []
localCol = 0

class PopUp(Toplevel):
    
    def __init__(self):
        Toplevel.__init__(self)
        self.geometry("200x100+2+2")
        self.initPopup()
        
    def initPopup(self):
        self.var1 = IntVar()
        cb = Checkbutton(self, text=str("Osteolysis"), variable=self.var1)
        cb.grid(row=0, column=0, padx=15, pady=20, sticky=E)
        self.var2 = IntVar()
        cb = Checkbutton(self, text=str("Synovitis"), variable=self.var2)
        cb.grid(row=0, column=1, pady=20, sticky=W)
         
        printButton = Button(self, text="Submit", command=self.setVars)
        printButton.grid(row=1, column=0, padx=15, sticky=E)
        printButton = Button(self, text="Close", command=self.destroy)
        printButton.grid(row=1, column=1, sticky=W)
     
    def setVars(self):
        global outputs
        global roiCounter
        global localRow
        global localCol
        global rowVal
        global colVal
        
        roiCounter += 1
        colVal.append(localCol)
        rowVal.append(localRow)
        
        self.variables = []
        self.variables.append(self.var1.get())
        self.variables.append(self.var2.get())
        self.destroy()
        outputs.append(self.variables)
        
class MainFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        
        #Clear the ROI counter
        self.roiIdx = 0
        
    def initUI(self):
        global init
        self.parent.title("Mavric Hip GUI")
        self.style = Style()
        self.style.theme_use("default")
        self.pack()
        
        #Initialize figure
        fig = matplotlib.figure.Figure()
        ax = fig.add_subplot(111)
        self.thisImg = np.eye(512, 512)
        self.figDrawing = ax.imshow(self.thisImg, cmap='gray')
        self.canvas=FigureCanvasTkAgg(fig,master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().configure(takefocus=True)
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=2, rowspan=1)
        
        #Reset the focus to the dicom images
        self.canvas.mpl_connect('button_press_event', lambda event:self.canvas._tkcanvas.focus_set())
        #Watch for mouse or key press events
        self.canvas.mpl_connect('button_press_event',self.selectRoi)
        self.canvas.mpl_connect('button_press_event', lambda event: PopUp())
        self.canvas.mpl_connect('key_press_event',self.writeRoi)
        #Load the buttons
        nextButton = Button(self, text="<", command=self.prev)
        nextButton.grid(row=0, column=0)
        
        openButton = Button(self, text="Open", command=self.pickFile)
        openButton.grid(row=2, column=1, sticky=E)
 
        quitButton = Button(self, text="Quit", command=self.quit)
        quitButton.grid(row=2, column=2, sticky=W)
        
        nextButton = Button(self, text=">", command=self.next)
        nextButton.grid(row=0, column=3)
        

    def pickFile(self):
        global roiCounter
        filename = askopenfilename()
        self.dicomName = filename
        #Get the folder and image names
        self.folder, self.name = os.path.split(self.dicomName)
        #Clear the counter for number or ROIs
        roiCounter = 0
        #Create a grid to "overlay" the image (32x32 voxels)
        self.gridLayout = [1]*256
        
        self.updateImage()
        
    def loadFile(self):
        global roiCounter
        self.updateImage()
        #Clear the counter for number or ROIs
        roiCounter = 0
        #Reset the grid "overlay" (32x32 voxels)
        self.gridLayout = [1]*256
        
    def next(self):
        #Get the folder and image names
        self.folder, self.name = os.path.split(self.dicomName)
        
        #Loads the next dicoms in the series
        count = 0
        for filename in os.listdir(self.folder):
            if(filename == self.name):
                if( (count+1) == len(os.listdir(self.folder))):
                    nextNum = 0
                else:
                    nextNum = count+1
                    
                newName = os.listdir(self.folder)[nextNum]
                
                self.dicomName = os.path.join(self.folder, newName)
                 
                self.loadFile()
            count += 1
            
    def prev(self):
        #Get the folder and image names
        self.folder, self.name = os.path.split(self.dicomName)
        
        #Loads the next dicoms in the series
        count = 0
        for filename in os.listdir(self.folder):
            if(filename == self.name):
                if( (count-1.0) < 0.0):
                    nextNum = len(os.listdir(self.folder)) - 1
                else:
                    nextNum = count-1
                      
                newName = os.listdir(self.folder)[nextNum]
                self.dicomName = os.path.join(self.folder, newName)
                self.loadFile()
            count += 1
        
    def updateImage(self):
        global init
        #Displays the dicom images
        ds = dicom.read_file(self.dicomName)
        self.dataArr = ds.pixel_array

        thisArr1Max = np.max(self.dataArr[::,::])
        if thisArr1Max == 0:
            thisArr1Max=1
        thisArr1 = self.dataArr[::,::].astype(np.float) / thisArr1Max
 
        self.figDrawing.set_data(thisArr1)
        self.canvas.draw()
        
        #Display the Image Number
        name = self.dicomName.split(".")
        number = name[0].split("-")
        self.num = number[-1].lstrip("0")
        test = Label(self, text=("Image Num: %s" % self.num), width=14)
        test.grid(row=1, column=1, sticky=E, pady=10)
        
        
        #Display the Series Number
        series = ds.SeriesNumber
        test = Label(self, text=("Series Num: %s" % series), width=15)
        test.grid(row=1, column=2, sticky=W, pady=10)
        
    def selectRoi(self, event):
        global roiCounter
        global prevRoi
        global localRow
        global localCol
        
        if roiCounter > prevRoi:
            for x in range(0, len(self.gridLayout)):
                if self.localGrid[x] == 0:
                    self.gridLayout[x] = 0
            prevRoi = roiCounter
        
        #Set the ROI coordinates
        print "Select Roi"
        newCol = event.xdata/512.0 * np.shape(self.dataArr)[1]
        newRow = event.ydata/512.0 * np.shape(self.dataArr)[0]
        
        localRow = int(np.round(newRow))
        localCol = int(np.round(newCol))
        
        gridCol = (localCol / 32) + 1
        gridRow = (localRow / 32) + 1
        
        val = (gridRow*8) - (8-gridCol) - 1

        #reset the local grid
        self.localGrid = [1]*256
        if(val-9.0 > 0.0): self.localGrid[val-9] = 0
        if(val-8.0 > 0.0): self.localGrid[val-8] = 0
        if(val-7.0 > 0.0): self.localGrid[val-7] = 0
        if(val-1.0 > 0.0): self.localGrid[val-1] = 0
        self.localGrid[val] = 0
        if(val+1 < 512): self.localGrid[val+1] = 0
        if(val+7 < 512): self.localGrid[val+7] = 0
        if(val+8 < 512): self.localGrid[val+8] = 0
        if(val+9 < 512): self.localGrid[val+9] = 0

    def writeRoi(self,event):
        global rowVal
        global colVal
        
        print "Write Roi"
        print 'key=%s'%(event.key)
        
        halfWidth = 16
        offsets = [-5, 0, 5]
        
        if event.key is 'w':
            for a in range(0, len(rowVal)):
                for rowOffset in offsets:
                    for colOffset in offsets:
                        startRow = rowVal[a] - halfWidth + rowOffset
                        endRow = rowVal[a]+halfWidth-1 + rowOffset
                        startCol = colVal[a] - halfWidth + colOffset
                        endCol = colVal[a] +halfWidth-1 + colOffset
             
                        if startRow < 0.0:
                            startRow = 0
                            print "Truncated start row"
                        if endRow >= np.shape(self.dataArr)[0]:
                            endRow = np.shape(self.dataArr)[0]-1
                            print "Truncated end row"
                 
                        if startCol < 0.0:
                            startCol = 0
                            print "Truncated start col"
                        if endCol >= np.shape(self.dataArr)[1]:
                            endCol = np.shape(self.dataArr)[1]-1
                            print "Truncated end col"
             
                        tmpRoi = self.dataArr[startRow:endRow:, startCol:endCol:]
                        
                        self.imageFolder = os.path.join(self.folder, "Image_" + self.num)
                        
                        if(os.path.exists(self.imageFolder)):
                            found = True
                        else:
                            os.makedirs(self.imageFolder)
                            
                        outName = self.name.split(".")    
                        self.roiName = 'roi_%i_anat_%s_.pic'%(self.roiIdx, outName[0])
                        fileName = os.path.join(self.imageFolder, self.roiName)
                        self.roiIdx += 1
              
                        np.save(fileName, tmpRoi)
             
                        print "Saved %s" % fileName
                         
                        self.writeOutput(True, a, fileName)
                    
    def writeOutput(self, roi, a, path):
        global outputs
        #Update the line for the association file    
        fullPath = os.path.join(path, self.roiName)
          
        if(roi):
            line = fullPath + ",  " + str(outputs[a][0]) + ",  " + str(outputs[a][1]) + "\n"
        else:
            line = fullPath + ",  " + "0" + ",  " + "0" + "\n"
        
        #Update the association file   
        newFile = os.path.join("diagnosisFile.txt")
        fileNew = open(newFile, "a+")
        fileNew.write(line)
        fileNew.close() 
    
def main():
  
    root = Tk()
    root.geometry("800x600+2+2")
    MainFrame(root)
    root.mainloop()  

if __name__ == '__main__':
    main() 