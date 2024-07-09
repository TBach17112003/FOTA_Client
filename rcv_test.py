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
from utime import sleep_ms


vcp = USB_VCP()
MotorB = port.B.motor

while True:
    if vcp.isconnected():  
        # vcp.CTS
        if vcp.any():
            # data = vcp.recv(8, 1000)
            data = vcp.readline(vcp.any()).strip()
            sleep_ms(100)
            vcp.write(data)
            print(data)
            sleep_ms(100)
            if data == b'RUN':
                MotorB.run_at_speed(-50)
                sleep_ms(1000)