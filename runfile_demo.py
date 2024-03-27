"""
This is corresponding to actual operations
Generates done_{config}_{operation}.txt files in the demo folder, to check the completion of the task
"""
import argparse, time, os, random

parser = argparse.ArgumentParser(description='Process options')
parser.add_argument('--op', type=str, required=True, choices=['a', 'b', 'c'], help='DEMO TASK: Option must be one of a, b, c')
parser.add_argument('--device_id', type=int, required=True, help='DEMO TASK: This is (almost) dummy argument for testing concurrency')
parser.add_argument('--cfg', type=int, required=True, help='DEMO TASK: Number, must be an integer')
args = parser.parse_args()

print(f'Operation: {args.op}, Configuration: {args.cfg}')

if not os.path.exists('./demo'):
    os.makedirs('demo')

sleep_time = {
    'a': 5  + random.random() * 5,
    'b': 5  + random.random() * 5,
    'c': 5  + random.random() * 5
}[args.op]

RAISE_ERROR_PROB = {
    'a': 0.3,
    'b': 0.5,
    'c': 0.7
}

time.sleep(sleep_time)
if random.random() < RAISE_ERROR_PROB[args.op]:
    raise Exception(f'Error raised for operation {args.op} and configuration {args.cfg}')
with open(f'./demo/done_{args.cfg}_{args.op}.txt', 'w') as f:
    f.write('Completed')
time.sleep(1)


