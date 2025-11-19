#!/usr/bin/env python3
import glob
import subprocess
import concurrent.futures
import sys
import os

MAX_WORKERS = os.cpu_count() or 1

errors = []

def run_translate(directory):
    if errors:
        return
    command = ["./translate.sh", directory]
    subprocess.run(
        command, 
        check=True
    )

directories = sorted(glob.glob("Public-Tests/*/*/"))

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_dir = {executor.submit(run_translate, d): d for d in directories}
    
    for future in concurrent.futures.as_completed(future_to_dir):
        try:
            future.result()
        except Exception as e:
            errors.append(e)

if errors:
    for e in errors:
        print(e)
    sys.exit(1)
