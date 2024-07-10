# LEGO type:standard slot:1 autostart
# DO NOT CHANGE LINE ABOVE
import hub
from hub import port         # Port module to set / get Port from LEGO hub
from hub import display      # Display module to control LEGO hub Display Screen
from hub import Image        # Image module to use built-in image
from hub import button       # To use Button on LEGO hub
from hub import led          # To control LED on LEGO hub
from hub import motion       # For current motion status on LEGO hub
from hub import sound
from hub import USB_VCP
from hub import BT_VCP
from utime import sleep_ms, ticks_ms  # Import delay function and ticks for timing


# Setup Ports, Motors, Sensors
vcp = USB_VCP(0)
MotorA = port.A.motor        # MotorA defines the port A of Hub
MotorB = port.B.motor        # MotorB defines the port B of Hub
MotorB.default(max_power = 50, stop = 2)

safe_State = False
motor_running = False
motor_end_time = 0

command = bytes([])
message = bytes([])

def get_State():
    global safe_State, motor_running
    # If either motor is running, set safe_State to False
    if MotorA.busy(1) or MotorB.busy(1):
        safe_State = False
        motor_running = True
    else:
        safe_State = True
        motor_running = False

def response_Confirmation():
    hub.led(2)
    sleep_ms(500)
    message = bytes([35, 1, 121, 0, 0, 0, 0, 0, 0])
    vcp.write(message)
    sleep_ms(100)
    if safe_State == True:
        request_flash_SW()

def response_Flash_Status():
    hub.led(1)
    sleep_ms(500)
    message = bytes([35, 1, 124, 0, 0, 0, 0, 0, 0])
    vcp.write(message)
    sleep_ms(100)

def request_flash_SW():
    hub.led(3)
    sleep_ms(500)
    message = bytes([35, 1, 122, 0, 0, 0, 111, 0, 0])
    vcp.write(message)
    sleep_ms(100)

def classify_Command(command):
    if command[1] == 120:
        response_Confirmation()
    elif command[1] == 123:
        response_Flash_Status()

def handle_VCP():
    if vcp.isconnected():  
        # vcp.CTS
        if vcp.any():
            # data = vcp.recv(8, 1000)
            command = vcp.readline(vcp.any()).strip()
            sleep_ms(100)
            classify_Command(command)
            sleep_ms(100)

def run_motor():
    global motor_running, motor_end_time
    if not motor_running:
        MotorB.run_for_time(3000, speed=50)
        motor_running = True
        motor_end_time = ticks_ms() + 3000  # Set the motor end time
        sleep_ms(500)

while True:
    if safe_State == False:
        run_motor()
    get_State()
    handle_VCP()
    