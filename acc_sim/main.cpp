#include "acc-simulator.h"
#include <chrono>
#include <iostream>

int main(){
    using namespace std::chrono_literals;
    AcceleratorSimulator acc(100 /*memorySize*/, 50 /*computeCapacity*/, 10 /*DRAMSpeed */, 1s /*contextSwitchPenalty */);
    int task1 = acc.addTask(2s, 200 /* datasize */, 10 /*computeSize*/, 1 /* taskID*/);
    int task2 = acc.addTask(2s, 10, 200, 0);
    int task3 = acc.addTask(2s, 10 /* datasize */, 10 /*computeSize*/, 2 /* taskID*/);
    int task4 = acc.addTask(4s, 100, 10, 3);
    acc.addTask(2s, 10, 10, 4);
    acc.addTask(2s, 10, 10, 5);
    acc.addTask(2s, 10, 10, 6);
    std::this_thread::sleep_for(15s);
    acc.contextSwitch(5);
    std::cout << "comp available" << acc.computeCapacityAvailable() << std::endl;
    std::cout << "memory available" << acc.memoryAvailable() << std::endl;
    std::cout << "tasks in queue" << acc.getNumTasksInQueue() << std::endl;
    std::cout << "current tasks " << std::endl;
    for (auto id: acc.getCurrentTaskIDs()){
        std::cout << id << std::endl;
    }
    acc.returnWhenDone();
}
