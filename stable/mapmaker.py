import csv
import time
import datetime
from ping3 import ping
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button

# Set the target website
website = 'cn-jsyz-ct-03-70.bilivideo.com'
router_ip = '192.168.1.1'

# Set the number of points to display in the live plot
display_points = 100
duration = 20

# Create a figure and axis for plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Live Latency and Jitter Tester')

# Initialize plots for latency and jitter
latency_line, = ax1.plot([], [], 'b-o', label='Latency', linestyle='-', marker='')
jitter_line, = ax2.plot([], [], 'r-o', label='Jitter', linestyle='-', marker='')

# Function to initialize the plot
def init():
 
    ax1.set_xlim(0, display_points)
    #ax1.set_ylim(0, 1)
    ax1.set_ylabel('Latency (s)')
    ax1.grid(True)
    ax1.legend()

    ax2.set_xlim(0, display_points)
    #ax2.set_ylim(0, 0.2)
    ax2.set_xlabel('Ping Attempt')
    ax2.set_ylabel('Jitter (s)')
    ax2.grid(True)
    ax2.legend()

    return latency_line, jitter_line

class Data:
    def __init__(self) -> None:
        #track how many lines of data
        self.tracker = 0

        self.file = open('lag_time.csv', mode='w', newline='')
    
    def mark_line(self):
        self.file.writerow([self.tracker, datetime.datetime.now().strftime("%H:%M:%S")])

class Draw():
    def __init__(self, writer_data, f) -> None:
        # super().__init__()
        self.writer_data = writer_data
        self.writer_lag = f

        # Initialize lists to store latency and jitter values
        self.latencies = []
        self.jitters = []
        self.latency = 0
        self.jitter = 0
        
        self.tracker = 0

    # Function to update the plot
    def update(self, frame):
        self.tracker += 1
        self.latency = ping(website)
        
        if self.latency is not None:
            self.latencies.append(self.latency)
            print(round(self.jitter, 3))
            if self.latency >= 0.04:
                self.writer_lag.writerow([self.tracker, datetime.datetime.now().strftime("%H:%M:%S")])
            if len(self.latencies) > 1:
                self.jitter = abs(self.latency - self.latencies[-2])
                self.jitters.append(self.jitter)
            else:
                self.jitters.append(0)  # No jitter for the first point
        else:
            self.latencies.append(np.nan)
            self.jitters.append(np.nan)

        self.writer_data.writerow([round(self.latency, 3),round(self.jitter, 4)])

        # Keep only the last `display_points` number of data points
        latencies_to_display = self.latencies[-display_points:]
        jitters_to_display = self.jitters[-display_points:]

        latency_line.set_data(range(len(latencies_to_display)), latencies_to_display)
        jitter_line.set_data(range(len(jitters_to_display)), jitters_to_display)

        ax1.set_ylim(0, max(latencies_to_display) * 1.2 if latencies_to_display else 1)
        ax2.set_ylim(0, max(jitters_to_display) * 1.2 if jitters_to_display else 0.2)

        
        return latency_line, jitter_line



with open('latency_jitter_data.csv', mode='w', newline='') as file:
    f = open('lag_time.csv', mode='w', newline='')
    writer = csv.writer(file)  
    f = csv.writer(f)
    draw = Draw(writer, f)
    
    # Create an animation that calls the `update` function every second
    ani = FuncAnimation(fig, draw.update, init_func=init, interval=1000, blit=True)

    # # Add a stop button
    # ax_button = plt.axes([0.8, 0.02, 0.1, 0.04])
    # stop_button = Button(ax_button, 'Stop', color='red', hovercolor='green')
    # stop_button.on_clicked(stop)

    # Display the live plot
    plt.show()
