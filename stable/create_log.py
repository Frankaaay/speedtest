import matplotlib.pyplot as plt
import csv

# with open('your_file.csv', mode='r') as file:
#     csv_reader = csv.reader(file)
#     for row in csv_reader:
#         second_number = row[3]
#         print(second_number)



import time
from ping3 import ping


# Set the target website
website = 'live.bilibili.com'

# Initialize lists to store latency and jitter values
latencies = []
jitters = []

# Measure latency over a number of pings
num_pings = 100
previous_latency = None

for i in range(num_pings):
    print(i)
    latency = ping(website)
    
    if latency is not None:
        latencies.append(latency)
        
        # Calculate jitter as the absolute difference between current and previous latency
        if previous_latency is not None:
            jitter = abs(latency - previous_latency)
            jitters.append(jitter)
        previous_latency = latency
    else:
        latencies.append(float('nan'))  # Handle cases where ping fails
        jitters.append(float('nan'))

    time.sleep(1)  # Wait a bit between pings to simulate real-world conditions

# Create a time axis for plotting
time_axis = list(range(len(latencies)))

# Plotting latency
plt.figure(figsize=(14, 7))

plt.subplot(2, 1, 1)
plt.plot(time_axis, latencies, marker='o', linestyle='-', color='b')
plt.title('Latency Over Time')
plt.ylabel('Latency (seconds)')
plt.grid(True)

# Plotting jitter
plt.subplot(2, 1, 2)
plt.plot(time_axis[1:], jitters, marker='o', linestyle='-', color='r')
plt.title('Jitter Over Time')
plt.xlabel('Ping Attempt')
plt.ylabel('Jitter (seconds)')
plt.grid(True)

# Display the plots
plt.tight_layout()
plt.show()