# Managing Chain of Operations with Python

## Repository Purpose
This repository enhances the execution of interconnected tasks requiring a specific operational sequence. It addresses the inefficiency in traditional methods like sequential script execution in a single file, which fails to optimize computational resources across tasks with varying execution times and costs.

## Approach
We offer a queue management system for handling stages of linked processes. Each stage has its queue, automatically updated every N seconds to reflect task completions. Completed tasks move to the next stage's queue, facilitating an efficient flow of operations and optimizing resource use by reducing idle time.

## Looking for Advanced Tools?
While Apache Airflow is an option, our direct queue management for each node offers a simpler, more intuitive solution that independently optimizes each process flow. Benefits include:

- **Resource Utilization Optimization**: Independent queues for each stage reduce idle time, enhancing computational efficiency.
- **Flexible Task Management**: Easier adjustment of task priorities, dynamic resource allocation, and quick retries.
- **Simplicity and Intuitiveness**: I think it is designed to be straightforward and user-friendly.

## To Start
Please try to run `python task_demo.py` (working on features).