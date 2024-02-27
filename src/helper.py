import time # timing tests
from pathlib import Path
import json
import re

# helper function to test timings
def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f"Function {func.__name__} took {run_time:.6f} seconds to run.")
        return result
    return wrapper

def init_temp_storage(temp_path):
    temp_path = Path(temp_path)
    temp_path.mkdir(parents=True, exist_ok=True)

    return temp_path

def read_file_as_str(file_path):
    with open(file_path, 'r') as f:
        data = f.read().replace('\n', '')

    return data

def read_json(json_path):
    with open(json_path, "r") as f:
        js = json.load(f)

    return js

def read_prompts_json(json_path):
    prompts = read_json(json_path)
    for key, val in prompts.items():
        prompts[key] = val.replace("\n", "")

    return prompts


def get_first_number(input_string):
    # Use regular expression to find the first occurrence of a number in the string
    match = re.search(r'\b\d+\b', input_string)
    
    if match:
        # Extract and return the matched number as an integer
        return int(match.group())
    else:
        # Return None if no number is found in the input string
        return None