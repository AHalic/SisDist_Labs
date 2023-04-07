import argparse
import time

from custom_thread import CustomThread
from arrays import create_array, divide_array, sort_arrays_threads, merge_arrays_threads, sort_arrays_processes, merge_arrays_processes
from report import generate_report

def parse_args() -> tuple[int, int, int, int]:
    parser = argparse.ArgumentParser(description='Merge sort with threads')
    parser.add_argument('n_threads', type=int, help='Number of threads')
    parser.add_argument('array_size', type=int, help='Size of the array')
    parser.add_argument('--use_process', action='store_true', help='Use process instead of threads')
    parser.add_argument('--sort_type', type=str, help='Type of sort (bubble, python)', default='python')
    args = parser.parse_args()    

    return args.n_threads, args.array_size, args.use_process, args.sort_type


def thread_main(n_threads, arrays, sort_type):
    # Start timer
    start_time = time.time()

    # Sort arrays using threads
    sorted_arrays = sort_arrays_threads(n_threads, arrays, sort_type)

    # Merge arrays
    while len(sorted_arrays) > 1:
        sorted_arrays = merge_arrays_threads(sorted_arrays)
    
    # Stop timer
    end_time = time.time()

    generate_report(n_threads, array_size, start_time, end_time, f"threads_{sort_type}")


def process_main(n_threads, arrays, sort_type):
    # Start timer
    start_time = time.time()

    # Sort arrays using process
    sorted_arrays = sort_arrays_processes(n_threads, arrays, sort_type)

    # Merge arrays
    while len(sorted_arrays) > 1:
        sorted_arrays = merge_arrays_processes(sorted_arrays)
    
    # Stop timer
    end_time = time.time()

    generate_report(n_threads, array_size, start_time, end_time, suffix=f"process_{sort_type}")


if __name__ == "__main__":
    # Parse arguments
    n_threads, array_size, use_process, sort_type = parse_args()

    print(f"n_threads: {n_threads}")
    print(f"array_size: {array_size}")
    print(f"use_process: {use_process}")
    print(f"sort_type: {sort_type}")

    # Create array
    array = create_array(array_size)
    # Divide array
    arrays = divide_array(n_threads, array)

    # Sort arrays using threads
    if use_process:
        process_main(n_threads, arrays, sort_type)
    else: 
        thread_main(n_threads, arrays, sort_type)