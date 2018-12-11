#!/bin/bash
for i in {1..5}
do
    python3 test_sim.py simple
done
for i in {1..5}
do
    python3 test_sim.py rr
done
for i in {1..5}
do
    python3 test_sim.py dynamic
done
