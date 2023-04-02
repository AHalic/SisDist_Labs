import os
import csv
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

def generate_report(n_threads: int, array_size: int, start_time: float, end_time: float) -> None:
    """
    Generates a report in CSV format
    @param n_threads: Number of threads
    @param array_size: Size of the array
    @param start_time: Start time of the execution
    @param end_time: End time of the execution
    return: None
    """
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

def scatter_plot_report() -> None:
    """
    Plots the report
    return: None

    obs.: currently, it does not save the plot
    """

    df = pd.read_csv(r'report.csv', delimiter=';')
    df.plot(x='n_threads', y='time_elapsed', kind='scatter')
    plt.show()	