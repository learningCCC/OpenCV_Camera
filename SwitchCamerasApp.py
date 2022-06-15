# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 11:14:09 2022

@author: hgzha
"""

import tkinter as tk
from tkinter import *
from CameraApp_tkinter_main import *
from GetCamIndex import *


class GetCamIndex:
    indexes = None
    def __init__(self):
        GetCamIndex.indexes = self.getIndex()
        
    def getIndex(self):
        index_cls = CamIndex()
        indexes = index_cls.get_cam_indexes()
        return indexes
    
class CameraSwitchApp(tk.Tk, GetCamIndex):
    def __init__(self):
        tk.Tk.__init__(self)
 
        self._mainCam= None
        # The dictionary to hold the class type
        self._allCams = dict()
        # Switch cameras
        self.switch_Cam(CamOne)
        # closing windows release cameras

        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.mainloop()
        

    
    def switch_Cam(self, Cam_class):
        # hide the current Frame if exists
        if self._mainCam:
            self._mainCam.grid_forget()

        # has Class been called before?
        Cam = self._allCams.get(Cam_class, False)
        # if Cam_class is a new class type, Cam is False
        if not Cam:
            # Instantiate the new class
            Cam = Cam_class(self)
            # Store it's type in the dictionary
            self._allCams[Cam_class] = Cam

        # Pack the Cam or self._mainCam (these are all frames)
        Cam.grid(row=0, column=0,sticky=N+S+W+E)
        Cam.bind('<Configure>', Cam.frame.resize_image)
             
        self.rowconfigure(0, weight=1) #noqa
        self.columnconfigure(0, weight=1) #noqa 
        # and make it the 'default' or current one.
        self._mainCam = Cam
        
    def on_closing(self, event=None):
        if self._allCams!= None:
            for i, cam in self._allCams.items():
                cam.frame.vid.running = False
                cam.frame.release_cam()
        self.destroy()
        
class CamOne(tk.Frame, GetCamIndex):
    def __init__(self, master,  *args, **kwargs):
        tk.Frame.__init__(self,master, *args, **kwargs)
        
        #(4096, 2160,30), (1920, 1080,60) for logitech
        width = 4096
        height = 2160
        indexes = GetCamIndex.indexes
        if len(indexes) == 0: return
        
        self.frame = None
        try:
            self.frame = TkCamera(self, 'First Camera',indexes[0], width,  height, 15)
        except:
            print('unable to open campera one')
       
        
        if self.frame:
            self.frame.grid(row=0, column=0, sticky=N+S+W+E) #noqa
            #self.frame.bind('<Configure>', self.frame.resize_image)
            if len(indexes) == 2:  
                self.button = tk.Button(self, text="To cam two",
                      command=lambda: master.switch_Cam(CamTwo))
                self.button.grid(row=1,column=0)
                
            self.rowconfigure(0, weight=1) #noqa
            self.columnconfigure(0, weight=1) #noqa

class CamTwo(tk.Frame, GetCamIndex): # Sub-lcassing tk.Frame
    def __init__(self, master, *args, **kwargs):
        # self is now an istance of tk.Frame
        tk.Frame.__init__(self,master, *args, **kwargs)
        
        # make a new Cam whose parent is self.
        width = 4096
        height = 2160
        
        indexes = GetCamIndex.indexes
        self.frame = None
        try:
            self.frame = TkCamera(self, 'First Camera',indexes[1], width,  height, 15)
        except:
            print('unable to open campera two')
        if self.frame: 
            self.frame.grid(row=0, column=0, sticky=N+S+W+E) #noqa
            self.rowconfigure(0, weight=1) #noqa
            self.columnconfigure(0, weight=1) #noqa
            
            self.button = tk.Button(self, text="To cam one",
                  command=lambda: master.switch_Cam(CamOne))
            self.button.grid(row=1,column=0)
        
if __name__ == "__main__":
    
    getindexes = GetCamIndex()
    indexes = getindexes.getIndex()

    if indexes!=None:
        app = CameraSwitchApp()
    
