import time
from ping3 import ping
import matplotlib.pyplot as plt
import csv

# Set the target website and router IP
router_ip = '192.168.1.1'
website = 'cn-jsyz-ct-03-70.bilivideo.com'

# Initialize lists to store latency and jitter values
router_latencies = []
website_latencies = []
router_jitters = []
website_jitters = []

# Number of pings
num_pings = 10
previous_router_latency = None
previous_website_latency = None

# Open a CSV file to write the data
with open('latency_jitter_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(['Router Latency', 'Router Jitter', 'Website Latency', 'Website Jitter'])
    
    for i in range(num_pings):
        print(i)
        # Measure latency to the router
        router_latency = ping(router_ip)
        
        # Measure latency to the website
        website_latency = ping(website)
        
        # Calculate jitter for the router and website
        router_jitter = abs(router_latency - previous_router_latency) if previous_router_latency is not None else 0
        website_jitter = abs(website_latency - previous_website_latency) if previous_website_latency is not None else 0
        
        # Append the latency and jitter values to the lists
        router_latencies.append(router_latency)
        website_latencies.append(website_latency)
        router_jitters.append(router_jitter)
        website_jitters.append(website_jitter)
        
        # Write the latency and jitter values to the CSV file
        writer.writerow([router_latency, router_jitter, website_latency, website_jitter])
        
        # Update the previous latency values
        previous_router_latency = router_latency
        previous_website_latency = website_latency

        # Wait a second between pings to simulate real conditions
        time.sleep(0.1)

# Create a time axis for plotting
time_axis = list(range(num_pings))

# Plotting the latencies
plt.figure(figsize=(12, 6))
plt.plot(time_axis, router_latencies, 'b-', label='Router Latency')
plt.plot(time_axis, website_latencies, 'r-', label='Website Latency')

# Adding titles and labels
plt.title('Latency to Router and Website Over Time')
plt.xlabel('Ping Attempt')
plt.ylabel('Latency (seconds)')
plt.legend()
plt.grid(True)

# Display the plot
plt.show()
