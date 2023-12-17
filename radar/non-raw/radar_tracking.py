# import required libraries
import sys
import time
import numpy as np
import math
import socket

import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from subprocess import run
from sklearn.metrics import silhouette_score

import warnings


# Local File Imports
from parse_bin_output import *

warnings.filterwarnings("ignore", category=FutureWarning)

CAMERA_FLAG = False
PORT = 5000
IP = "172.16.120.188"

def sendUDPMessage(message, UDP_IP, UDP_PORT):
    # Send a UDP message to the specified IP address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (UDP_IP, UDP_PORT))

def monitor_directory(directory_path):
    """
    Monitors a directory for new subdirectories.

    Args:
        directory_path (str): The path to the directory to monitor.

    Returns:
        str: The path to the new subdirectory.
    """
    # Get the initial list of folders in the directory
    initial_folders = set(os.listdir(directory_path))

    start_time = time.time()

    print("Monitoring directory for new folders...")

    while time.time() - start_time <= 30:
        # Get the current list of folders in the directory
        current_folders = set(os.listdir(directory_path))

        # Find the difference (new folders created)
        new_folders = current_folders - initial_folders

        if new_folders:
            # If a new folder is created, return its name
            folder = new_folders.pop()
            return os.path.join(directory_path, folder)

        # Wait for a short duration before checking again
        time.sleep(1)
    
    return None

def monitor_files(directory_path):
    """
    Monitors a directory for new files.

    Args:
        directory_path (str): The path to the directory to monitor.

    Returns:
        str: The path to the new file.
    """
    # Get the initial list of files in the directory
    initial_files = set(os.listdir(directory_path))

    start_time = time.time()

    print("Monitoring directory for new files...")

    while time.time() - start_time <= 5:
        # Get the current list of files in the directory
        current_files = set(os.listdir(directory_path))

        # Find the difference (new files created)
        new_files = current_files - initial_files

        if new_files:
            # If a new file is created, return its name
            file = new_files.pop()
            return os.path.join(directory_path, file)

        # Wait for a short duration before checking again
        time.sleep(0.1)
    
    return None

def determine_optimal_clusters(xyz, max_k=5):
    """
    Determines the optimal number of clusters for the given XYZ data using the silhouette score.

    Args:
        xyz (array-like): The XYZ coordinates.
        max_k (int): The maximum number of clusters to consider.

    Returns:
        int: The optimal number of clusters.
    """
    best_k = 1
    best_score = -1

    # Handle k=1 separately
    if len(xyz) > 1:
        kmeans = KMeans(n_clusters=1, random_state=0).fit(xyz)
        # best_score = 0  # Or use some other default scoring for single cluster
        # TODO: Fix default scoring for single cluster
        # Use inertia as a measure for a single cluster
        best_score = -kmeans.inertia_  # Negate inertia because lower inertia is better, but we want higher score to be better

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=0).fit(xyz)
        labels = kmeans.labels_
        score = silhouette_score(xyz, labels)

        if score > best_score:
            best_score = score
            best_k = k

    return best_k

def get_coordinates(centroids):
    """
    Extracts and prints the coordinates of centroids.

    Args:
        centroids (array-like): The centroids from which to extract coordinates.

    Returns:
        list: A list of tuples representing the coordinates of each centroid.
    """
    coords = []
    for i, centroid in enumerate(centroids):
        x, y, z = centroid
        coords.append((x, y, z))
        # print(f"Centroid {i}: ({x}, {y}, {z})")

    return coords

def check_for_people(output_dict):
    """
    This function checks for people in an output dictionary. It uses a point cloud
    from each frame to determine the number of clusters representing people and
    their locations.

    Args:
    output_dict (dict): A dictionary containing frame data with point clouds.

    Returns:
    tuple: A tuple containing the maximum number of people and their locations.
    """
    THRESHOLD = 6
    total_people = 0
    frames = 0
    locations = []

    for frame, data in enumerate(output_dict):
        if "pointCloud" in data:
            if data['pointCloud'].shape[0] > THRESHOLD:
                xyz = data['pointCloud'][:, 0:3]
                optimal_clusters = determine_optimal_clusters(xyz)

                kmeans = KMeans(n_clusters=optimal_clusters, random_state=0).fit(xyz)
                centroids = kmeans.cluster_centers_

                coords = get_coordinates(centroids)
                locations.append(coords)
                total_people += len(centroids)
                frames += 1

    if frames > 0:
        max_people = math.floor(total_people / frames)
        if max_people > 1:
            max_people -= 1
    else:
        max_people = 0
    return max_people, locations

def process_radar_data(output_dict, file, send=True):
    """
    Processes radar data to detect people and set a camera flag based on detection.

    Args:
        output_dict (dict): The output dictionary containing radar data.

    Globals:
        CAMERA_FLAG (bool): A flag to indicate camera status.
        start_time (float): The time when the process started.
    """
    global CAMERA_FLAG, start_time

    num_people, locations = check_for_people(output_dict)
    time_passed = time.time() - start_time
    seconds = time_passed % (24 * 3600)

    if num_people > 0:
        print(f"{num_people} people detected at {seconds} seconds")
        # print(f"Locations: {locations}")
        CAMERA_FLAG = True
        if send: sendUDPMessage(b"1", IP, PORT)
        file.write(f"{seconds}|{num_people}|{locations}\n")
    else:
        print(f"No people detected at {seconds} seconds")
        CAMERA_FLAG = False
        if send: sendUDPMessage(b"0", IP, PORT)

def main():
    """
    The main function.

    Globals:
        start_time (float): The time when the process started.
    """

    global start_time
    start_time = time.time() 
    directory_path = "/Users/wolf/dev/radar/Industrial_Visualizer/binData"

    try:
        folder = monitor_directory(directory_path)

        if folder:
            print(f"New folder created: {folder}")

            with open("locations.txt", "w") as f:


                # Monitor the directory for new .bin files
                while True:
                    bin_file = monitor_files(folder)

                    if bin_file:
                        print(f"New file created: {bin_file}")

                        # Process the data
                        output_dict = parse_ADC(bin_file)

                        # Process the data
                        process_radar_data(output_dict, f, send=True)
        else:
            print("No new folder created within 30 seconds. Exiting.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
