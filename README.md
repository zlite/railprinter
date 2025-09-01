# railprinter

This is code to control two 3D-printing robot arms on rails, cooperating to print a big thing.

The rails are connected to a GRBL controller, which drives the stepper motors for each one. I'm using Rotrics arms to do the 3D printing. I embed the "M118 P2 [your text]" into the Gcode each arm is using to print, which sends the [your text] to the serial port. My laptop reads the serial port communications from each arm with this python script and when it gets a command it sends it to the GRBL controller to drive the appropriate rail stepper to move the arm to its desired position
