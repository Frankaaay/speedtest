import pandas as pd
from datetime import timedelta

# Load the CSV file into a DataFrame
df = pd.read_csv('log\speed\测试\speed.csv')

# Define the format of your time column (if it's in MM-DD HH:MM:SS format)
df['time'] = pd.to_datetime(df['time'], format='%m-%d %H:%M:%S', errors='coerce')

# Check if there were any parsing errors
if df['time'].isnull().any():
    print("Warning: Some rows could not be converted to datetime. Check the input format.")

# Add 1 minute to each time entry
df['time'] = df['time'] + timedelta(minutes=1)

# Save the modified DataFrame back to the CSV
df.to_csv('log\speed\测试\speed.csv', index=False)

print("Time column updated successfully!")
