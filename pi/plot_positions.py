import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.collections import LineCollection

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_locations_and_times(json_data):
    times = []
    locations = []
    for frame in json_data['frames']:
        if frame['locations']:
            times.append(datetime.strptime(frame['time'], "%H:%M:%S"))
            locations.append(frame['locations'][0])
    return times, locations

def synchronize_and_interpolate(x_times, x_locs, y_times, y_locs):
    # Convert times to seconds from the start
    start_time = min(x_times[0], y_times[0])
    x_seconds = [(t - start_time).total_seconds() for t in x_times]
    y_seconds = [(t - start_time).total_seconds() for t in y_times]

    # Common timeline: from 0 to the max time, in 1-second intervals
    timeline = np.arange(0, max(x_seconds[-1], y_seconds[-1]) + 1)

    # Interpolate locations
    x_interp = np.interp(timeline, x_seconds, x_locs)
    y_interp = np.interp(timeline, y_seconds, y_locs)

    return x_interp, y_interp

def plot_movement(x_coords, y_coords):
    plt.figure(figsize=(10, 10))
    
    # Create a set of line segments so that we can color each one individually
    points = np.array([x_coords, y_coords]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap='viridis', norm=plt.Normalize(0, 1))
    
    # Set the values used for colormapping
    lc.set_array(np.linspace(0, 1, len(x_coords)))
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    
    # Plot start and end points
    plt.scatter(x_coords[0], y_coords[0], color='green', marker='o', label='Start')
    plt.scatter(x_coords[-1], y_coords[-1], color='red', marker='o', label='End')

    plt.colorbar(lc, label='Time Progression')
    plt.title('Movement Tracking')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    x_data = read_json('output_x.json')
    y_data = read_json('output_y.json')

    x_times, x_coords = extract_locations_and_times(x_data)
    y_times, y_coords = extract_locations_and_times(y_data)

    # Synchronize and interpolate
    x_interp, y_interp = synchronize_and_interpolate(x_times, x_coords, y_times, y_coords)

    plot_movement(x_interp, y_interp)

if __name__ == "__main__":
    main()
