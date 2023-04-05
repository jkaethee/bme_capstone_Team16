import serial
import time

# Change port number accordingly
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1)

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))  # Writing to Arduino 
    time.sleep(0.05)
    data = arduino.readline()  # Reading value sent back from Arduino
    return data

def main():
    while True:
        input_val = input("Enter a number (q - Exit): ")
        if (input_val == "q"):
            print("Quit signal received! Exiting program...")
            return
        value = write_read(input_val)
        print(value)

if __name__ == "__main__":
    main()