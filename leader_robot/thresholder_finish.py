
import numpy as np
import cv2
import time
import os.path

# Colour detection limits
lV = 125 # low value
lS = 125 # low saturation
lH= 125 # low hue
hV = 255 # high value
hS = 255 # high saturation
hH = 179 #high hue
white_balance = 500
exposure = 300
camera = None

write_file = "trackbar_defaults_finish.txt"

# functions to colour detection limits
def update_low_value(new):
    global lV
    lV = new

def update_low_saturation(new):
    global lS
    lS = new

def update_low_hue(new):
    global lH
    lH = new
    
def update_high_hue(new):
    global hH
    hH= new
    
def update_high_value(new):
    global hV
    hV = new

def update_high_saturation(new):
    global hS
    hS = new

def update_white_balance(new):
    global white_balance
    white_balance = new
    camera.set(cv2.CAP_PROP_WB_TEMPERATURE, white_balance)
    
def update_exposure(new):
    global exposure
    exposure = new
    camera.set(cv2.CAP_PROP_EXPOSURE, exposure)

def write_values_to_file(path_of_text_file):
    with open(path_of_text_file, "w") as file: #w means write
        file.write(f"low_hue = {lH}\n")
        file.write(f"high_hue = {hH}\n")
        file.write(f"low_saturation = {lS}\n")
        file.write(f"high_saturation = {hS}\n")
        file.write(f"low_value = {lV}\n")
        file.write(f"high_value = {hV}\n")
        file.write(f"white_balance_temperature = {white_balance}\n")
        file.write(f"exposure = {exposure}")
        

def get_values_from_file(path_of_text_file):
    #check if the txt file exists
    check_file = os.path.isfile(path_of_text_file)
    print(check_file)
    #make global to get it
    global lH
    global hH
    global lS
    global hS
    global lV
    global hV
    global white_balance
    global exposure
    
    #read file
    if check_file:
        file = open(write_file, "r")
        content = file.readlines()
        for file_content in content:
            seperate_text = file_content.split()
            trackbar_value = seperate_text[-1]
            #print(trackbar_value, seperate_text[0])
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
                
        file.close
    else:
        print("faili pole")
        
    

def main():
    global camera
    #time to get fps
    frame_time = 0 #current frame time
    eelmine_frame_time = 0 #previous frame time
    
    # Open the camera
    camera = cv2.VideoCapture(0)
    camera.read()
    #calling it out so it will not start changing them automatically
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    camera.set(cv2.CAP_PROP_AUTO_WB, 0)
    
    #detector
    #detector = cv2.SimpleBlobDetector_create(blobparams)

    # Create a named window and name it "Threshold" so trackbar will be in the same window where is the picture
    cv2.namedWindow("Threshold")
    cv2.namedWindow("bar")
    #cv2.createTrackbar(name, name of the window where trackbar is, slider value, max value, callback fn)
    #trackbar to control low and high HSV and exposure and white balance temperature
    get_values_from_file(write_file) #call out function, this function will get values from file
    cv2.createTrackbar("low_hue", "bar", int(lH), 179, update_low_hue)
    cv2.createTrackbar("high_hue", "bar", int(hH), 179, update_high_hue)
    cv2.createTrackbar("low_saturation", "bar", int(lS), 255, update_low_saturation)
    cv2.createTrackbar("high_saturation", "bar", int(hS), 255, update_high_saturation)
    cv2.createTrackbar("low_value", "bar", int(lV), 255, update_low_value)
    cv2.createTrackbar("high_value ", "bar", int(hV), 255, update_high_value)
    cv2.createTrackbar("white_balance_temperature", "bar", int(white_balance), 6500, update_white_balance)
    cv2.createTrackbar("exposure", "bar", int(exposure), 500, update_exposure)
        
    while True:
        # Read the image from the camera
        ret, frame = camera.read()
        frame = frame[300:340]
        # get camera frame size (height, width, ch = 3 == vÃ¤rvikanalid)
        h, w, ch = frame.shape
        #to detect half object
        cv2.rectangle(frame, (0, 0), (w-1, h-1), (255, 255, 255), 1)
        
        #calculate fps ehk me jalgime algset frame time ja eelmist frame time ning labi selle arvutame fpsi
        frame_time  = time.time() #votame aega esimesest frame-st
        fps = 1 / (frame_time - eelmine_frame_time) #jalgime current frame ja eelmist frame aega ning jagame selle 1 sekundiga
        eelmine_frame_time = frame_time 
        
        fps = int(fps) #teeme fps int
        
        #frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Colour detection limits
        lowerLimits = np.array([lH, lS, lV])
        upperLimits = np.array([hH, hS, hV])

        # Our operations on the frame come here
        threshold = cv2.inRange(frame, lowerLimits, upperLimits)
        
        threshold = cv2.bitwise_not(threshold)
        #contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on the original frame
        #cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        # Write fps to frame
        print(f"fps {fps}")
        


        cv2.imshow("Original", frame)
        # Display the resulting frame
        cv2.imshow("Threshold", threshold)

        # Quit the program when "q" is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    # When everything done, release the camera
    print("closing program")
    camera.release()
    cv2.destroyAllWindows()
    write_values_to_file(write_file)



if __name__ == "__main__":
    main()
