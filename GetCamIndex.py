# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:20:01 2022

@author: zhangh
"""


import cv2
from device_manager import USBDeviceScanner

# ! pip install device-manager
# ! pip install python-nmap

class CamIndex:
    
    #builtIn_cam_indexes = []
    def __init__(self):
        self.cams = []
        self.builtIn_cam_indexes = []
        self.usb_cam_indexes = []
        self.usb_cam_names = []
        
        self.get_cam_indexes()
        self.get_cam_names()
        
    def get_cams_info(self): 
        
        
        for index in range(len(self.builtIn_cam_indexes)):
            self.cams.append(('builtIn_cam', index))
        
        for index, name in zip(self.usb_cam_indexes, self.usb_cam_names):
            self.cams.append((name, index))
            
        return self.cams
    
    
    def get_cam_indexes(self):
        # initialize empty list
        self.builtIn_cam_indexes = []
        self.usb_cam_indexes = []
        cam_indexes =[]
        
        for i in range(4):
            cap= cv2.VideoCapture(i, cv2.CAP_DSHOW) #CAP_DSHOW
            ret,frame = cap.read()
            if ret:
                zoom = cap.get(cv2.CAP_PROP_ZOOM) 
                #print (zoom)
                if  (i == 0) & (zoom <=0): 
                    self.builtIn_cam_indexes.append(i)
                    cam_indexes.append(i)

                elif zoom > 0: # get the logitech USB cams which usually has zoom =100
                    self.usb_cam_indexes.append(i)
                    cam_indexes.append(i)
                cap.release()
         
        return cam_indexes


    def get_cam_names(self):
        # initialize empty list
        self.usb_cam_names = []
        
        usb_scanner = USBDeviceScanner()
        usb_devices = usb_scanner.list_devices()
        for usb_device in usb_devices:
            if usb_device.product_name == None:
                continue 
            if (usb_device.product_name.endswith('cam')):
                    #print (usb_device, usb_device.vendor_name, usb_device.product_name,usb_device.unique_identifier) 
                    self.usb_cam_names.append(usb_device.product_name)

if __name__ == '__main__':
        
    cams = CamIndex() #noqa
    print(cams.get_cam_indexes())
    print(cams.get_cams_info())