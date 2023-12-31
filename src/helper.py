import time # timing tests
from pathlib import Path
import json

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

def read_prompts_json(json_path):
    with open(json_path, "r") as f:
        prompts = json.load(f)
    
    for key, val in prompts.items():
        prompts[key] = val.replace("\n", "")

    return prompts