import cv2
import numpy as np
import time
import os.path
from gopigo import *

global camera

# Colour detection limits for finish detection
lV = 125 # low value
lS = 125 # low saturation
lH= 125 # low hue
hV = 255 # high value
hS = 255 # high saturation
hH = 179 #high hue

#other stuff
white_balance = 500
exposure = 300

open_file_finish = "trackbar_defaults_robot.txt"

def read_from_file(read_of_text_file = open_file_finish):
    check_file = os.path.isfile(read_of_text_file)
    
    #make global to get it
    global lH, hH, lS, hS, lV, hV, white_balance, exposure
    
    #read file
    if check_file:
        file = open(open_file_finish, "r")
        content = file.readlines()
        for file_content in content:
            seperate_text = file_content.split()
            trackbar_value = seperate_text[-1]
            #change trackbar value
            if seperate_text[0] == "low_hue":
                lH = int(trackbar_value)
            if seperate_text[0] == "high_hue":
                hH = int(trackbar_value)
            if seperate_text[0] == "low_saturation":
                lS = int(trackbar_value)
            if seperate_text[0] == "high_saturation":
                hS = int(trackbar_value)
            if seperate_text[0] == "low_value":
                lV = int(trackbar_value)
            if seperate_text[0] == "high_value":
                hV = int(trackbar_value)
            if seperate_text[0] == "white_balance_temperature":
                white_balance = int(trackbar_value)
            if seperate_text[0] == "exposure":
                exposure = int(trackbar_value)
            file.close()
    else:
        print("finishi txt faili pole")
        
def get_leader_location(threshold):
    #get leader robot location
    threshold = cv2.bitwise_not(threshold)
    img = np.nonzero(threshold)[1]
    mat = np.nonzero(threshold)
    su = 0
    for li in mat:
        su = su + sum(li)   
    avg = np.mean(img)
    size_of_cylinder = 69529600 - su
    print("size", size_of_cylinder)
    return avg, size_of_cylinder

def bang_bang_hysteresis(leader_location):
    #move robot according to leader robot
    if leader_location > 325 :
        left()
        print("left")
    elif leader_location < 315:
        print("right")
        right()
    elif 315 <= leader_location <= 325:
        forward()

   
def init():
    global camera
    camera = cv2.VideoCapture(0)
    
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    camera.read()
    camera.set(cv2.CAP_PROP_WB_TEMPERATURE, white_balance)
    camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    camera.set(cv2.CAP_PROP_AUTO_WB, 0)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

  
def main():
    global camera
    
    #time to get fps
    frame_time = 0 #current frame time
    eelmine_frame_time = 0 #previous frame time
    
    
    #read from file
    read_from_file()
    #custom names
    read_from_file(open_file_finish)
    
    set_speed(60)
    area_status = "Start"
    
    try: 
        while True:
            # Read the image from the camera
            ret, frame = camera.read()
            frame = frame[300:380]
            h, w, ch = frame.shape # get camera frame size (height, width, 3 - vÃƒÂ¤rvikanalid
            
            #calculate fps ehk me jalgime algset frame time ja eelmist frame time ning labi selle arvutame fpsi
            frame_time  = time.time() #votame aega esimesest frame-st
            fps = 1 / (frame_time - eelmine_frame_time) #jalgime current frame ja eelmist frame aega ning jagame selle 1 sekundiga
            eelmine_frame_time = frame_time 
            fps = int(fps) #teeme fps int
            print(f"fps {fps}")
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Colour detection limits for finish
            lowerLimits = np.array([lH, lS, lV])
            upperLimits = np.array([hH, hS, hV])
            
            #operation on the frame
            threshold = cv2.inRange(frame, lowerLimits, upperLimits)
            
            threshold = cv2.bitwise_not(threshold)
                        
            #function callout
            leader_location = get_leader_location(threshold)[0]
            bang_bang_hysteresis(leader_location)
            area_of_cylinder = get_leader_location(threshold)[1]
            print("AREA", area_of_cylinder)
            print("LOCATION", leader_location)
            
            print(f"location: {leader_location}")
            print(area_status)
           # bang_bang_hysteresis(leader_location)
             
            if area_status == "Start":
                if area_of_cylinder < 52000000:
                    area_status = "Fast"
                elif area_of_cylinder > 65000000:
                    area_status = "Slow"
                else :
                    area_status = "Normal"
            elif area_status == "Fast":
                if area_of_cylinder > 56000000:
                    area_status = "Slow"
                elif area_of_cylinder > 52000000:
                    area_status = "Normal"
                else:
                    set_speed(70)
            elif area_status == "Slow":
                if area_of_cylinder < 52000000:
                    area_status = "Fast"
                elif area_of_cylinder < 56000000:
                    area_status = "Normal"
                else:
                    set_speed(10)
            else:
                if area_of_cylinder < 52000000:
                    area_status = "Fast"
                elif area_of_cylinder > 56000000:
                    area_status = "Slow"
                else:
                    set_speed(50)
           
            #cv2.imshow("original", frame)
            cv2.imshow("Thresholded", threshold)
            
            # Quit the program when "q" is pressed
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
            
    except KeyboardInterrupt:
        print("Got KeyboardInterrupt, closing, GOODBYE!")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        stop()

if __name__ == "__main__":
    init()
    main()
