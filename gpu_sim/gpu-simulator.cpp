#include "gpu-simulator.h"
#include <thread>
#include <chrono>

GPUSimulator::GPUSimulator(int memorySize, double DRAMSpeed){
    this->memorySize = memorySize;
    this->DRAMSpeed = DRAMSpeed;
    this->currentTaskID = -1;
}

int GPUSimulator::addTask(std::chrono::microseconds duration, int dataSize){
    if (dataSize > this->memorySize){
        // Ensure job fits in memory
        return -1;
    }
    auto newTask = std::make_shared<Task>(); 
    newTask->taskID = this->taskQueue.size();
    newTask->inProgress = false;
    newTask->timeToCompletion = duration;
    newTask->memoryOverhead = std::chrono::milliseconds((int)(dataSize/(DRAMSpeed*1000)));
    newTask->dataSize = dataSize;
    newTask->isComplete = false;
    if (this->isAvailable()){
        // Start the task if GPU is available
        newTask->startTime = std::chrono::system_clock::now();
        newTask->inProgress = true;
        this->currentTaskID = newTask->taskID;
    }
    taskQueue.push_back(newTask);
    return newTask->taskID;
}

int GPUSimulator::contextSwitch(int taskID){
    updateTaskQueue();
    for (auto it = this->taskQueue.begin() ; it != this->taskQueue.end(); ++it){
        auto task = *it;
        if (task->taskID == taskID){
            if (task->inProgress == false && task->isComplete == false){
                int currTask = getCurrentTaskID();
                if (currTask != -1){
                    for (auto innerIt = this->taskQueue.begin() ; innerIt != this->taskQueue.end(); ++innerIt){
                        auto innerTask = *innerIt;
                        if (innerTask->taskID == currTask){
                            innerTask->inProgress = false;
                            //std::chrono::time_point_cast<std::chrono::milliseconds>(now)
                            auto timeSpent = std::chrono::system_clock::now() - innerTask->startTime;
                            if (timeSpent >= innerTask->memoryOverhead){
                                innerTask->timeToCompletion -= std::chrono::duration_cast<std::chrono::microseconds>(timeSpent) - innerTask->memoryOverhead;
                            }
                            std::this_thread::sleep_for(innerTask->memoryOverhead);
                            break;
                        }
                    }
                }
                this->taskQueue.erase(it);
                this->taskQueue.insert(taskQueue.begin(), task);
                task->startTime = std::chrono::system_clock::now();
                task->inProgress = true;
                this->currentTaskID = taskID;
            }
            return 1;
        }
    }
    return -1;
}

bool GPUSimulator::isAvailable(){
    updateTaskQueue();
    for (auto& task : this->taskQueue){
        if (task->inProgress == true){
            return false;
        }
    }
    return true;
}


int GPUSimulator::getNumTasksInQueue(){
    updateTaskQueue();
    int count = 0;
    for (auto& task : this->taskQueue){
        if (task->isComplete == false){
            count++;
        }
    }
    return count;
}


std::chrono::microseconds GPUSimulator::getTimeUntilFree(){
    updateTaskQueue();
    std::chrono::microseconds timeLeft(0);
    for (auto& task : this->taskQueue){
        if (task->inProgress == true){
            timeLeft += task->timeToCompletion;
        }
        else if (task->isComplete == false){
            timeLeft += task->memoryOverhead + task->timeToCompletion;
        }
    }
    return timeLeft;
}

int GPUSimulator::getCurrentTaskID(){
    updateTaskQueue();
    return currentTaskID;
}

void GPUSimulator::updateTaskQueue(){
    auto now = std::chrono::system_clock::now();
    for (auto& task: this->taskQueue){
        if (task->inProgress == true){
            std::chrono::microseconds timeLeft(0);
            if (task->startTime + task->timeToCompletion + task->memoryOverhead <= now){
                timeLeft = std::chrono::duration_cast<std::chrono::milliseconds>(now - task->startTime) - task->memoryOverhead - task->timeToCompletion;
                task->inProgress = false;
                task->isComplete = true;
                this->currentTaskID = -1;
                for (auto& innerTask: this->taskQueue){
                    if (innerTask->inProgress == false && innerTask->isComplete == false){
                        currentTaskID = innerTask->taskID;
                        if (innerTask->timeToCompletion + innerTask->memoryOverhead <= timeLeft){
                            innerTask->isComplete = true;
                            this->currentTaskID = -1;
                            timeLeft -= (innerTask->timeToCompletion + innerTask->memoryOverhead);
                        }
                        else {
                            innerTask->startTime = now - timeLeft;
                            innerTask->inProgress = true;
                            return;
                        }
                    }
                }
            }
            return;
        } else if (task->inProgress == false && task->isComplete == false){
            task->startTime = now;
            task->inProgress = true;
            this->currentTaskID = task->taskID;
            return;
        }
    }
}
