# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 16:03:44 2022

@author: zhangh

https://stackoverflow.com/questions/71381525/python-zooming-and-capturing-a-specific-part-of-a-webcam-live-video-using-opencv
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
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0) # on is 3, off is 1?
        
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
        self.cropped = []
        
        self.panX_bool = False
        self.panX_num = 0
        # colors
        
        self.tiltY_bool = False
        self.tiltY_num = 0

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
                frame_copy = frame.copy()
                
                # rocord before coverting channels
                if self.recording:
                    self.record(frame)

                if self.panX_bool:
                    self.panX(self.panX_num)
                    
                if self.tiltY_bool:
                    self.tiltY(self.tiltY_num)

                                                    
                if self.zoom_bool:
                    self.zoom(self.scale)   
                
                if self.click_zoom_bool:
                    frame = self.click_zoom(frame,(self.center_x, self.center_y))
                    
                    #TODO: panX and panY after click zoom
                    # pass frame_copy, self.center_x, self.center_y, frame_width, frame_height to the pan functions
                    # if self.panY_bool:
                    #     frame_height,frame_width = self.cropped.shape[0:2]
                    #     frame = self._panY(0, self.panY_num, frame_copy,  int(frame_width), int(frame_height), self.center_x, self.center_y)
                
                # # mouse callback
               
                
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
         
        height,width = img.shape[:2] # height = rows, width = cols
        
        if center is None: # zoom center is the center of original image
            center_x = int(width/2) # new half width
            center_y =  int(height/2) # new half height
            radius_x, radius_y = int(width/2), int(height/2)
            
        else: # center of the new image is  not the orignal image
        
            
            center_x, center_y = center
            
            # clamp the min and max of center_x center_y
            rate = height/width
            if center_x < width*(1-rate):
                center_x = width*(1-rate)
            elif center_x > width * rate:
                center_x = width * rate
            
            #rate = width/height
            if center_y < height*(1-rate):
                center_y = height*(1-rate)
            elif center_y > height*rate:
                center_y = height*rate
        
            center_x, center_y = int(center_x), int(center_y)
            # change the self.center_x, self.center_y to new center_x, center_y
            self.center_x, self.center_y = center_x, center_y
            
            # clamp x, y boundary
            left_x, right_x = center_x, int(width - center_x)
            up_y, down_y = int(height - center_y), center_y
            radius_x = min(left_x, right_x)
            radius_y = min(up_y, down_y)
        
        # new radius after zoom
        radius_x, radius_y = int(self.click_zoom_scale* radius_x), int(self.click_zoom_scale* radius_y)
            
            
        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y
        
        self.cropped = img[min_y:max_y, min_x:max_x] # y is rows, x is cols
        
        
        new_img = cv2.resize(self.cropped, (self.width,self.height), interpolation=cv2.INTER_LINEAR)
        
        return new_img
    
    # self.click_zoom_bool
    def click_zoom_out(self, scale):
        # right mouse button single click
        if self.click_zoom_scale < 1:
            self.click_zoom_bool = True
            #self.click_zoom_scale += 0.1
            self.click_zoom_scale = scale
        if self.click_zoom_scale == 1:
            self.center_x = self.width/2
            self.center_y = self.height/2
            self.click_zoom_bool = False

    def click_zoom_in(self, cX, cY, scale):
        # left button double click
        if self.click_zoom_scale > 0.2:
            self.click_zoom_bool = True
            self.center_x = cX
            self.center_y = cY
            #self.click_zoom_scale -=0.1
            self.click_zoom_scale = scale
        else:
            self.click_zoom_bool = False
    
    
    def panX(self,deltaX):
        self.panX_num = deltaX
        self.vid.set(cv2.CAP_PROP_PAN,deltaX)
        self.panX_bool = True
        #translated_frame = imutils.translate(img, deltaX, 0)
        #return translated_frame
        
    def tiltY(self,deltaY):
        self.tiltY_num = deltaY
        self.vid.set(cv2.CAP_PROP_TILT,deltaY)
        self.tiltY_bool = True
    
    #frame = self._panY(self.panY_num, frame_copy,  frame_width, frame_height, self.center_x, self.center_y)
    def _panY(self,delta_x,delta_y,img, w, h, center_x, center_y):
        
        # new frame boundary
        print(center_x, center_y, delta_x,delta_y, w,h)
 
        print(img.shape[0:2])
        left_x, right_x = int(center_x + delta_x- 2/w), int(center_x + delta_x + 2/w)
        up_y, down_y = int(center_y + delta_y + 2/h), int(center_y + delta_y - 2/h)
        
        new_frame = img[down_y:up_y, left_x:right_x]
        
        
        return new_frame
        
    def set_exposure(self, val):
         self.vid.set(cv2.CAP_PROP_EXPOSURE, val)
         self.vid.set(cv2.CAP_PROP_GAIN, val*10) # increase the gain as increase exposure
         #self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, val)
         #print(val, self.vid.get(cv2.CAP_PROP_AUTO_EXPOSURE))
     
        # autoexpsure does not work
    # def set_autoExposureON(self):
    #     print("Auto Exposure On")
    #     self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    
    # def set_autoExposureOff(self):
    #     print("Auto Exposure Off")
    #     self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, -1)
        
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
    
