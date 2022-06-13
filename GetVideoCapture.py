# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 16:03:44 2022

@author: zhangh
"""

import cv2

import PIL.Image, PIL.ImageTk
import time
import threading

from  GetCamIndex import * #noqa

# camera func
class MyVideoCapture:
    def __init__(self,video_source=0, width=None, height=None, fps=None):
        # the necessary parameters
        
        if width == None:
            width = 640
        if height== None:
            height = 80
        if fps == None:
            fps = 30
            
        self.video_source = video_source
        self.width = width
        self.height = height
        self.fps = fps
        
        # open the camera
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
        self.vid.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))
        self.vid.set(cv2.CAP_PROP_FPS,fps)
        # since different camera has differet aspec so we should not set a gerenal width and height
        # then how to get the best resolution
#         self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#         self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        #print('exp:',self.vid.get(cv2.CAP_PROP_EXPOSURE) )
        
        # 4096, 2160,
        
        self.focus_value = 35
        self.vid.set(cv2.CAP_PROP_FOCUS,self.focus_value)
        
        if not self.vid.isOpened():
            raise ValueError('Undable to open camera:', video_source)
            
        
        
        self.ret = False
        self.frame = None
        # recording
        self.recording = False
        self.recording_filename = 'Output.mp4'
        self.recoridng_writer = None
        
        # cv2 zoom
        self.zoom_bool = False
        self.scale = 100
        
        # click zoom
        self.click_zoom_bool = False
        self.click_zoom_scale = 1
        self.center_x = int(self.width/2)
        self.center_y = int(self.height/2)
        
        self.panX_bool = False
        self.panX_num = 0
        # colors
        
        self.panY_bool = False
        self.panY_num = 0

        # threading
        #self.lock = threading.Lock()
         #https://www.pythontutorial.net/advanced-python/python-threading-lock/
            
        self.running = True
        
        
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    # cam funcs
    def process(self): 
        #self.lock.acquire() # lock start
        while self.running:
            # first set the zoom

            ret,frame = self.vid.read()
            
            if ret:
                # process the frames
                #frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
                
                # rocord before coverting channels
                if self.recording:
                    self.record(frame)

                if self.panX_bool:
                    self.panX(self.panX_num)
                
                if self.panY_bool:
                    frame = self.panY(frame, self.panY_num)
                    
                                                    
                if self.zoom_bool:
                    self.zoom(self.scale)   
                
#                 if self.click_zoom_bool:
#                     frame = self.click_zoom(frame,(self.center_x, self.center_y))
#                 # mouse callback
               
                
                # from opencv to tkiner frame formate
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = PIL.Image.fromarray(frame)
                
                # return frame
                self.ret = ret
                self.frame = frame # this is a PIL image object
                
            else:
                print('Stream end:', self.video_source)
                self.running = False
                if self.recording:
                    self.stop_recording()
                break

            
            # sleep for next frame
            time.sleep(1/self.fps)
            
    def get_frame(self):
        return self.ret, self.frame
        
    
    # release the video source when the window is closed
    def __exit__(self):
        if self.running:
            self.running = False
        if self.vid.isOpened():
            self.vid.release()
            #self.lock.release() # release lock
            self.thread.join() # should it be here or in get_frame()
    
    def release_cam(self):
        self.__exit__()
    # recording funcs
    def start_recording(self,filename=None):
        if self.recording:
            print('[MyVideoCapture] already recording:', self.recording_filename)
        
        else:
                self.recording_filename = filename + '_' + time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime())+ '.avi'
                    
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.recording_writer = cv2.VideoWriter(self.recording_filename, 
                                                    fourcc,self.fps, 
                                                    (self.width,self.height))
                self.recording = True
                

    def stop_recording(self):
        if not self.recording:
            print ('[MyVideoCapture] is not recording')
        else:
            self.recording = False
            self.recording_writer.release()     
            
    
    def record(self,frame):
        if self.recording_writer and self.recording_writer.isOpened():
            self.recording_writer.write(frame)
    
    # zoom
    def zoom(self,scale):
        self.scale = scale
        self.vid.set(cv2.CAP_PROP_ZOOM,scale)
        self.zoom_bool=True
            
  
    def click_zoom(self, img, center=None):
         
        height,width =self.height,self.width # height = rows, width = cols
        
        if center is None: # zoom center is the center of original image
            center_x, half_width = int(width/2), int(self.click_zoom_scale*width/2) # new half width
            center_y, half_height =  int(height/2),int(self.click_zoom_scale*height/2) # new half height
            
        else: # center of the new image is  not the orignal image
            center_x, center_y = center
            half_width = min(center_x, width - center_x) # could be right or left of the original center
            half_height = min(center_y, height - center_y)
            
            half_width = int(self.click_zoom_scale*half_width)
            half_height = int(self.click_zoom_scale*half_height)
            
            if half_width/half_height > self.width/self.height:
                half_width = int(half_height*self.width/self.height)
            elif half_width/half_height > self.width/self.height:
                half_height = int(half_width*self.height/self.width)
            
        min_x, max_x = center_x - half_width, center_x + half_width
        min_y, max_y = center_y - half_height, center_y + half_height
        
        cropped = img[min_y:max_y, min_x:max_x] # y is rows, x is cols
        
        new_img = cv2.resize(cropped, (self.width,self.height), interpolation=cv2.INTER_CUBIC)
        
        return new_img
    
#     # self.click_zoom_bool
#     def click_zoom_out(self, scale):
#         # right mouse button single click
#         if self.click_zoom_scale < 1:
#             self.click_zoom_bool = True
#             #self.click_zoom_scale += 0.1
#             self.click_zoom_scale = scale
#         if self.click_zoom_scale == 1:
#             self.center_x = self.width/2
#             self.center_y = self.height/2
#             self.click_zoom_bool = False

#     def click_zoom_in(self, cX, cY, scale):
#         # left button double click
#         if self.click_zoom_scale > 0.2:
#             self.click_zoom_bool = True
#             self.center_x = cX
#             self.center_y = cY
#             #self.click_zoom_scale -=0.1
#             self.click_zoom_scale = scale
#         else:
#             self.click_zoom_bool = False
    
    
    def panX(self,deltaX):
        self.panX_num = deltaX
        self.vid.set(cv2.CAP_PROP_PAN,deltaX)
        self.panX_bool = True
        #translated_frame = imutils.translate(img, deltaX, 0)
        #return translated_frame
        
#     def panY(self,img,deltaY):
#         self.panY_num = deltaY
#         self.panY_bool = True
#         translated_frame = imutils.translate(img, 0, deltaY)
#         return translated_frame
    
    def set_exposure(self, val):
         self.vid.set(cv2.CAP_PROP_EXPOSURE, val)
      
    def focusing(self, focus_value):
        if focus_value >=0 and focus_value<=255:
            self.vid.set(cv2.CAP_PROP_FOCUS,focus_value)
            
if __name__ == '__main__':

    # show one captured frame for each camera
    
    cams = CamIndex() #noqa

    total_cams  = cams.get_cam_indexes()
    print(total_cams)
    
    for index in total_cams:
        cap = MyVideoCapture(index)
        # wait the process to finish
        time.sleep(2) 
        ret, frame = cap.get_frame()
        if ret:
        # frame is a PIL image object
            frame.show()
            time.sleep(1)
        cap.release_cam()
    
