import json
import random
from datetime import datetime, timedelta

def generate_random_data(file_name, num_values, value_range, time_increment_range):
    data = {"frames": []}
    current_time = datetime.now()

    for _ in range(num_values):
        # Generate a random location within the specified range
        location = random.randint(value_range[0], value_range[1])
        
        # Increment time by a random amount within the specified range
        increment = timedelta(seconds=random.randint(time_increment_range[0], time_increment_range[1]))
        current_time += increment

        frame_data = {
            "time": current_time.strftime("%H:%M:%S"),
            "locations": [location]
        }
        data["frames"].append(frame_data)

    # Save data to a JSON file
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage: generate 20 random values within the range 0 to 100,
# with time increments between 1 and 5 seconds
generate_random_data("output_x.json", 100, (0, 100), (1, 5))

# Usage: To generate a file with different parameters, modify the arguments in the generate_random_data function call.