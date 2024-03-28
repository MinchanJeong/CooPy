"""
This is a simple example of a task script that can be used to test the execution manager.
This script is used to test the execution manager with a simple task that generates 
    done_{config}_{operation}.txt files in the debug folder to check the completion of the task.
"""
import os, logging
from coopy.logger import default_logger
from coopy.utils import Info, Scripter, Detector
from coopy.execution_manager import ExecutionManager

# Logger configuration
logger = logging.getLogger()
default_logger(logger)

# Task configuration
# Operation list: List of operations to be executed. Ordered in the expected order of executions.
operation_list  = ['a', 'b', 'c']
# Maximum number of operations to be executed in parallel. 
# The slot (index) in `range(op_max_parallel[operation])` will be used to identify the concurrent operations.
op_max_parallel = [5, 3, 2]
# Configuration list: List of configurations to be executed.
config_list     = ['1', '10', '2', '9', '3', '8', '4', '7', '5', '6']
# Update frequency: Frequency(s) of checking the completion of the task.
update_frequency = 10

# Define Scripter and Detector classes / functions
class DemoScripter(Scripter):

    def script(self, operation, config, slot):
        if operation == 'a':
            return f'python3 runfile_demo.py --op a --cfg {config} --device_id {slot}'
        elif operation == 'b':
            return f'python3 runfile_demo.py --op b --cfg {config} --device_id {slot}'
        elif operation == 'c':
            return f'python3 runfile_demo.py --op c --cfg {config} --device_id {slot}'
        else:
            raise NotImplementedError('This operation is not implemented')

class DemoDetector(Detector):

    def detect(self, operation, config):
        return os.path.exists(f'./debug/done_{config}_{operation}.txt')

# Execution
if __name__ == '__main__':
    info = Info(operation_list, config_list,  op_max_parallel, 
                update_frequency, error_tolerance=3,
                cfg_sort_func=lambda x: sorted(x, reverse=True, key=int))
    scripter = DemoScripter()
    detector = DemoDetector()

    manager = ExecutionManager(info, scripter, detector)
    manager.execute()
    manager.summary()