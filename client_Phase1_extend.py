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
from utime import sleep_ms, ticks_ms  # Import delay function and ticks for timing

#---------------------

# Port Description:
# A: Front Right, Front Left Wheel
# B: Rear Right, Rear Left Wheel

# Setup Ports, Motors, Sensors
vcp = USB_VCP(0)
MotorA = port.A.motor        # MotorA defines the port A of Hub
MotorB = port.B.motor        # MotorB defines the port B of Hub
MotorB.default(max_power = 50, stop=2)

# Variables
speed = 0
degree = 0
motor_Selector = 0  # 1: Motor A, 2: Motor B
safe_State = True
new_SW = False
is_Running = False
current_Command = None
current_state = False
motor_running = False
motor_end_time = 0

# Setup Command
address = 1
data = [0, 0, 0, 0]
func_Code = 0
crc = ["xx", "xx"]  # cycle redundancy check
command = [address, func_Code, data[0], data[1], data[2], data[3], crc[0], crc[1]]  # each index must be in range of {0; 255}

# -----------------------

# Setup Message
def get_State():
    global safe_State, motor_running
    # If either motor is running, set safe_State to False
    if MotorA.busy(1) or MotorB.busy(1):
        safe_State = False
        motor_running = True
    else:
        safe_State = True
        motor_running = False

# Implementation of Command Classification
def notify_New_SW():  # func_Code = 120
    # Change LED color
    hub.led(1)  # Assuming 1 sets the LED to a specific color
    sleep_ms(1000)  # Wait for 1 second
    hub.led(0)  # Reset the LED color, assuming 0 turns it off

    # Send response back to the master
    response_Confirmation()

def response_Confirmation():  # func_Code = 121
    global command
    # Construct the message with start and end bits
    start_bit = 2
    end_bit = 3
    response_message = [start_bit, 1, 121, 0, 0, 0, 111, 0, 0, end_bit]
    vcp.write(bytes(response_message))
    sleep_ms(100)

def classify_Command(command):
    if command[1] == 120:
        notify_New_SW()
        sleep_ms(100)

def handle_vcp():
    global current_Command
    if vcp.isconnected():
        if vcp.any():
            command = vcp.read(vcp.any()).strip()
            sleep_ms(100)
            classify_Command(command)
            sleep_ms(100)

def run_motor():
    global motor_running, motor_end_time
    if not motor_running:
        MotorB.run_for_time(3000, speed=-50)
        motor_running = True
        motor_end_time = ticks_ms() + 3000  # Set the motor end time
        sleep_ms(500)

# Main loop
while True:
    handle_vcp()
    sleep_ms(100)
    get_State()
    if not safe_State:
        run_motor()
    else:
        # Check if the motor running time has ended
        if motor_running and ticks_ms() >= motor_end_time:
            motor_running = False
    sleep_ms(100)
