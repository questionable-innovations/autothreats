from time import sleep
from gcodeplot.gcodeplot import Plotter
from generateGcode import callGCodePlot
import gcodeplot.gcodeplotutils.sendgcode as sendgcode
import serial.tools.list_ports

def classify_device(port):
    # Open a connection to the device
    print("Testing device")
    port.reset_input_buffer()

    port.write(str.encode(";\n"))
    port.flush()
    # Read the response
    exp = port.readline().strip()

    print("Device response: ", exp)

    port.reset_input_buffer()

    # Close the connection
    port.close()

    if exp == b"wrong":
        return "arduino"
    else:
        return "printer"
    return "unknown"

def send_letter(serial, letter):
    assert len(letter) == 1
    serial.reset_input_buffer()
    serial.write(str.encode("letter"))
    print("Sent letter: ", letter)
    print("Received: ", serial.readline())


def sendToPrinter(gcode: str, plotter: Plotter):
    # Unfortunately, the Printer's and Arduino USB ID's are identical. Go figure.
    SERIAL_VENDOR_ID = 0x7523
    SERIAL_PRODUCT_ID = 0x1a86

    ports = serial.tools.list_ports.comports()
    
    printer_serial = None
    arduino_serial = None
    
    for p in ports:
        if p.pid == SERIAL_VENDOR_ID and p.vid == SERIAL_PRODUCT_ID:
            port = serial.Serial(p.device, 115200, timeout=2)
            device = classify_device(port)
            if device == "printer":
                printer_serial = p.device
            elif device == "arduino":
                sleep(2.5)
                arduino_serial = port
    
    if arduino_serial is not None:
        print("Arduino found on port: ", arduino_serial)
        send_letter(arduino_serial,"s")


    if printer_serial is not None:
        print("Printer not found, ignoring")
        print("Printer found on port: ", printer_serial)
        sendSpeed = 115200
        
        sendgcode.sendGcode(port=printer_serial, speed=sendSpeed, commands=gcode, plotter=plotter, variables=plotter.variables, formulas=plotter.formulas)
    else:
        print("WOULD PRINT NOW IF PRINTER EXISTED")
        sleep(20)


    if arduino_serial is not None:
        print("Arduino found on port: ", arduino_serial)
        send_letter(arduino_serial,"e")
        arduino_serial.close()


def main():
    file_name = "test_drawing.svg"
    gcode_out = ""
    with open(file_name, "r") as file:
        data = file.read()
        gcode_out, plotter = callGCodePlot(data)
        
    with open("output.gcode", "w") as file:
        file.write(gcode_out)
        
            
    print(sendToPrinter(gcode_out, plotter))
        
if __name__ == "__main__":
    while True:
        input("Press enter to draw")
        main()
        