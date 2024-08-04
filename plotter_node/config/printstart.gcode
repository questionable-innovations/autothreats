G00 S1; endstops
G00 E0; no extrusion
G01 S1; endstops
G01 E0; no extrusion
G21; millimeters
G0 F%.1f{{zspeed*60}} Z%.3f{{safe}}; pen park !!Zsafe