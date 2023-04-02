import os
import csv
from datetime import datetime

def generate_report(n_threads, array_size, start_time, end_time):
    info = {
        "n_threads": n_threads,
        "array_size": array_size,
        "time_elapsed": (end_time - start_time) * 1000, # in milliseconds
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    write_header = not os.path.exists(r'report.csv')

    with open(r'report.csv', 'a', newline='') as csvfile:
        fieldnames = list(info.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        if write_header: writer.writeheader()
        writer.writerow(info)