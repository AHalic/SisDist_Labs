from threading import Thread

class CustomThread(Thread):
    """
    Custom thread class that permits to get the return value of a function.
    Based on https://superfastpython.com/thread-return-values/#Need_to_Return_Values_From_a_Thread
    """

    def __init__(self, func, params):
        """
        Constructor
        @param func: function to be executed in a new thread
        @param params: parameters of the function
        """

        # execute the base constructor
        Thread.__init__(self)

        # set a default value
        self.value = None
        self.func = func
        self.params = params
 
    def run(self):
        """	
        Run the thread, saving the return value in an instance variable
        """
        # store data in an instance variable
        self.value = self.func(self.params)