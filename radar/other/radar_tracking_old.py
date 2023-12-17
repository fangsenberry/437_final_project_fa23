from kmeans import *
# import required libraries
import struct
import sys
import serial
import binascii
import time
import numpy as np
import math
import socket

import os
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.datasets import make_blobs
from subprocess import run


# Local File Imports
from parse_bin_output import *

CAMERA_FLAG = False
IP = "0.0.0.0"
PORT = 5005

def sendUDPMessage(message, UDP_IP, UDP_PORT):
    # Send a UDP message to the specified IP address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (UDP_IP, UDP_PORT))

# Function to monitor a directory for new folders
def monitor_directory(directory_path):
    # Get the initial list of folders in the directory
    initial_folders = set(os.listdir(directory_path))

    start_time = time.time()

    print("Monitoring directory for new folders...")

    while time.time() - start_time <= 60:
        # Get the current list of folders in the directory
        current_folders = set(os.listdir(directory_path))

        # Find the difference (new folders created)
        new_folders = current_folders - initial_folders

        if new_folders:
            # If a new folder is created, return its name
            folder = new_folders.pop()
            return os.path.join(directory_path, folder)

        # Wait for a short duration before checking again
        time.sleep(5)
    
    return None

def monitor_files(directory_path):
    # Get the initial list of files in the directory
    initial_files = set(os.listdir(directory_path))

    start_time = time.time()

    print("Monitoring directory for new files...")

    while time.time() - start_time <= 60:
        # Get the current list of files in the directory
        current_files = set(os.listdir(directory_path))

        # Find the difference (new files created)
        new_files = current_files - initial_files

        if new_files:
            # If a new file is created, return its name
            file = new_files.pop()
            return os.path.join(directory_path, file)

        # Wait for a short duration before checking again
        time.sleep(5)
    
    return None

def check_for_people(radar_data):
    return (0,0)

def process_radar_data(radar_data):
    global CAMERA_FLAG

    # Check if there are people in the frames
    has_people, num_people = check_for_people(radar_data)

    # Set the camera flag based on the result
    if has_people:
        CAMERA_FLAG = True
        sendUDPMessage(b"1", "0.0.0.0", 5005)
    else:
        CAMERA_FLAG = False
        sendUDPMessage(b"0", "0.0.0.0", 5005)

def parse_raw_ADC(bin_file):
    rawData = np.load(bin_file)
    data = np.array([frame["adcSamples"][:, 128:] for frame in rawData])

def main():
    directory_path = "/Users/wolf/dev/radar/Industrial_Visualizer/binData"

    folder = monitor_directory(directory_path)

    if folder:
        print(f"New folder created: {folder}")

        while True:
            # Monitor the directory for new files
            new_file = monitor_files(folder)

            if new_file:
                print(f"New file created: {new_file}")

                # Parse the new file for raw ADC data
                radar_data = parse_raw_ADC(new_file)

                # Process the radar data
                process_radar_data(radar_data)

            else:
                print("No new file created within 1 minute. Exiting.")
                sys.exit(2)

    else:
        print("No new folder created within 1 minute. Exiting.")
        sys.exit(1)

    try:
        while True:
            # Monitor the directory for new folders
            new_folder = monitor_directory(directory_path)

            # get full path of new folder
            new_folder = os.path.join(directory_path, new_folder)

            if new_folder:
                print(f"New folder created: {new_folder}")

                output_dict = parse_ADC(new_folder)

                print(f"Number of frames: {len(output_dict)}")

                # Process the radar data
                process_radar_data(output_dict)

            else:
                print("No new folder created within 1 minute. Exiting.")
    except KeyboardInterrupt:
        print("Exiting.")
        sendUDPMessage(b"quit", "0.0.0.0", 5005)