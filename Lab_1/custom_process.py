from multiprocessing import Process

class CustomProcess(Process):
    """
    Custom Process class that permits to get the return value of a function.
    """

    def __init__(self, queue, func: callable, params: list, ) -> None:
        """
        Constructor
        @param func: function to be executed in a new Process
        @param params: parameters of the function
        """

        # execute the base constructor
        Process.__init__(self)

        # set a default value
        self.queue = queue
        self.func = func
        self.params = params
 
    def run(self) -> None:
        """	
        Run the Process, saving the return value in an instance variable
        """
        # store data in an instance variable


        # print('func', self.func.__name__)
        # print('params', self.params)
        
        ret = self.func(self.params)
        # print("ret", ret)
        # print("\n")
        self.queue.put(ret)