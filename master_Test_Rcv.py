import serial
import time

# Configure the serial port
serial_port = '/dev/ttyUSB0'  # Adjust this according to your setup
baud_rate = 9600

# Open the serial port
ser = serial.Serial(serial_port, baud_rate, timeout=1)

def read_message():
    while True:
        if ser.in_waiting > 0:
            start_bit = ser.read(1)
            if start_bit == b'\x02':  # Check if the start bit is correct
                message = ser.read(9)  # Read the next 9 bytes (total 10 bytes with start bit)
                end_bit = ser.read(1)
                if end_bit == b'\x03':  # Check if the end bit is correct
                    # Process the message
                    message_data = list(message)
                    address, func_code, data1, data2, data3, data4, crc1, crc2, crc3 = message_data
                    print(f"Received message: {address}, {func_code}, {data1}, {data2}, {data3}, {data4}, {crc1}, {crc2}, {crc3}")
                else:
                    print("End bit incorrect, message discarded")
            else:
                print("Start bit incorrect, message discarded")

try:
    while True:
        read_message()
        time.sleep(0.1)
except KeyboardInterrupt:
    ser.close()
    print("Serial port closed")
