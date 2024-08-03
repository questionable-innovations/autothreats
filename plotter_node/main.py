from gcodeplot.gcodeplot import Plotter
from generateGcode import callGCodePlot
import gcodeplot.gcodeplotutils.sendgcode as sendgcode
import serial.tools.list_ports

def sendToPrinter(gcode: str, plotter: Plotter):
    VENDOR_ID = 0x1a86
    PRODUCT_ID = 0x7523
    ports = serial.tools.list_ports.comports()
    
    printer_port = None
    
    for p in ports:
        if p.pid == PRODUCT_ID and p.vid == VENDOR_ID:
            printer_port = p.device
    
    if printer_port is None:
        print("Printer not found, ignoring")
        return
    
    print("Printer found on port: ", printer_port)
    sendSpeed = 115200
    
    sendgcode.sendGcode(port=printer_port, speed=sendSpeed, commands=gcode, plotter=plotter, variables=plotter.variables, formulas=plotter.formulas)


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
    main()
        