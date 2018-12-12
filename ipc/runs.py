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

def run_simple(n, arg = ' '):
    for i in range(n):
        os.system("python3.7 test_sim.py simple " + arg)


def run_rr(n, arg = ' '):
    for i in range(n):
        os.system("python3.7 test_sim.py rr "  + arg )


def run_dynamic(n, arg = ''):
    for i in range(n):
        os.system("python3.7 test_sim.py dynamic" + arg)


def run_all(n, arg=''):
    run_simple(n, arg)
    run_dynamic(n, arg)
    run_rr(n, arg)


def clean():
    time.sleep(3)
    os.system("rm astdout bstdout req_* server_* resp_*")
    os.system("sudo killall python3.7")

def main():
    if len(sys.argv) < 3:
        print("enter command and number of runs")
    arg = ''
    if len(sys.argv) == 4:
        cmd = sys.argv[1]
        num_runs = int(sys.argv[2])
        arg = sys.argv[3]
        if(cmd) == 'simple':
            run_simple(num_runs,arg)
        elif(cmd == 'rr'):
            run_rr(num_runs, arg)
        elif(cmd == 'dynamic'):
            run_dynamic(num_runs, arg)
        elif(cmd == 'all'):
            run_all(num_runs, arg)
        elif(cmd == 'clean'):
            clean()
    else:
        cmd = sys.argv[1]
        num_runs = int(sys.argv[2])
        if(cmd) == 'simple':
            run_simple(num_runs,arg)
        elif(cmd == 'rr'):
            run_rr(num_runs, arg)
        elif(cmd == 'dynamic'):
            run_dynamic(num_runs, arg)
        elif(cmd == 'all'):
            run_all(num_runs, arg)
        elif(cmd == 'clean'):
            clean()
        clean()
if __name__ == '__main__':
    main()


