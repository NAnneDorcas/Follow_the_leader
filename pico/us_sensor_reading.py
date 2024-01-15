from machine import UART, Pin
import time
import json

uart = UART(0, baudrate = 115200, tx=Pin(0), rx=Pin(1))
#right sensor pins
right_echo_pin = 7 
right_trig_pin = 6 

#left sensor pins
left_echo_pin = 2 
left_trig_pin = 3

mid_trig_pin = 4
mid_echo_pin = 5

delay_us = 10 

left_trigger = Pin(left_trig_pin, Pin.OUT)
left_echo = Pin(left_echo_pin, Pin.IN)

right_trigger = Pin(right_trig_pin, Pin.OUT)
right_echo = Pin(right_echo_pin, Pin.IN)

mid_trigger = Pin(mid_trig_pin, Pin.OUT)
mid_echo = Pin(mid_echo_pin, Pin.IN)

def mid_get_ultrasonic_reading(timeout_us=100_000, default_value=-1):
    method_start_us = time.ticks_us()
    mid_trigger.high()
    time.sleep_us(delay_us)
    mid_trigger.low()
    
    signal_rise = time.ticks_us()
    signal_fall = signal_rise   
    
    while mid_echo.value() == 0:
        signal_rise = time.ticks_us()
        if time.ticks_diff(signal_rise, method_start_us) > timeout_us:
            return default_value

    while mid_echo.value() == 1:
        signal_fall = time.ticks_us()
        if time.ticks_diff(signal_fall, method_start_us) > timeout_us:
            return default_value

    mid_duration_us = signal_fall - signal_rise
    distance_from_mid = mid_duration_us / 5.8
    
    return distance_from_mid



def left_get_ultrasonic_reading(timeout_us=100_000, default_value=-1):
    method_start_us = time.ticks_us()
    left_trigger.high()
    time.sleep_us(delay_us)
    left_trigger.low()
    
    signal_rise = time.ticks_us()
    signal_fall = signal_rise   
    
    while left_echo.value() == 0:
        signal_rise = time.ticks_us()
        if time.ticks_diff(signal_rise, method_start_us) > timeout_us:
            return default_value
        
    while left_echo.value() == 1:
        signal_fall = time.ticks_us()
        if time.ticks_diff(signal_fall, method_start_us) > timeout_us:
            return default_value

    left_duration_us = signal_fall - signal_rise
    distance_from_left = left_duration_us / 5.8
    
    return distance_from_left

    
def right_get_ultrasonic_reading(timeout_us=200_000, default_value=-1):
    method_start_us = time.ticks_us()
    right_trigger.high()
    time.sleep_us(delay_us)
    right_trigger.low()
    signal_rise = time.ticks_us()
    signal_fall = signal_rise

    while right_echo.value() == 0:
        signal_rise = time.ticks_us()
        if time.ticks_diff(signal_rise, method_start_us) > timeout_us:
            return default_value

    while right_echo.value() == 1:
        signal_fall = time.ticks_us()
        if time.ticks_diff(signal_fall, method_start_us) > timeout_us:
            return default_value

    right_duration_us = signal_fall - signal_rise
    distance_from_right = right_duration_us / 5.8
    
    return distance_from_right
def send_data_to_raspberry_pi(sensor_distances):
    json_string = json.dumps(sensor_distances)
    uart.write(json_string + '\n')
 
def main():
    while True:
        mid_dist = mid_get_ultrasonic_reading()
        left_dist = left_get_ultrasonic_reading()
        right_dist = right_get_ultrasonic_reading()
        
        #creating dictionary
        sensor_distances = {
            "mid_distance": mid_dist,
            "left_distance": left_dist,
            "right_distance": right_dist
            }
        send_data_to_raspberry_pi(json.dumps(sensor_distances))
        print(json.dumps(sensor_distances))
        time.sleep(0.25)
        
    
if __name__ == "__main__":
    # Run the main function
    main()


