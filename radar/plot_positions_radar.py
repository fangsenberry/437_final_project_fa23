import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

def parse_radar_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split('|')
            if len(parts) < 3:
                continue
            try:
                timestamp = float(parts[0])
                locations = eval(parts[2].strip())
                for loc in locations:
                    if isinstance(loc, tuple) and len(loc) == 3:
                        x, y, _ = loc
                        data.append((timestamp, x, y))
            except ValueError:
                continue
    return data

def plot_data(data):
    # Extract x and y values
    x_vals = [x for _, x, _ in data]
    y_vals = [y for _, _, y in data]

    # Create a set of line segments
    points = np.array([x_vals, y_vals]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Create a LineCollection from the segments
    lc = LineCollection(segments, cmap='viridis', norm=plt.Normalize(0, 1))
    lc.set_array(np.linspace(0, 1, len(x_vals)))
    lc.set_linewidth(2)

    plt.figure(figsize=(10, 6))
    plt.gca().add_collection(lc)
    plt.xlim(np.min(x_vals) - 1, np.max(x_vals) + 1)
    plt.ylim(np.min(y_vals) - 1, np.max(y_vals) + 1)

    # Plot start and end points
    plt.scatter(x_vals[0], y_vals[0], color='green', marker='o', label='Start')
    plt.scatter(x_vals[-1], y_vals[-1], color='red', marker='o', label='End')

    plt.colorbar(lc, label='Time Progression')
    plt.title('Radar Data 2D Path')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    file_path = 'non-raw/locations2.txt'  # Replace with your file path
    data = parse_radar_data(file_path)
    plot_data(data)

if __name__ == "__main__":
    main()
