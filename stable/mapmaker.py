# import matplotlib.pyplot as plt
# import csv

# # with open('your_file.csv', mode='r') as file:
# #     csv_reader = csv.reader(file)
# #     for row in csv_reader:
# #         second_number = row[3]
# #         print(second_number)



# import time
# from ping3 import ping


# # Set the target website
# website = 'live.bilibili.com'

# # Initialize lists to store latency and jitter values
# latencies = []
# jitters = []

# # Measure latency over a number of pings
# num_pings = 100
# previous_latency = None

# for i in range(num_pings):
#     print(i)
#     latency = ping(website)
    
#     if latency is not None:
#         latencies.append(latency)
        
#         # Calculate jitter as the absolute difference between current and previous latency
#         if previous_latency is not None:
#             jitter = abs(latency - previous_latency)
#             jitters.append(jitter)
#         previous_latency = latency
#     else:
#         latencies.append(float('nan'))  # Handle cases where ping fails
#         jitters.append(float('nan'))

#     time.sleep(1)  # Wait a bit between pings to simulate real-world conditions

# # Create a time axis for plotting
# time_axis = list(range(len(latencies)))

# # Plotting latency
# plt.figure(figsize=(14, 7))

# plt.subplot(2, 1, 1)
# plt.plot(time_axis, latencies, marker='o', linestyle='-', color='b')
# plt.title('Latency Over Time')
# plt.ylabel('Latency (seconds)')
# plt.grid(True)

# # Plotting jitter
# plt.subplot(2, 1, 2)
# plt.plot(time_axis[1:], jitters, marker='o', linestyle='-', color='r')
# plt.title('Jitter Over Time')
# plt.xlabel('Ping Attempt')
# plt.ylabel('Jitter (seconds)')
# plt.grid(True)

# # Display the plots
# plt.tight_layout()
# plt.show()

import time
from ping3 import ping
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Set the target website
website = 'cn-jsyz-ct-03-70.bilivideo.com'
router_ip = '192.168.1.1'

# Initialize lists to store latency and jitter values
latencies = []
jitters = []
router_latencies = []

# Set the number of points to display in the live plot
display_points = 1000

# Create a figure and axis for plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Live Latency and Jitter Tester')

# Initialize plots for latency and jitter
latency_line, = ax1.plot([], [], 'b-o', label='Latency',  linestyle='-', marker='')
jitter_line, = ax2.plot([], [], 'r-o', label='Jitter',  linestyle='-', marker='')

# Function to initialize the plot
def init():
    ax1.set_xlim(0, display_points)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel('Latency (s)')
    ax1.grid(True)
    ax1.legend()

    ax2.set_xlim(0, display_points)
    ax2.set_ylim(0, 0.2)
    ax2.set_xlabel('Ping Attempt')
    ax2.set_ylabel('Jitter (s)')
    ax2.grid(True)
    ax2.legend()

    return latency_line, jitter_line

# Function to update the plot
def update(frame):
    latency = ping(website)
    
    if latency is not None:
        latencies.append(latency)
        
        if len(latencies) > 1:
            jitter = abs(latency - latencies[-2])
            jitters.append(jitter)
        else:
            jitters.append(0)  # No jitter for the first point
    else:
        latencies.append(np.nan)
        jitters.append(np.nan)

    # Keep only the last `display_points` number of data points
    latencies_to_display = latencies[-display_points:]
    jitters_to_display = jitters[-display_points:]

    latency_line.set_data(range(len(latencies_to_display)), latencies_to_display)
    jitter_line.set_data(range(len(jitters_to_display)), jitters_to_display)

    ax1.set_ylim(0, max(latencies_to_display) * 1.2 if latencies_to_display else 1)
    ax2.set_ylim(0, max(jitters_to_display) * 1.2 if jitters_to_display else 0.2)

    return latency_line, jitter_line

# Create an animation that calls the `update` function every second
ani = FuncAnimation(fig, update, init_func=init, interval=50, blit=True)

# Display the live plot
plt.show()
