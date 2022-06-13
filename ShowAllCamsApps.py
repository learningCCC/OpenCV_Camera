# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 10:53:08 2022

@author: hgzha
"""


import warnings
warnings.filterwarnings("ignore")

import tkinter
from tkinter import * #noqa

# helper function
from  GetCamIndex import CamIndex       
from  CameraApp_tkinter_main import TkCamera       

    
class CameraApp:
    def __init__(self, window, window_title, video_sources):
        
        self.window = window

        self.window.title(window_title)
        
        self.window.resizable(True,True) # TODO, make it user resizable
        self.window.aspect(1,1,1,1) # this is not working!!! very annoying
        
        #self.window.minsize(1920,600)
        self.x_pixel = 1920
        self.y_pixel = 1080
        self.fps  = 30

        #self.window.bind('<Configure>',self._resize_window)
        #self.window.update_idletasks()
        geometry = (f'{self.x_pixel}x{int(self.y_pixel/2)}')
        self.window.geometry(geometry)
        
        self.vids = []
        columns = 2
        
        
        
        
        for num, src in enumerate(video_sources):
            text, camID = src
            # this should be general # (4096, 2160,30), (1920, 1080,60) for logitech
            # for built in camera like hp wide vision hd camera  it is 1280 x 720
            self.vid = TkCamera(self.window, text, camID, self.y_pixel, self.x_pixel, self.fps) 
            
            row = num // columns
            column = num % columns
            
            self.vid.grid(row=row, column=column, sticky=N+S+W+E) #noqa
            Grid.rowconfigure(self.window, row, weight=1) #noqa
            Grid.columnconfigure(self.window, column, weight=1) #noqa
            
            self.vids.append(self.vid)
     
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.window.mainloop()

        
    # def _resize_window(self, event):

    #     self.event_width = event.width 
    #     self.win_width = event.width
    #     self.win_height = int(self.event_width*6/9)

        
        
    def on_closing(self, event=None):
            for src in self.vids:
                src.vid.running = False
                src.release_cam()
            self.window.destroy()
                
            

if __name__ == '__main__':
    
 
    
    cams = CamIndex() #noqa
    # print(cams.get_cams_info())
    sources = cams.get_cams_info()
    if sources!= None:    
        CameraApp(tkinter.Tk(), 'Jupiter Side Cameras', sources)