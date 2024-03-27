
from multiprocessing import Process, Manager
import logging
import subprocess
import time

from coopy.utils import Info, Scripter, Detector
from coopy.queue_manager import QueueManager

class ExecutionManager:
    def __init__(self, info: Info, scripter: Scripter, detector: Detector):
        
        """Initialize the ExecutionManager with info, a scripter instance, and a queue manager."""
        self.operation_list = info.operation_list
        self.update_frequency = info.update_frequency
        self.op_max_parallel = info.op_max_parallel
        self.cfg_sort_func = info.cfg_sort_func
        self.scripter = scripter
        self.queue_manager = QueueManager(info, detector)

        # Initialize multiprocessing manager and shared signal dictionary
        self.mp_manager = Manager()
        self.signal_dict = self.mp_manager.dict()

        self.processes = {}
        self.total_jobs = len(self.queue_manager.config_list)

    def execution_frame(self, op, cfg, slot):
        """Runs a single operation for a given configuration."""
        logging.info(f"Operation {op} for configuration {cfg} started on slot {slot}.")
        self.signal_dict[(op, cfg)] = ('RUNNING', 0, '')
        script = self.scripter.script(op, cfg, slot)
        result = subprocess.run(script, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            self.signal_dict[(op, cfg)] = ('SUCCESS', 0, result.stderr)
        else:
            self.signal_dict[(op, cfg)] = ('ERROR', result.returncode, result.stderr)
    
    def execute(self):
        while self.queue_manager.config_list:

            for op in self.operation_list:
                running_slots, available_slots = self.queue_manager.check_slots(op)
                
                if len(running_slots) > 0:
                    for slot, cfg in running_slots.items():
                        status, returncode, stderr = self.signal_dict[(op, cfg)]
                        if status != 'RUNNING':
                            self.queue_manager.update_termination(op, cfg, returncode, stderr)
                            available_slots.append(slot)

                tmp_queue = self.queue_manager.check_queue(op)
                tmp_queue = self.cfg_sort_func(tmp_queue)
                if len(available_slots) == 0 or len(tmp_queue) == 0:
                    continue
   
                for slot in available_slots:
                    if tmp_queue:
                        cfg = tmp_queue.pop(0)
                        p = Process(target=self.execution_frame, args=(op, cfg, slot))
                        p.start()
                        self.processes[(op,slot)] = (p, cfg)
                        self.queue_manager.update_execution(op, cfg, slot)
                        time.sleep(0.1)
                    else:
                        continue
            
            self.queue_manager.cleanup_completed_configs()
            logging.info("")
            logging.info("=="*40)
            logging.info("Checking the status of the operations...")
            logging.info("")
            time.sleep(self.update_frequency)

    # Summary of the execution
    def summary(self):
        logging.info("Execution Summary:")
        logging.info(f"Total jobs: {self.total_jobs}")
        logging.info(f"Completed jobs: {len(self.queue_manager.completed_list)}")
        logging.info("Errored jobs:")
        for cfg, errors in self.queue_manager.errored_log_dict.items():
            logging.info(f"    Configuration {cfg} - Errors: {errors}")
        logging.info(f"Remaining jobs: {len(self.queue_manager.config_list)}")
    
