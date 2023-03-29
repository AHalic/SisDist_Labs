import random
from threading import Thread
import sys


class CustomThread(Thread):
    # constructor
    def __init__(self, func, params):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.value = None
        self.func = func
        self.params = params
 
    # function executed in a new thread
    def run(self):
        # store data in an instance variable
        self.value = self.func(self.params)

def create_array(size):
    """
    Creates a random array of size
    """
    array = random.sample(range(50*size), size)
    return array


def divide_array(n_threads, big_array):
    """
    Divides array, copying arrays. Obs.: see if copy() affects time
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

def merge_arrays(array_a, array_b):
    """
    Merges arryas
    """

    y , y = 0, 0
    results = list()
    
    size_a, size_b = len(array_a), len(array_b)
    size = len(array_a) if len(array_b) < len(array_a) else len(array_b)        

    while x != size_a and y != size_b:
        if array_a[x] <= array_b[y]:
            new_el = array_a[x] 
            x+=1
            results.append[new_el] 
        else: 
            new_el = array_b[y]
            y+=1
            results.append[new_el] 
    if x == size_a: 
        results.append(array_b[y:].copy())
        
    elif y == size_b:
        results.append(array_a[x:].copy())
    
        
def sort_array(array):
    return sorted(array)

def divide_threads(arrays):
    n = len(arrays)
    rest = n%2
    # se tem resto, entao faz pop do array de arrays
    # e ja adiciona o array no array final
    # roda sempre como numero par de arrays
    # if rest 

    n_threads = n//2

    threads = []
    for i in range(0, n_threads + 1, 2): 
        thread = CustomThread(merge_arrays, arrays[i:i+2])
        threads.append(thread)
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    pass



"""
Ref:
https://docs.python.org/3/library/threading.html
https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.ThreadPool +  https://stackoverflow.com/questions/69005467/how-to-get-return-values-of-multi-threads-once-one-of-them-is-finished
https://superfastpython.com/thread-return-values/#Need_to_Return_Values_From_a_Thread
"""

if __name__ == "__main__":
    n_threads = sys.argv[1]
    array_size = sys.argv[2]

    array = create_array(array_size)
    arrays = divide_array(n_threads, array)


    # Sort arrays
    threads = []
    for i in range(n_threads):
        thread = CustomThread(sort_array, arrays[i])
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()



    while n_threads > 1:
        if n_threads % 2: n_threads +=1 
        n_threads = n_threads // 2


"""
from multiprocessing.pool import ThreadPool
with ThreadPool(n_threads) as pool:
    results = pool.starmap(sort_array, arrays)
"""