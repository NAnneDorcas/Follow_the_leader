import cv2
import numpy as np
import time
import os.path
import easygopigo3 as go
import serial
import json
import _thread

ser = serial.Serial(port="/dev/ttyACM0", baudrate = 115200, timeout=1)

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
global camera
global us_value
myRobot = go.EasyGoPiGo3()

open_file_finish = "trackbar_defaults_finish.txt"

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
        
def init():
    global camera
    camera = cv2.VideoCapture(0)
    
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    camera.read()
    camera.set(cv2.CAP_PROP_WB_TEMPERATURE, white_balance)
    camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    camera.set(cv2.CAP_PROP_AUTO_WB, 0)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def get_finish(finish_threshold):
    finish_threshold = cv2.bitwise_not(finish_threshold)
    img = np.nonzero(finish_threshold[1])
    avg = np.average(img)
    return avg

def read_sensor_data():
    global us_value
    
    while True:
        #get values from pico
        data = ser.readline().strip(b'\n\r')
        data_1 = data.decode("utf-8")
        us_value = json.loads(data_1)

_thread.start_new_thread(read_sensor_data, ())     

         
def main():
    global camera
    global us_value
    
    #us data as dictionary
    us_value = {'mid_distance': 0, 'left_distance': 0, 'right_distance': 0}
    
    
    #time to get fps
    frame_time = 0 #current frame time
    eelmine_frame_time = 0 #previous frame time
    
    #read from file
    read_from_file()
    read_from_file(open_file_finish)
    
    myRobot.set_speed(100)
    
    current_state = "search"
    while True:
        
        #us values
        mid_us = us_value['mid_distance']
        left_us = us_value['left_distance']
        right_us = us_value['right_distance']
        
        print(us_value)
        
        # Read the image from the camera
        ret, frame = camera.read()
        frame = frame[300:340]
        h, w, ch = frame.shape # get camera frame size (height, width, 3 - vÃƒÂ¤rvikanalid
        cv2.rectangle(frame, (0, 0), (w-1, h-1), (255, 255, 255), 1)
        
        #calculate fps ehk me jalgime algset frame time ja eelmist frame time ning labi selle arvutame fpsi
        frame_time  = time.time() #votame aega esimesest frame-st
        fps = 1 / (frame_time - eelmine_frame_time) #jalgime current frame ja eelmist frame aega ning jagame selle 1 sekundiga
        eelmine_frame_time = frame_time 
        fps = int(fps) #teeme fps int
        print(f"fps {fps}")
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Colour detection limits for finish
        lowerLimits_finish = np.array([lH, lS, lV])
        upperLimits_finish = np.array([hH, hS, hV])
        
        #finish threshold
        finish_threshold = cv2.inRange(frame, lowerLimits_finish , upperLimits_finish)
        
        finish_threshold = cv2.bitwise_not(finish_threshold)
        
        #write fps to frame
        #cv2.putText(frame, str(fps), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        #rectange, can comment this out
        #cv2.rectangle(finish_threshold, (0, 0), (w-1, h-1), (255, 255, 255), 20)
        
        
        #camera size and left / right
        cam_mid = 640
        cam_left = cam_mid - 4
        cam_right = cam_mid + 4
        
        #searching finish
        if current_state == "search":
            print("scanning finish")
            #finish location
            finish_location = get_finish(finish_threshold)
            print(f"finish location {finish_location}")
            if finish_location < cam_left:
                myRobot.steer(5,-5)
            elif finish_location > cam_right:
                myRobot.steer(-5,5)
            else:
                myRobot.steer(0,0)
                print("we are in mid")
                current_state = "first move"
            
        #go straight and stopping when there is something in front of us
        elif current_state == "first move":
            if mid_us < 140:
                myRobot.steer(0,0)
                print("stop")
                current_state = "turn"
            else:
                myRobot.steer(100,100)
                print("steer 100")
                
        #searching freedom
        elif current_state == "turn":
            if 670 <= mid_us <= 720 and 110 <= left_us <= 135:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            elif 721 <= mid_us <= 740 and 110 <= left_us <= 135:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            elif 735 <= mid_us <= 745 and 160 <= left_us <= 175:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            elif 780 <= mid_us <= 795 and 155 <= left_us <= 194:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            elif 800 <= mid_us <= 815 and 153 <= left_us <= 165:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            elif 800 <= mid_us <= 815 and 130 <= left_us <= 140:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "go"
            else:
                myRobot.steer(5,-5)
                print("searchin freedom")
                
         #after first turn going straight       
        elif current_state == "go":
            if mid_us < 125:
                myRobot.steer(0,0)
                print("stopped")
                current_state = "turn_left"
            else:
                myRobot.steer(100,100)
                print("steer again 100,100")
              
        #turning left   
        elif current_state == "turn_left":
            if 600 <= mid_us <= 735 and 125 <= right_us <= 165:
                print("turned left")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 530 <= mid_us <= 600 and 180 <= right_us <= 200:
                print("turned..")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 765 <= mid_us <= 800 and 125 <= right_us <= 165:
                print("turned left big")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 470 <= mid_us <= 480 and 125 <= right_us <= 145:
                print("tuqrned left, very close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 500 <= mid_us <= 530 and 115 <= right_us <= 135:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 645 <= mid_us <= 660 and 170 <= right_us <= 180:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 890 <= mid_us <= 1015 and 140 <= right_us <= 155:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 890 <= mid_us <= 1110 and 155 <= right_us <= 170:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 625 <= mid_us <= 635 and 170 <= right_us <= 180:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 630 <= mid_us <= 650 and 90 <= right_us <= 130:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            elif 1200 <= mid_us <= 1300 and 115 <= right_us <= 135:
                print("turned left, close")
                myRobot.steer(0,0)
                current_state = "straight_again"
            else:
                myRobot.steer(-5,5)
                print("turning left")
                
        #going straight
        elif current_state == "straight_again":
            if mid_us < 180:
                myRobot.steer(0,0)
                print("stopped again")
                current_state = "finish"
            else:
                myRobot.steer(100,100)
                print("straight_again")
            
        #searching finish
        elif current_state == "finish":
            #finish location
            finish_location = None
            finish_location = get_finish(finish_threshold)
            print(f"finish location {finish_location}")
            myRobot.steer(-10,10)
            print("scanning finish")
            if finish_location < cam_left:
                myRobot.steer(5,-5)
            elif finish_location > cam_right:
                myRobot.steer(-5,5)
            if 635 <= finish_location <= 645:
                myRobot.steer(0,0)
                print(f"finish location {finish_location}")
                print("we have eyes on target ")
                current_state = "target_secured"
                 
        #going to finish
        elif current_state == "target_secured":
            finish_location = get_finish(finish_threshold)
            print(f"finish location {finish_location}")
            if mid_us < 85:
                myRobot.steer(0,0)
                print(f"finish location {finish_location}")
                print("we are in finish")
            else:
                myRobot.steer(100,100)
                print(f"finish location {finish_location}")
                print("going to finish")
             
            
        #cv2.imshow("Original", frame)
        cv2.imshow("FinishThreshold", finish_threshold)

        # Quit the program when "q" is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    # When everything done, release the camera
    print("closing program")
    camera.release()
    cv2.destroyAllWindows()
    myRobot.stop()

if __name__ == "__main__":
    init()
    main()



