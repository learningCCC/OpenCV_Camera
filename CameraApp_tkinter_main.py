# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 16:06:02 2022

@author: zhangh
"""
import warnings
warnings.filterwarnings("ignore")

import tkinter
from tkinter import * #noqa
import PIL.Image, PIL.ImageTk
import time

# helper function
from  GetVideoCapture import * #noqa
from  GetCamIndex import * #noqa


class TkCamera(tkinter.Frame):
    def __init__(self, window, text="", video_source=0,width=None, height=None,fps=None):
        super().__init__(window) # self tkinter frame
        
        # declare main params
        self.window =  window
        
        self.video_source = video_source
        self.text = text
        # get ret and frame from capture class
        self.vid = MyVideoCapture(self.video_source, width, height, fps) #noqa
                
        # build the tkinter window
        self.label = tkinter.Label(self,text=text)
        self.label.pack()
        
        self.win_width = window.winfo_width()
        self.win_height = window.winfo_height()
        self.window.update_idletasks()
        #print (window.winfo_width(),window.winfo_height())
        
        # small size 
        self.canvas = tkinter.Canvas(self, width=self.win_width, height=self.win_height)
        self.canvas = tkinter.Canvas(self) #width=640, height=480
        self.canvas.pack(fill='both', expand=True)
        # make it resizable with the big window
        self.canvas.bind('<Configure>', self.resize_image)
        
        # mouse wheel focus on cavas
        self.canvas.bind('<MouseWheel>', self._mouse_focus)
        self.count = self.vid.focus_value #35
        
#         # mouse click for zoom
#         self.canvas.bind('<Double-Button-1>', self._click_zoom_in)
#         self.canvas.bind('<Button-3>', self._click_zoom_out)
#         self.click_zoom_scale = 1
   
   
        # buttons
        self.btn_start = tkinter.Button(self, text='Start', command=self.start_button)
        self.btn_start.pack( side='left') #anchor='center
        
        self.btn_stop = tkinter.Button(self, text='Stop', command=self.stop_button)
        self.btn_stop.pack( side='left') #anchor='center
        
        self.btn_snapshot = tkinter.Button(self, text='Snapshot', command=self.snapshot_button)
        self.btn_snapshot.pack(side='left') #anchor='center
        
        #self.zoom_label = Label(self, text='zoom')
        
        self.slider_zoom = tkinter.Scale(self,from_=100, to=500,
                                         orient=HORIZONTAL,command=self.zoom_slider) #label='Zoom', #noqa
        self.slider_zoom.pack(side='right',anchor='center')
        self.slider_zoom.set(100)
        self.label_zoom = tkinter.Label(self,text='Zoom')
        self.label_zoom.pack(side='right',)
        
        self.slider_pan = tkinter.Scale(self, from_=-15, to=15,
                                         orient=HORIZONTAL,command=self.pan_h_slider) #label='Pan',#noqa
        self.slider_pan.pack(side='right',anchor='center')
        self.slider_pan.set(0)
        self.label_pan = tkinter.Label(self,text='Pan')
        self.label_pan.pack(side='right')
        
        self.slider_exposure = tkinter.Scale(self, from_=-10, to=10,
                                         orient=HORIZONTAL,command=self.exposure_slider) #label='Pan',#noqa
        self.slider_exposure.pack(side='right',anchor='center')
        self.slider_exposure.set(0)
        self.label_exposure = tkinter.Label(self,text='Exposure')
        self.label_exposure.pack(side='right')

        
  
        self.delay = int(1000/self.vid.fps)
        self.image = None
        self.image_on_canvas=None
        self.running = True

        # hold the after method id
        self.handler = None
        
        self.update_frame() 
        

        
    # update frames
    def update_frame(self):
        # close pending after callback process, otherwise spider will invoke "invalide command error
        # https://stackoverflow.com/questions/9776718/how-do-i-stop-tkinter-after-function
        if self.handler:
            self.window.after_cancel(self.handler)
            
            
        ret, frame = self.vid.get_frame()

        if ret:
            self.image = frame

            self.image = self.image.resize((self.win_width, self.win_height))
                               
            self.image_on_canvas= PIL.ImageTk.PhotoImage(image=self.image)
            
            self.canvas.create_image(0, 0, image=self.image_on_canvas, anchor='nw')
        
        if self.running:
            self.handler = self.window.after(self.delay, self.update_frame)
        else:
            self.vid.running = False
            if self.handler:
                self.window.after_cancel(self.handler)
    
    def release_cam(self):
        self.vid.vid.release()
        if self.handler:
            self.window.after_cancel(self.handler)
    
    def resize_image(self, event):
        self.win_width = event.width
        self.win_height = event.height
        
#         ret, frame = self.vid.get_frame()
#         if ret:
#             self.image = frame
#             self.image_resize = self.image.resize((event.width, event.height),resample=PIL.Image.Resampling.LANCZOS )

#             self.configure_image = PIL.ImageTk.PhotoImage(self.image_resize)
#             self.canvas.itemconfig(self.image_on_canvas, image= self.configure_image)
    
    # some buttons
    def start_button(self):
        filename = self.text
        self.vid.start_recording(filename)
        
    def stop_button(self):
        self.vid.stop_recording()
        
    def snapshot_button(self):
        if self.image:
            self.image.save(time.strftime('%Y_%m_%d_%H_%M_%S.jpg'))
    
    # zoom buttons
    
    def zoom_slider(self, event):
        zoom_scale = int(self.slider_zoom.get())
        #print(zoom_scale)
        self.vid.zoom(zoom_scale)

    # pan buttons
    def pan_h_slider(self, event):
        panX = int(self.slider_pan.get())
        self.vid.panX(panX)
    
    def exposure_slider(self,event):
        exposure_val = self.slider_exposure.get()
        self.vid.set_exposure(exposure_val)
    
    def _mouse_focus(self, event): 
        # wheel forward = focus +
        
        if event.num == 5 or event.delta == -120:
            self.count -= 5
            self.vid.focusing(self.count)
            
        if event.num == 4 or event.delta == 120:
            self.count += 5
            self.vid.focusing(self.count)
            
#     def _click_zoom_in(self, event):
        
#         if self.click_zoom_scale >=0.2:
#               self.click_zoom_scale -=0.1 
        
#               cX, cY=  event.x, event.y
#               self.vid.click_zoom_in(cX, cY, self.click_zoom_scale)
        
#     def _click_zoom_out(self, event):
        
#         if self.click_zoom_scale <= 1:
#             self.click_zoom_scale +=0.1
#             self.vid.click_zoom_out(self.click_zoom_scale)
                 
            
 ##################################################################################################################           
            
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
            self.vid = TkCamera(self.window, text, camID, self.x_pixel, self.y_pixel, self.fps) 
            
            row = num // columns
            column = num % columns
            # make the video change size with the main window
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
        
#     sources=[
#         ('Me', 0),
#         ('Jupiter', 2)
#             ]
    
#     CameraApp(tkinter.Tk(), 'Jupiter Side Cameras', sources)
