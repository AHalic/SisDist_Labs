import random 
from custom_thread import CustomThread

def create_array(size):
    """
    Creates a random array of size
    @param size: size of array
    return: array of size
    """
    array = random.sample(range(50*size), size)
    return array


def divide_array(n_threads, big_array):
    """
    Divides array, copying arrays. Obs.: see if copy() affects time
    @param n_threads: number of threads
    @param big_array: array to be divided
    return: list of arrays
    """
    size_floor = len(big_array) // n_threads
    arrays = list()
    
    for i in range(0, n_threads):
        if i < n_threads -1:
            new_array = big_array[size_floor*i: size_floor*(i+1)].copy()
            arrays.append(new_array)
        else:
            arrays.append(big_array[size_floor * i:].copy()) 

    return arrays


def merge_arrays(arrays):
    """
    Merges arrays in a sorted way
    @param arrays: list of arrays to be merged
    return: merged array
    """
    (array_a, array_b) = arrays

    x , y = 0, 0
    results = []
    
    size_a, size_b = len(array_a), len(array_b)    

    while x != size_a and y != size_b:
        if array_a[x] <= array_b[y]:
            new_el = array_a[x] 
            x+=1
            results.append(new_el)
        else: 
            new_el = array_b[y]
            y+=1
            results.append(new_el)

    if x == size_a: 
        results.extend(array_b[y:])
        
    elif y == size_b:
        results.extend(array_a[x:])

    return results
    
        
def sort_array(array):
    """
    Sorts array function for CustomThread
    @param array: array to be sorted
    return: sorted array
    """
    return sorted(array)

def sort_arrays_threads(n_threads, arrays):
    """
    Sorts arrays using threads
    @param arrays: list of arrays to be sorted
    @param n_threads: number of threads
    return: list of sorted arrays
    """
    
    threads = []
    for i in range(n_threads):
        thread = CustomThread(sort_array, arrays[i])
        threads.append(thread)
    
    # Start sorting in threads
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Get sorted arrays from threads
    return [t.value for t in threads]


def merge_arrays_threads(arrays):
    """
    Divide threads in pairs and merge them until there is only one array, using threads
    @param arrays: list of arrays to be merged
    return: list with only one array
    """

    n = len(arrays)
    last = None

    # If odd, remove last array
    if n % 2:
        last = arrays.pop()

    # Create threads, with merge function for 2 arrays at a time
    threads = []
    for i in range(0, len(arrays), 2): 
        threads.append(CustomThread(merge_arrays, arrays[i:i+2]))

    # Start merging threads
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
    # Get merged arrays from threads
    merged_arrays = [t.value for t in threads]

    # Add last array if odd
    if last:
        merged_arrays.append(last)

    return merged_arrays