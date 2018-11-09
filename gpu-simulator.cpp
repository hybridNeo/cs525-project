#include "gpu-simulator.h"

GPUSimulator::GPUSimulator(int memorySize, double DRAMSpeed){
    this->memorySize = memorySize;
    this->DRAMSpeed = DRAMSpeed;
    this->currentTaskID = -1;
}

int GPUSimulator::addTask(std::chrono::microseconds duration, int dataSize){
    if (dataSize > memorySize){
        return -1;
    }
    auto newTask = std::make_shared<Task>(); 
    newTask->taskID = this->taskQueue.size();
    newTask->inProgress = false;
    if (this->isAvailable()){
        newTask->startTime = std::chrono::system_clock::now();
        newTask->inProgress = true;
        newTask->currentTaskID = newTask->taskID;
    }
    newTask->timeToCompletion = duration;
    newTask->memoryOverhead = std::chrono::milliseconds(dataSize/(DRAMSpeed*1000));
    newTask->dataSize = dataSize;
    newTask->isComplete = false;
    taskQueue.push_back(newTask);
    return newTask->taskID;
}

int GPUSimulator::contextSwitch(int taskID){
    for(const auto& task: this->taskQueue){
        if (task->taskID == taskID){
            if (task->inProgress == false && task->isComplete == false){
                int currTask = getCurrentTaskID();
                if (currTask == -1){
                    
                }
                else{
                }
            }
            return 0;
        }
    }
    return -1;
}

int GPUSimulator::isAvailable(){
}

