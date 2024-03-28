"""
This is corresponding to actual operations
Generates done_{config}_{operation}.txt files in the demo folder, to check the completion of the task
"""
import argparse, time, os, random

EXECUTION_TIME = {
    'a': 5  + random.random() * 5,
    'b': 5  + random.random() * 5,
    'c': 5  + random.random() * 5
}

RAISE_ERROR_PROB = {
    'a': 0.3,
    'b': 0.5,
    'c': 0.7
}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process options')
    parser.add_argument('--op', type=str, required=True, choices=['a', 'b', 'c'], help='DEMO TASK: Option must be one of a, b, c')
    parser.add_argument('--device_id', type=int, required=True, help='DEMO TASK: This is (almost) dummy argument for testing concurrency')
    parser.add_argument('--cfg', type=int, required=True, help='DEMO TASK: Number, must be an integer')
    args = parser.parse_args()

    # Extract the operation and configuration from the arguments
    op, cfg = args.op, args.cfg
    
    # Simulate the execution of the operation
    execution_time = EXECUTION_TIME[op]
    time.sleep(execution_time)

    # Simulate the error raised during the operation
    raise_error_prob = RAISE_ERROR_PROB[op]
    if random.random() < raise_error_prob:
        raise Exception(f'Error raised for operation {op} and configuration {cfg}')
    
    # Write a file to indicate the completion of the task
    if not os.path.exists('./demo'):
        os.makedirs('demo')
    with open(f'./demo/done_{cfg}_{op}.txt', 'w') as f:
        f.write('Completed')
    time.sleep(1.0)



