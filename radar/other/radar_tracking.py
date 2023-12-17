# import required libraries
import sys
import time
import numpy as np
import math
import socket

import os
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from subprocess import run

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# Local File Imports
from parse_bin_data import *

from mpl_toolkits.mplot3d import Axes3D

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

def determine_optimal_clusters(data):
    # Using the Elbow Method to find the optimal number of clusters
    silhouette_scores = []
    for n_clusters in range(2, 10):  # Testing for 2 to 9 clusters
        kmeans = KMeans(n_clusters=n_clusters, n_init='auto')
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)
        silhouette_scores.append(score)

    optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
    return optimal_k

def monitor_files(directory_path):
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

def check_for_people(file):
    rawData = np.load(file)
    data = np.array([frame["adcSamples"][:, 128:] for frame in rawData])

    # Compute the Range Profile
    # FFT along the samples per chirp axis (axis=2)
    range_profile = np.fft.fft(data, axis=2)

    # Compute the Range-Doppler Profile
    # FFT along the chirps axis (axis=0)
    range_doppler_profile = np.fft.fft(range_profile, axis=0)

    # You might also want to shift the zero-frequency component to the center
    range_doppler_profile = np.fft.fftshift(range_doppler_profile, axes=0)

    # Preprocess the data
    magnitude = np.abs(range_doppler_profile)
    threshold = np.percentile(magnitude, 95)  # adjust the percentile as needed
    significant_points = np.argwhere(magnitude > threshold)

    # Feature Scaling
    scaler = StandardScaler()
    significant_points_scaled = scaler.fit_transform(significant_points)
    
    # plot_point_cloud(significant_points_scaled)

    # This should be done manually by observing the plot
    optimal_k = determine_optimal_clusters(significant_points_scaled)

    # Apply K-Means Clustering with the optimal number of clusters
    kmeans = KMeans(n_clusters=optimal_k)
    kmeans.fit(significant_points_scaled)

    # Estimating the number of people
    num_people = len(np.unique(kmeans.labels_))
    print(f'Estimated number of people: {num_people}')

    return num_people

def plot_point_cloud(data):
    # Assuming 'data' is a NumPy array of shape (N, 3)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(data[:,0], data[:,1], data[:,2])
    ax.set_xlabel('Range Axis')
    ax.set_ylabel('Doppler Axis')
    ax.set_zlabel('Angle Axis')

    plt.show()


def process_radar_data(file):
    global CAMERA_FLAG, start_time
    start_time = 0
    # Check if there are people in the frames
    num_people = check_for_people(file)

    # Set the camera flag based on the result
    if num_people > 0:
        print(f"{num_people} people detected at {time.time() - start_time} seconds")
        CAMERA_FLAG = True
        # sendUDPMessage(b"1", "0.0.0.0", 5005)
    else:
        print(f"No people detected at {time.time() - start_time} seconds")
        CAMERA_FLAG = False
        # sendUDPMessage(b"0", "0.0.0.0", 5005)

def main():
    # create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)


    global start_time
    start_time = time.time() 
    directory_path = "/Users/wolf/dev/radar/Industrial_Visualizer/binData"

    try:
        folder = monitor_directory(directory_path)

        if folder:
            print(f"New folder created: {folder}")

            # Monitor the directory for new .bin files
            while True:
                bin_file = monitor_files(folder)

                if bin_file:
                    print(f"New file created: {bin_file}")

                    # run parse_bin_output script to get .npy file
                    basename = os.path.basename(bin_file)
                    # remove .bin extension
                    basename = basename[:-4]
                    save_path = os.path.join(data_dir, basename + ".npy")
                    # save_path = "data/" + basename + ".npy"
                    # save_path = os.path.join("data", os.path.basename(bin_file))
                    data, output_file = parse_ADC(bin_file, output_file=save_path)

                    # Process the data
                    process_radar_data(output_file)
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