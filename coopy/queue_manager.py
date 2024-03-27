from collections import defaultdict
from copy import copy
from typing import List, Dict
import logging

from coopy.utils import Info, Detector

class QueueManager:
    def __init__(self, info: Info, detector: Detector):
        """
        Initializes the QueueManager with operational and configuration details from an Info instance,
        a Detector instance for status detection, and sets up internal tracking structures.
        """

        # Initialize lists of operations and configurations, including their count.
        self.operation_list: List[str] = info.operation_list
        self.N_ops = len(self.operation_list)  # Total number of operations
        self.config_list: List[str] = copy(info.config_list)
        self.N_cfg = len(self.config_list)  # Total number of configurations
        
        # Initialize operational parameters from the Info instance.
        self.error_tolerance: int = info.error_tolerance
        self.op_max_parallel: Dict[str, int] = info.op_max_parallel
        
        # Detector instance for checking operation status.
        self.detector: Detector = detector
        
        # Tracking dictionaries:
        # finished_dict: Tracks which operations are finished (1) or not (0) for each configuration.
        self.finished_dict = defaultdict(list)  
        # queue_dict: Indicates if operations are queued (1) or not (0) based on their execution status.
        # Operations are queued, only if it is not running or completed or waiting for previous operations.
        self.queue_dict = defaultdict(list)
        # Initializes status tracking structures and filters out already completed configurations.
        self._initialize_tracking_dicts()

        # Error tracking for each operation in every configuration.
        self.error_dict = defaultdict(lambda: [0] * self.N_ops)
        # Current running slot (-1 if not running) for each operation in every configuration.
        self.running_dict = defaultdict(lambda: [-1] * self.N_ops)
        # List of completed / errored configurations.
        self.completed_list = []
        self.errored_log_dict = {}
        # Remove completed configurations from tracking structures and the main configuration list.
        self.cleanup_completed_configs()

    def _initialize_tracking_dicts(self):
        """Initializes status dictionaries for each configuration and filters out completed configurations."""

        for cfg in self.config_list:
            """
            Sequentially define queue status for each operation.
            Not done operation is queued only if the previous operation is completed
            If the last operation is not completed, the operation is not queued anyway.
            """
            prev_op_finished = 1
            for op in self.operation_list:
                op_finished = int(self.detector.detect(op, cfg))
                self.finished_dict[cfg].append(op_finished)
                self.queue_dict[cfg].append((1 - op_finished) * prev_op_finished)
                prev_op_finished = op_finished

            self.queue_dict[cfg].append(prev_op_finished)

    def cleanup_completed_configs(self):

        # Identify configurations that have completed all operations.
        completed = [cfg for cfg, status in self.finished_dict.items() if status[-1] == 1]
        # Update the set of completed configurations.
        self.completed_list = list(set(self.completed_list + completed))

        # Identify configurations that have exceeded the error tolerance.
        errored = dict([(cfg, errors) for cfg, errors in self.error_dict.items() if max(errors) >= self.error_tolerance])
        # Update the errored configurations.
        self.errored_log_dict = {**self.errored_log_dict, **errored}

        # Remove completed configurations from tracking structures and the main configuration list.
        for cfg in completed + list(errored.keys()):
            self.pop_config(cfg)

    def pop_config(self, cfg):
        self.finished_dict.pop(cfg, None)
        self.queue_dict.pop(cfg, None)
        self.error_dict.pop(cfg, None)
        self.running_dict.pop(cfg, None)
        try:
            self.config_list.remove(cfg)
        except ValueError:
            pass

    def update_execution(self, op, cfg, slot):
        """Updates the status of a given operation and configuration based on the slot."""
        i_op = self.operation_list.index(op)
        assert self.queue_dict[cfg][i_op] == 1, "Operation must be queued before execution."
        assert self.running_dict[cfg][i_op] == -1, "Operation must not be running."

        self.queue_dict[cfg][i_op] = 0
        self.running_dict[cfg][i_op] = slot

    def update_termination(self, op, cfg, exit_code, stderr):
        """Updates the status of a given operation and configuration based on the exit code."""
        i_op = self.operation_list.index(op)
        # Reset the slot number as not running
        self.running_dict[cfg][i_op] = -1

        task_str = f"Operation {op} on Configuration {cfg}"
        if exit_code == 0:
            self._handle_success(i_op, cfg, task_str)
        else:
            self._handle_error(i_op, cfg, exit_code, stderr, task_str)

    def _handle_success(self, i_op, cfg, task_str):
        """Handles successful operation completion."""
        self.finished_dict[cfg][i_op] = 1
        self.queue_dict[cfg][i_op + 1] = 1
        logging.info(f"{task_str} completed successfully.")

    def _handle_error(self, i_op, cfg, exit_code, stderr, task_str):
        """Handles operation failure based on exit code and error tolerance."""
        self.error_dict[cfg][i_op] += 1
        logging.error(f"{task_str} failed with exit code: {exit_code} and stderr:\n\n {stderr}")
        if self.error_dict[cfg][i_op] >= self.error_tolerance:
            logging.info(f"{task_str} exceeded the error tolerance. Removing from the queue.\n")
        else:
            self.queue_dict[cfg][i_op] = 1  # Retry
            logging.info(f"{task_str} will be retried.\n")

    def check_queue(self, op):
        """Returns a list of configurations queued for a given operation."""

        i_op = self.operation_list.index(op)
        return [cfg for cfg, status in self.queue_dict.items()
                if status[i_op] == 1 and self.error_dict[cfg][i_op] < self.error_tolerance]

    def check_slots(self, op):
        """Returns the progress of a given operation across all configurations."""
        i_op = self.operation_list.index(op)

        slots = dict([(self.running_dict[cfg][i_op], cfg) for cfg in self.config_list if self.running_dict[cfg][i_op] != -1])
        assert len(set(slots.keys())) == len(slots.keys()), "Duplicate slots detected."

        available_slots = list(set(range(self.op_max_parallel[i_op])) - set(slots.keys()))

        return slots, available_slots
