from time import sleep
from gcodeplot.gcodeplot import Plotter, processCode
from generateGcode import callGCodePlot
import gcodeplot.gcodeplotutils.sendgcode as sendgcode
import serial.tools.list_ports
import websockets
import asyncio


import re

gcode_regex = r"(?:G0?[01].+(?:[XYZ]\d))|(?:G28)"

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

    if exp == b"wrong":
        return "arduino"
    else:
        return "printer"
    return "unknown"

def send_letter(serial, letter):
    assert len(letter) == 1
    serial.reset_input_buffer()
    serial.write(str.encode(letter))
    print("Sent letter: ", letter)
    print("Received: ", serial.readline())

def send_gcode_file(serial, plotter, file_name):
    sleep(2)
    print("SENDING FILE", file_name)
    file_content = ""
    with open(file_name, "r") as file:
        file_content = file.read()
    
    commands = processCode(file_content, plotter)
    flat_commands = []
    for command in commands:
        flat_commands += command.split("\n")
    
    sleep(0.5)
    serial.reset_input_buffer()
    for command in flat_commands:
        serial.reset_input_buffer()
        print("Sending command: ", command)
        serial.write(str.encode(command + "\n"))
        
        # if re.match(gcode_regex, command):
        while(1): # Wait until the former gcode has been completed.
            text = serial.readline()
            if text:
                print("Received: ", text)
            if text.startswith(b'ok'):
                break

        else:
            print("Not waiting for response")



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
            sleep(2.5)
            device = classify_device(port)
            if device == "printer":
                print("Printer found on port: ", p.device)
                printer_serial = port
            elif device == "arduino":
                print("Arduino found on port: ", p.device)
                arduino_serial = port
    
    # FIRST - run startup
    if printer_serial is not None:
        # processCode
        send_gcode_file(printer_serial, plotter, "config/startup.gcode")
        send_gcode_file(printer_serial, plotter, "config/printstart.gcode")



    if arduino_serial is not None:
        send_letter(arduino_serial,"s")
        sleep(5)


    if printer_serial is not None:
        print("Printer not found, ignoring")
        
        sendgcode.sendGcode(printer_serial, commands=gcode, plotter=plotter, variables=plotter.variables, formulas=plotter.formulas)
        send_gcode_file(printer_serial, plotter, "config/printend.gcode")

    else:
        print("WOULD PRINT NOW IF PRINTER EXISTED")
        sleep(20)


    if arduino_serial is not None:
        print("Arduino found on port: ", arduino_serial)
        send_letter(arduino_serial,"e")
        sleep(1)
        arduino_serial.close()
    
    if printer_serial is not None:
        
        printer_serial.close()


def main():
    file_name = "test_drawing.svg"
    gcode_out = ""
    with open(file_name, "r") as file:
        data = file.read()
        gcode_out, plotter = callGCodePlot(data)
        
    with open("output.gcode", "w") as file:
        file.write(gcode_out)
        
            
    print(sendToPrinter(gcode_out, plotter))

async def run():
    async with websockets.connect("wss://autothreat-svg-generator.host.qrl.nz/jobs", max_size=1_000_000_000) as websocket:
        while True:
            data = await websocket.recv()
            with open("test_drawing.svg", "+w") as f:
                f.write(data)
            main()
                
        
if __name__ == "__main__":
    while True: 
        input("Press enter to draw")
        
    asyncio.get_event_loop().run_until_complete(run())
