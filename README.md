# Raspberry Pi and Radar Project README

## Overview
This repository contains all the necessary files and instructions for setting up and running a Raspberry Pi-based radar project. The project is divided into two main sections: Raspberry Pi setup and Radar setup. Sample radar data is also provided to test the system.

---

## Section 1: Raspberry Pi Setup

### Execution Instructions:
1. Navigate to the `pi/` directory.
2. Edit the `perspective` variable in `recognition.py` to the appropriate axis that you have placed your camera on.
3. Run `python3 server.py` to start server, the server will handle starting of the camera code.

### Input File Format:


### Output Files:
1. `output_x.json` and `output_y.json` - JSON files containing the x and y coordinates of the detected person.


### Hardcoded Addresses:
- In `server.py`, update the IP and PORT fields with appropriate values.

### Hardware Connections:
1. Connect the Raspberry Pi to the camera module.
2. Ensure the Raspberry Pi is connected to a power source.
3. Connect the Raspberry Pi to a monitor.

### Post Processing and Plotting:
1. Run `python3 plot_positions.py` to generate a plot of the detected person's location, and them moving through the space.

---

## Section 2: Radar Setup

### Files and Folders:
1. **radar_data/non-raw - radar code.


### Execution Instructions:
1. Ensure the radar is connected to a computer with the radar software.
2. Update the frames in the software code to an appropriate frame number
3. Use the lab5.cfg file for configuration file used in the software
4. Run `python3 radar_tracking.py` in `radar/non-raw` to detect people and collect data.

### Data:
- Located in `radar/non-raw/locations.txt`

### Hardcoded Addresses:
- In `radar_tracking.py`, update the IP and PORT fields with appropriate values.
- In `radar_tracking.py`, update the directory path to the location where the bin data will be stored.

### External Hardware Setup:
- Radar Module: Connect the radar module to a computer via the provided USB cable.

### Additional Notes:
- Ensure all drivers for the radar module are installed on the Raspberry Pi.
- For detailed radar module setup, refer to the manufacturer's documentation.

### Post Processing and Plotting:
1. Run `python3 plot_positions_radar.py` to generate a plot of the detected person's location, and them moving through the space, use the appropriate path to the data file. You can edit it in the `main()` function.

---
