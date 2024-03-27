from abc import ABC, abstractmethod
from typing import List, Callable

class Info:
    """
    This class represents the information of the task.
    self.operation_list: Operation to be executed. List of operations in the expected order of executions.
    self.config_list: Configuration to be executed.
    self.op_max_parallel: Number of operations to be executed concurrently.
    self.update_frequency: Frequency(s) of checking the completion of the task.
    self.error_tolerance: Number of errors to be tolerated before stopping the execution.
    self.cfg_sort_func: Function to sort the configuration list. Default is None (no sorting).
    """
    def __init__(self, operation_list, config_list, op_max_parallel,
                 update_frequency: int = 10, error_tolerance: int = 3,
                 cfg_sort_func: Callable[[List[str]], List[str]] = None):
        
        self.operation_list = operation_list
        self.config_list = config_list

        self.op_max_parallel = op_max_parallel

        self.update_frequency = update_frequency
        self.error_tolerance = error_tolerance

        self.cfg_sort_func = cfg_sort_func if cfg_sort_func is not None else lambda x: x

    def __str__(self):
        return f'Info({self.operation_list}, {self.op_max_parallel}, {self.config_list}, {self.update_frequency}, {self.error_tolerance})'

    def __repr__(self):
        return self.__str__()

class Scripter(ABC):
    """
    This class represents a task that can be executed with scripts.
    self.operation_list: List ordered in the expected order of executions.
    script module returns the script to be executed.
    """
    @abstractmethod
    def script(self, operation, config, slot):
        """
        if operation == 'a':
             return f'python3 a_process.py --config {config}'
        ...
        ...
        else:
            raise NotImplementedError('This operation is not implemented')
        """
        pass

class Detector(ABC):
    """
    This class detects the completed execution of tasks.
    self.config_list: List of configurations to be executed.
    detect module returns True if the task is completed, False otherwise.
    """
    @abstractmethod
    def detect(self, operation, config):
        """
        if operation == 'a':
            return os.path.exists(f'done_{config}_a.txt')
        ...
        ...
        else:
            raise NotImplementedError('This operation is not implemented')
        """
        pass