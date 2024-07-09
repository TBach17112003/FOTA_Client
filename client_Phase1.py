# LEGO type:standard slot:0 autostart
# DO NOT CHANGE LINE ABOVE

#-----------------------

# Import library, framework
import hub
from hub import port         # Port module to set / get Port from LEGO hub
from hub import display      # Display module to control LEGO hub Display Screen
from hub import Image        # Image module to use built-in image
from hub import button       # To use Button on LEGO hub
from hub import led          # To control LED on LEGO hub
from hub import motion       # For current motion status on LEGO hub
from hub import sound        # For sound adjustment of hub
from hub import USB_VCP      # Set up USB Virtual Com Port
from hub import BT_VCP       # Set up Bluetooth Virtual Com Port
from utime import sleep_ms   # Import delay function                            

#---------------------

# Port Description:
# A: Front Right, Front Left Wheel
# B: Rear Right, Rear Left Wheel

# Setup Ports, Motors, Sensors
vcp = USB_VCP(0)
MotorA = port.A.motor        # MotorA defines the port A of Hub
MotorB = port.B.motor        # MotorB defines the port B of Hub
MotorB.default(max_power = 50, stop = 2)

# Variables
speed = 0
degree = 0
motor_Selector = 0 # 1: Motor A, 2: Motor B
safe_State = True
new_SW = False
is_Running = False

#-----------------------

# Command Description 

# Command: [address; func_code; {data:4 byte}; {CRC: 2 byte}]

# Command Details:

# Phase 1:
# - Notify new SW: [addr; 120; {0; 0; 0; 0}; {xx; xx}]
# - Response Confirmation: [addr; 121; {0; 0; 0; 0}; {xx; xx}]
# - Request flash SW [addr; 122; {0; 0; 0; 0}; {xx; xx}]
# - Safe State: [addr; 124; {0; 0; 0; 111}; {xx; xx}]
# - Unsafe State: [addr; 124; {0; 0; 0; 111}; {xx; xx}]

# Phase 2:
# - Set Motion: [addr; 101; {0; 0; degree; speed}; {xx; xx}]
# - Set PWM: [addr; 102;{0; 0; motor_Select; pwm}; {xx; xx}]
# - Run: [addr; 110; {0; time; 0; speed}; {xx; xx}]
# - Turn_LR: [addr; 111; {0; 0; degree; speed}; {xx; xx}]

# Setup Command
address = 1
data = [0, 0, 0, 0]
func_Code = 0
crc = ["xx", "xx"] #cycle redundancy check
command = [address, func_Code, data[0], data[1], data[2], data[3], crc[0], crc[1]] #each index must be in range of {0; 255}
current_Command = None

# -----------------------

# Setup Message
def get_State():
    global state 
    state = False

    pass 

# Implementation of Command Classification

def notify_New_SW(): #func_Code = 120
    response_Confirmation()
    if (safe_State == True): 
        request_flash_SW()
def response_Confirmation(): #func_Code = 121
    global command 
    command = [1, 121, 0, 0, 0, 0, "xx", "xx"]
    vcp.write(command)

def request_flash_SW():
    global command 
    command = [1, 122, 0, 0, 0, 111, "xx", "xx"]
    vcp.write(command) #func_Code = 122


def classify_Command(command):
    if (command[1] == 120):
        current_Command = notify_New_SW()
    # elif(command[1] == 121):
    #     current_Command = response_Confirmation()
    # elif(command[1] == 122):
    #     current_Command = request_flash_SW()

    return current_Command

while (True):
    if vcp.isconnected():
        if vcp.any():
            command = vcp.readline(vcp.any()).strip()
            sleep_ms(1000)
            current_Command = classify_Command(command)
            sleep_ms(1000)
    if (current_Command):
        current_Command()
        sleep_ms(1000)
        current_Command = None
        sleep_ms(100)
    get_State()
    while (not safe_State):
        MotorB.run_for_time(3000,speed = -50)
        sleep_ms(1000)

