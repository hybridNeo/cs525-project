#!/bin/bash
import os
import sys
import subprocess
import time
def get_result():
    with open('temp') as f:
            content = f.readlines()
    # content = [x.strip() for x in content]
    print(content)
    for i in content:
        if "[Querier] Test Completed :" in i:
            print(i)
            sb = i.split(":")
            time = float(sb[-1])
            print(time)
            return time
    return 0.0

def run_simple(n):
    for i in range(n):
        os.system("python3.7 test_sim.py simple ")


def run_rr(n):
    for i in range(n):
        os.system("python3.7 test_sim.py rr ")


def run_dynamic(n):
    for i in range(n):
        os.system("python3.7 test_sim.py dynamic")


def run_all(n):
    run_simple(n)
    run_dynamic(n)
    run_rr(n)


def clean():
    time.sleep(3)
    os.system("rm astdout bstdout req_* server_* resp_*")
    os.system("sudo killall python3.7")

def main():
    if len(sys.argv) < 3:
        print("enter command and number of runs")
    else:
        cmd = sys.argv[1]
        num_runs = int(sys.argv[2])
        if(cmd) == 'simple':
            run_simple(num_runs)
        elif(cmd == 'rr'):
            run_rr(num_runs)
        elif(cmd == 'dynamic'):
            run_dynamic(num_runs)
        elif(cmd == 'clean'):
            clean()
        clean()
if __name__ == '__main__':
    main()


