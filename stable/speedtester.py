import time
from ping3 import ping
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Set the target website and router IP
website = 'cn-jsyz-ct-03-70.bilivideo.com'
router_ip = '192.168.1.1'

# Initialize lists to store latency values
router_latencies = []
website_latencies = []

# Set the number of points to display in the live plot
display_points = 1000

# Create a figure and axis for plotting
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Live Latency to Router and Website')

# Initialize plots for latency
router_line, = ax.plot([], [], 'b-', label='Router Latency')
website_line, = ax.plot([], [], 'r-', label='Website Latency')

# Function to initialize the plot
def init():
    ax.set_xlim(0, display_points)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Ping Attempt')
    ax.set_ylabel('Latency (s)')
    ax.grid(True)
    ax.legend()
    return router_line, website_line

# Function to update the plot
def update(frame):
    router_latency = ping(router_ip)
    website_latency = ping(website)
    
    if router_latency is not None:
        router_latencies.append(router_latency)
    else:
        router_latencies.append(np.nan)

    if website_latency is not None:
        website_latencies.append(website_latency)
    else:
        website_latencies.append(np.nan)

    # Keep only the last `display_points` number of data points
    router_latencies_to_display = router_latencies[-display_points:]
    website_latencies_to_display = website_latencies[-display_points:]

    router_line.set_data(range(len(router_latencies_to_display)), router_latencies_to_display)
    website_line.set_data(range(len(website_latencies_to_display)), website_latencies_to_display)

    ax.set_ylim(0, max(max(router_latencies_to_display, default=0), max(website_latencies_to_display, default=0)) * 1.2)

    return router_line, website_line

# Create an animation that calls the `update` function every 1000 ms (1 second)
ani = FuncAnimation(fig, update, init_func=init, interval=100, blit=True)

# Display the live plot
plt.show()
