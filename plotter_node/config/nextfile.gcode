G91;
G0 F%.1f{{zspeed*60}} Z%.3f{{safe}}; pen park !!Zsafe
G90; absolute
G00 F3000.0 X191 Y211; Top Right Point
G00 F3000.0 Z0.500; Down to the paper
G00 F3000.0 X175 Y0; Down to the paper
G00 F3000.0 Z{{safe}}; Down to the paper
G00 F3000.0 X0 Y0; Down to the paper

