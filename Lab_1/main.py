import argparse
import time

from custom_thread import CustomThread
from arrays import create_array, divide_array, sort_arrays_threads, merge_arrays_threads
from report import generate_report

def parse_args() -> tuple[int, int]:
    parser = argparse.ArgumentParser(description='Merge sort with threads')
    parser.add_argument('n_threads', type=int, help='Number of threads')
    parser.add_argument('array_size', type=int, help='Size of the array')
    args = parser.parse_args()    

    return args.n_threads, args.array_size

if __name__ == "__main__":
    # Parse arguments
    n_threads, array_size = parse_args()

    # Create array
    array = create_array(array_size)
    # Divide array
    arrays = divide_array(n_threads, array)

    # Start timer
    start_time = time.time()


    # Sort arrays using threads
    sorted_arrays = sort_arrays_threads(n_threads, arrays)

    # Merge arrays
    merged_arrays = merge_arrays_threads(sorted_arrays)
    while len(merged_arrays) > 1:
        merged_arrays = merge_arrays_threads(merged_arrays)

    # Stop timer
    end_time = time.time()

    generate_report(n_threads, array_size, start_time, end_time)