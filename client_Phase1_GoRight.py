import sys
import hub
from hub import port         # Port module to set / get Port from LEGO hub
from hub import display      # Display module to control LEGO hub Display Screen
from hub import Image        # Image module to use built-in image
from hub import button       # To use Button on LEGO hub
from hub import led          # To control LED on LEGO hub
from hub import motion       # For current motion status on LEGO hub
from hub import sound
from hub import USB_VCP
from utime import sleep_ms, ticks_ms  # Import delay function and ticks for timing

# Setup Ports, Motors, Sensors
MotorA = port.A.motor        # MotorA defines the port A of Hub
MotorB = port.B.motor        # MotorB defines the port B of Hub
MotorB.default(max_power = 50, stop = 2)

command = bytes([])
message = bytes([])
new_SW = False
safe_State = True
motor_running = False
req = False
motor_end_time = 0
safe_period = 0

def request_Flash_SW(vcp):
    global new_SW
    global message
    global req
    hub.led(3)
    sleep_ms(50)
    message = bytes([35, 1, 122, 0, 0, 0, 111, 0, 0])
    hub.led(8)
    sleep_ms(50)
    vcp.write(message)
    print("Here")
    sleep_ms(100)
    # req = True
    # print("Here")
    new_SW = False
    sys.exit()
    
    

def response_Confirmation(vcp):
    global message
    global safe_State
    global new_SW
    new_SW = True

    hub.led(2)
    sleep_ms(50)
    # print('#hello')
    message = bytes([35, 1, 121, 0, 0, 0, 0, 0, 0])
    hub.led(5)
    vcp.write(message)
    sleep_ms(10)
    if safe_State == True:
        request_Flash_SW(vcp)
        

def response_Flash_Status(vcp):
    global message
    hub.led(4)
    sleep_ms(50)
    message = bytes([35, 1, 124, 0, 0, 0, 0, 0, 0])
    vcp.write(message)
    sleep_ms(10)



def classify_Command(command, vcp):
    hub.led(1)
    sleep_ms(50)
    if command[1] == 120:
        response_Confirmation(vcp)
        sleep_ms(10)
    elif command[1] == 123:
        response_Flash_Status(vcp)
        sleep_ms(10)

def handle_VCP():
    vcp = USB_VCP(0)
    vcp.setinterrupt(3)
    global command
    global safe_State
    global new_SW
    
    if vcp.isconnected():  
        # vcp.CTS
        # command = bytes([1, 120, 0, 0, 0, 0, 0, 0])
        if vcp.any():
            
            command = vcp.readline(vcp.any()).strip()
            sleep_ms(10)
            classify_Command(command, vcp)
            sleep_ms(10)
        if safe_State == True and new_SW == True:
            request_Flash_SW(vcp)
            sleep_ms(10)
    #hub.led(0)

def run_motor():
    global motor_running, motor_end_time, motor_start_time,safe_period
    MotorA.run_for_degrees(30, speed = 50)
    MotorB.run_at_speed(-50)  # Run the motor at a constant speed
    motor_start_time = ticks_ms()  # Record the start time of motor running
    motor_running = True
    motor_end_time = motor_start_time + 5000  # Set the motor end time to 5 seconds after start
    safe_period = motor_end_time + 5000

while True:
    
    current_time = ticks_ms()
    if not motor_running:
            safe_State = False 
            run_motor()
    elif motor_running:
        # Check if motor has been running for more than 5 seconds
        if current_time >= motor_end_time:
            MotorB.brake()  # Brake the motor
            # Turn to safe state and wait for 2 seconds
            safe_State = True
            sleep_ms(10)
            if current_time >= safe_period:
                motor_running = False
    # MotorB.brake()
    # safe_State = True
    handle_VCP()
    # if req == True:
    #     break
    # safe_State = False
