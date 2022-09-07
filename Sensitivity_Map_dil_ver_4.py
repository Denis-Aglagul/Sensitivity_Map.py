""" Author: Denis Aglagul
    takes images of any type( .png,.jpg.tif,etc..) and generates a sensitivity map.
    if a threshold is not provided, a threshold is computed and displayed using the first few images
    in the folder"""
import time
from tkinter import ttk


import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage
import pandas as pd
# import matplotlib.patches 
import math
# import random


#from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)


import threading
from tkinter import filedialog
from datetime import date

from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.morphology import local_maxima
from skimage import data, img_as_float
from skimage.measure import label
from skimage import data
from skimage import color
from skimage.morphology import extrema

import tkinter as tk
import os
import fnmatch
import cv2
import datetime
from os import path

def rgb2gray(rgb,sizes):
    if len(sizes) == 3:
        return color.rgb2gray(rgb)
    elif len(sizes) == 2:
        return rgb
    
    
    #return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

class App(tk.Tk):

    def __init__(self):
        
        super().__init__()
        
        self.colormaps = ('jet','magma','plasma','inferno','viridis','gnuplot')
        self.option_var = tk.StringVar(self)
        self.option_var.set(self.colormaps[0])
        self.v = tk.IntVar(self)
        self.v.set(2)
        self.readme = tk.StringVar(self)
        self.readme.set('takes images of any type ( .png,.jpg.tif,etc..)and generates a sensitivity map. \n\
The first entry is filepath to the directory containing images of hits\n\
on your detecotor. The images can be named anything and do not need to be\n\
numbered, you just have to make sure there are not other images in the\n\
same directory. The next entry is thetheshold for hit identification.\n\
If a threshold is not provided, a threshold is computed using the first\n\
few images in the folder. The final entry is the minimum hit size(in pixels)\n\
adjust this to supplement the hit identification,put to \'1\' if youre unsure,\n\
dont leave it blank. You can save the sensitivty map anytime from the top left\n\
\'save sens map\' option even while the images are still beign processed.\n\
 if you want to halt the processing, just close and relaunch the app')
         
        # Dictionary to create multiple buttons

        # Create a style
        style = ttk.Style(self)

        # Set the theme with the theme_use method
        style.theme_use('classic')  # put the theme name here, that you want to use

        # configure the root window
        self.title('Sensitivity Map')
        self.geometry('900x530')
        self.button_explore = ttk.Button(self, text = "Browse Files")
        self.button_explore['command'] = self.browseFiles
        self.button_explore.place(x=10,y = 25)
        self.statusvar = tk.StringVar(self)
        self.statusvar.set("Ready")
        self.sbar =ttk.Label(self, textvariable=self.statusvar, relief=tk.SUNKEN, anchor="w")
        self.sbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        #progress bar
        self.pb = ttk.Progressbar(
            self,
            orient = tk.HORIZONTAL,
            length = 100,
            mode = 'determinate'
            )
        self.pb.place(x=10, y=430,width=420,height = 25)

        self.runcode()
        
        self.bind('<Control-s>',self.save_map)
        self.bind('<Escape>',self.destroy_w)
        self.ni_enter()
        self.G_enter()
        self.BB_enter()
        self.fp_enter()
        self.comments()
        
        self.menu_bar()
        
        
    def showup(self):
        
        im.set_cmap(self.option_var.get())
        canvas.draw()

    #menu bar for saving results
   
        
    def menu_bar(self):

        self.my_menu =tk.Menu(self,background='#ff8000', foreground='black', activebackground='white', activeforeground='black')
        self.config(menu = self.my_menu)
        self.file_menu=tk.Menu(self.my_menu,tearoff = False)
        self.my_menu.add_cascade(label = 'Save Sens Map',command = self.save_map_2)
        
        self.menu1 = tk.Menu(self,tearoff = False)
        self.submenu = tk.Menu(self,tearoff = False)
        self.submenu.add_radiobutton(label = "morphological peaks(Single pixel)", variable =self.v,value = 1,
                                     command = self.comments)#.place(x = 260,y = 130)

        self.submenu.add_radiobutton(label = "thesholded peaks(Bounding box)",variable = self.v,value = 2,
                                     command = self.comments)#.place(x = 260,y = 160)
        self.submenu.add_radiobutton(label="thesholded peaks(Single Pixel)", variable=self.v, value=3,
                                     command=self.comments)  # .place(x = 260,y = 160)

        self.my_menu.add_cascade(label="Method", menu=self.submenu)

        self.subcmapmenu = tk.Menu(self,tearoff = False)
        
        for i in range(len(self.colormaps)):            
            self.subcmapmenu.add_radiobutton(label = self.colormaps[i],variable = self.option_var ,value = self.colormaps[i],
                                             command = self.showup)
        self.my_menu.add_cascade(label="Cmap", menu=self.subcmapmenu)
        
        
    def runcode(self):
        self.button = ttk.Button(self, text='Calculate sensitivity map')
        self.button['command'] = self.threadin
        self.button.place(x = 240, y = 150)

    def comments(self):
        
        if self.v.get() == 2 or self.v.get() == 3:
            self.readme.set('takes images of any type ( .png,.jpg.tif,etc..)and generates a sensitivity map. \n\
The first entry is filepath to the directory containing images of hits\n\
on your detecotor. The images can be named anything and do not need to be\n\
numbered, you just have to make sure there are not other images in the\n\
same directory. The next entry is the threshold for hit identification.\n\
If a threshold is not provided, a threshold is computed using the first\n\
few images in the folder. The final entry is the minimum hit size(in pixels)\n\
adjust this to supplement the hit identification,put to \'1\' if youre unsure,\n\
dont leave it blank. You can save the sensitivty map anytime from the top left\n\
\'save sens map\' option even while the images are still beign processed.\n\
 if you want to halt the processing, just close and relaunch the app')
            self.BBThresh['state'] = 'normal'
            self.GrayThresh['state'] = 'normal'
            self.update()
            self.Glabel = ttk.Label(self, text='Threshold')
            self.Glabel.place(x=90, y=175)
        elif self.v.get() == 1:
            self.readme.set('takes images of any type ( .png,.jpg.tif,etc..)and generates a sensitivity map. \n\
The first entry is filepath to the directory containing images of hits\n\
on your detecotor. The images can be named anything and do not need to be\n\
numbered, you just have to make sure there are not other images in the\n\
same directory. There is no threshold for this method. This method \n\
populates with single pixels and is generally slower but can handle\n\
more hits per image. You can save the sensitivty map anytime from the top left\n\
\'save sens map\' option even while the images are still beign processed.\n\
 if you want to halt the processing, just close and relaunch the app.')
            self.update()
            self.BBThresh['state'] = 'disabled'
            self.GrayThresh['state'] = 'normal'
            self.Glabel = ttk.Label(self, text='Relative height')
            self.Glabel.place(x=90, y=175)
     
        self.comment = ttk.Label(self,text = self.readme.get() ).place(x = 10,width = 430,y = 245,height = 180)
        
       
    
            
        
        

            
                    
    def ni_enter(self):         
       self.ni =  ttk.Entry(self)
       #self.ni.insert(0,"200")
       self.ni.place(x = 15,y = 130,width = 70,height = 30)
       
       self.nilabel = ttk.Label(self,text = 'Number of images')
       self.nilabel.place(x= 90,y = 135)
       


    def BB_enter(self): 
        
        
        self.BBThresh =  ttk.Entry(self)
        self.BBThresh.insert(0,"4")
        self.BBThresh.place(x = 15,y = 210,width  = 70,height =30 )

        self.BBLabel = ttk.Label(self,text = 'Min hit size')
        
        self.BBLabel.place(x = 90,y = 215)
               
    def G_enter(self):    
        self.GrayThresh =  ttk.Entry(self)
       
        self.GrayThresh.place(x = 15,y = 170,width  = 70,height = 30)
        
        self.Glabel =  ttk.Label(self,text = 'Threshold')
        self.Glabel.place(x = 90,y = 175)


    def save_map(self,event):
       todays_date = date.today()
       date_path = "D:\data" + str(todays_date.year) + "/"
        
       text_file = filedialog.asksaveasfilename(defaultextension = ".txt",initialdir=date_path,
                                                 title = 'Save File',filetypes = (("Text Files","*.txt"),("All Files","*.*")) )
       # name = text_file
       # name.replace(date_path,"")
       np.savetxt(text_file, self.image)
    def save_map_2(self):
       todays_date = date.today()
       date_path = "D:\data" + str(todays_date.year) + "/"
        
       text_file = filedialog.asksaveasfilename(defaultextension = ".txt",initialdir=date_path,
                                                 title = 'Save File',filetypes = (("Text Files","*.txt"),("All Files","*.*")) )
       np.savetxt(text_file,self.image)
        
    def browseFiles(self):
        self.fp.delete(0,tk.END)
        filename = filedialog.askdirectory()
        self.fp.insert(tk.END, filename + '/')
        
        return filename 

    def threadin(self):
        
        
        # Call work function
        t1=threading.Thread(target =  self.Sensitivity_Map)
        t1.setDaemon(True)
        t1.start()
        
    def fp_enter(self):
    
        self.fp  =  ttk.Entry(self)
        self.fp.insert(0,"E:\DATA\dark_counts_test_1\\")
        self.fp.place(x = 10,y = 70,width  = 400)            

    
        
   
    def destroy_w(self,event):
        self.destroy()
        
    @staticmethod
    def relative_peak(z, Grey, Picks, h):
        
         h_maxima = extrema.h_maxima(z, h)
         label_h_maxima = label(h_maxima)
         z[label_h_maxima==0] = 0
         label_h_maxima[label_h_maxima!=0] = 1
         
         Grey+= z     
         Picks+=label_h_maxima.astype( Picks.dtype )
         
         return [ Grey, Picks]

    @staticmethod
    def abs_peak(z, GT, BT, Picks, Grey, counting):

        
       z_thresh = np.copy(z)
       z_thresh[z_thresh<GT] = 0

       #now find the objects
       labeled_image, number_of_objects = scipy.ndimage.label(z_thresh)                   
       peak_slices = scipy.ndimage.find_objects(labeled_image)

       for peak_slice in peak_slices:

           BP = 0
           dy,dx = peak_slice
           bounding_box = z[dy.start:dy.stop,dx.start:dx.stop]

           if ((dx.stop - dx.start)*(dy.stop-dy.start) > BT and (dx.stop - dx.start)*(dy.stop-dy.start)< 100):  
                counting+=1
                BP = np.max(bounding_box)
                Grey[dy.start:dy.stop,dx.start:dx.stop] += BP
                Picks[dy.start:dy.stop,dx.start:dx.stop] += 1
           else:
               pass
       return [Grey, Picks,counting]


    @staticmethod
    def abs_peak_single(z, GT, BT, Picks, Grey, counting):

       z_thresh = np.copy(z)
       z_thresh[z_thresh<GT] = 0

       #now find the objects
       labeled_image, number_of_objects = scipy.ndimage.label(z_thresh)
       peak_slices = scipy.ndimage.find_objects(labeled_image)

       for peak_slice in peak_slices:

           BP = 0
           dy,dx = peak_slice
           bounding_box = z[dy.start:dy.stop,dx.start:dx.stop]

           if ((dx.stop - dx.start)*(dy.stop-dy.start) > BT and (dx.stop - dx.start)*(dy.stop-dy.start)< 100):
                counting+=1
                BP = np.max(bounding_box)
                bounding_box[BP!=bounding_box] = 0
                z_thresh[dy.start:dy.stop, dx.start:dx.stop] = bounding_box



           else:
               z_thresh[dy.start:dy.stop,dx.start:dx.stop] = 0

       Grey += z_thresh
       z_thresh[z_thresh!=0] = 1
       Picks += z_thresh
       return [Grey, Picks,counting]
                   
          
    def Sensitivity_Map(self):
        tic = time.perf_counter()
        self.button['state'] = 'disabled'
        self.statusvar.set('initializing...')        
        
        filepat = self.fp.get()
        #initializing arrays        
        j = 0
        threshM = 0
        threshSTD = 0
        if os.path.isdir(filepat) is False:
            self.statusvar.set('directory not found.')
            self.button['state'] = 'normal'
            return None
        for filename in os.listdir(filepat):
            img = (cv2.imread(os.path.join(filepat,filename), -1))
           
            if img is not None :
                if j < 10:
                    print(img.dtype)
                    DATA_TYPE = img.dtype
               
                    initialize = rgb2gray((img),img.shape)
                    threshM+=np.nanmean(initialize)
                    threshSTD += np.nanstd(initialize)**2
                    print(threshSTD,threshM)
                
                
                    Total_Grey_value = np.zeros_like(initialize)
                    Times_raw_imgked =  np.zeros_like(initialize)
                    j+=1


                        

                else:
                    threshM = threshM/j
                    threshSTD = math.sqrt(threshSTD/j)
                    
                    break
            else:
                pass
                  
        #if number of images are not provided, scan directroy for files and count images     
        if len(self.ni.get()) == 0:
            dir_path = self.fp.get()
            count = len(fnmatch.filter(os.listdir(dir_path), '*.*'))
            numberofimages = count
            self.ni.insert(0,str(numberofimages))         
        else:          
            numberofimages = int(self.ni.get())
        #if threshold is not provided, calculate a threshold using the mean background of an image.
        if len(self.GrayThresh.get()) == 0:
            if self.v.get() == 2 or self.v.get() == 3:
                GT =threshM  + 3 * threshSTD
                self.GrayThresh.insert(0,str(GT))
            elif self.v.get() == 1:
                GT =  .66 * threshSTD/threshM
                h = GT
                self.GrayThresh.insert(0, str(GT))

        else:
            GT = (float(self.GrayThresh.get()))
            h = GT

        BT = int(self.BBThresh.get())
        h = GT
        
        self.pb['value'] = 0
        index = 0
        self.statusvar.set('running...')
        counting = 0
        for filename in os.listdir(filepat):

            img = (cv2.imread(os.path.join(filepat,filename),-1))
            if img is not None:
              z = rgb2gray(img,img.shape)
            if img is None:
                if index > numberofimages - 20:
                    self.statusvar.set('done.')
                    self.button['state'] = 'normal'
                    
                    return None
                
                pass

            im.set_cmap(self.option_var.get())
            canvas.draw()
            self.update()
            #print(frame/int(self.ni.get()),frame,self.ni.get())
            self.update_idletasks()
            self.pb['value'] = ((index+1)/numberofimages)*100
            
            
            
            if self.v.get() == 2:
                
                arrays = self.abs_peak(z = z,GT = GT, BT = BT, Picks = Times_raw_imgked, Grey = Total_Grey_value,
                                       counting = counting)
            elif self.v.get() == 1:
                
                arrays = self.relative_peak(z = z, Picks = Times_raw_imgked, Grey = Total_Grey_value,h=h)

            elif self.v.get() ==3:
                arrays = self.abs_peak_single(z=z, GT=GT, BT=BT, Picks=Times_raw_imgked, Grey=Total_Grey_value,
                                       counting=counting)
            else:
                print('something went wrong')
                self.quit()
            toc = time.perf_counter()
                

            #counting =+ arrays[2]
            Total_Grey_value = arrays[0]
            Times_raw_imgked = arrays[1]  
            #print(counting)
            
        
            index+=1
            if index%100 == 0 or index >= numberofimages:
                sens = Total_Grey_value/Times_raw_imgked
                df = pd.DataFrame({'Sens':sens.flatten()})
                Smax = df[['Sens']].quantile(.97)[0]
                a.set_xticks([])
                a.set_yticks([])
                a.axis('off')
                self.image = sens/Smax
                im.set_data(self.image)
                im.set_clim(vmin=0,vmax=1)
                canvas.draw()
                print(toc - tic)

            else:
                pass
            
            
            if index >= numberofimages:
                self.statusvar.set('done.')
                self.button['state'] = 'normal'
                return None
                
        self.statusvar.set('done.')    
        self.button['state'] = 'normal'
        return None
        
if __name__ == "__main__":
    
    app = App()

    #make figure to show results   
    f = plt.Figure(figsize=(2,2),dpi=200)
    a = f.add_subplot(111)        
    a.set_xticks([])
    a.set_yticks([])  
    A = np.zeros((300,300))   
    for x in range(300):
        for y in range(300):
            A[x][y] =math.sin(x*y/300**2)
    im = a.imshow(A,interpolation = 'nearest',cmap = 'jet',clim = (0,1))
    cbar = plt.colorbar(im,ax = a,shrink = .8,ticks = (0,.25,.5,.75,1))
    plt.tight_layout()                
    canvas = FigureCanvasTkAgg(f,
                               master = app)       
    canvas.get_tk_widget().place(x =450,y= 40,width = 445,height = 430)
    #add tkinter tool bar
    toolbar = NavigationToolbar2Tk(canvas,
                                  app)

    
    
    canvas.draw()
    toolbar.update()
    app.resizable(False, False)

    app.mainloop()