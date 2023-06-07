import matplotlib.pyplot as plt
import numpy

# includes a lot of parsing
def plot(data):
    hrv_datetime = {}
    hrv_timestamps = []
    hrv_datapoints = []
    for row in data:
        print(row)
        date = row[0].split(" ")[0]
        time = row[0].split(" ")[1]
        hrv_datetime['year'] = int(date.split("-")[0])
        hrv_datetime['month'] = int(date.split("-")[1])
        hrv_datetime['day'] = int(date.split("-")[2])
        hrv_datetime['hour'] = int(time.split(":")[0])
        hrv_datetime['minute'] = int(time.split(":")[1])
        print(hrv_datetime['month'])
        print(hrv_datetime['day'])
        print(hrv_datetime['hour'])
        hrv_timestamps.append(hrv_datetime['day'])
        hrv_datapoints.append(int(row[1]))

    plt.plot(hrv_datapoints)
    plt.xlabel('Time')
    plt.ylabel('Value (unit)')
    plt.savefig('data_plot.png')
