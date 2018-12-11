#include "acc-simulator.h"

#include <thread>
#include <chrono>
#include <cstdint>
#include <algorithm>
#include <iostream>
#include <time.h>

AcceleratorSimulator::AcceleratorSimulator(double memorySize, double computeCapacity, double DRAMSpeed, std::chrono::nanoseconds contextSwitchPenalty, std::ofstream& outputFifo) : outputFile(outputFifo){
    srand(time(0));
    this->memorySize = memorySize;
    this->DRAMSpeed = DRAMSpeed;
    this->computeCapacity = computeCapacity;
    this->contextSwitchPenalty = contextSwitchPenalty;
    this->computeCapacityInUse = 0;
    this->memoryInUse = 0;
}

int AcceleratorSimulator::addTask(std::chrono::nanoseconds duration, double dataSize, double computeUnitsRequired, int taskID){
    if (dataSize > this->memorySize || computeUnitsRequired > this->computeCapacity || computeUnitsRequired <= 0 || dataSize <= 0){
        // Ensure the task is valid for this accelerator 
        return -1;
    }
    auto newTask = std::make_shared<Task>(); 
    newTask->taskID = taskID;
    newTask->inProgress = false;
    newTask->timeToCompletion = duration;
    newTask->computeUnitsRequired = computeUnitsRequired;
    // Convert seconds to nanoseconds
    newTask->memoryOverhead = std::chrono::nanoseconds((uint64_t)((dataSize*1000000000)/DRAMSpeed));
    newTask->dataSize = dataSize;
    newTask->isComplete = false;
    std::lock_guard<std::mutex> lock(this->resources);
    if (this->computeCapacityAvailableWithLock() >= computeUnitsRequired &&
            this->memoryAvailableWithLock() >= dataSize && this->taskQueue.size() == 0){
        // Start the task if enough resources are available
        this->startTask(newTask);
        std::thread t1(&AcceleratorSimulator::startThread, this, newTask);
        t1.detach();
        auto consumer = std::make_shared<Consumer>();
        consumer->task = newTask;
        this->threadQueue.push_back(consumer);
    }
    else{
        // Add it to task queue for later
        taskQueue.push_back(newTask);
    }
    return newTask->taskID;
}

void AcceleratorSimulator::startTask(std::shared_ptr<Task> task){
    task->inProgress = true;
    task->isComplete = false;
    this->memoryInUse += task->dataSize;
    this->computeCapacityInUse += task->computeUnitsRequired;
    currentTaskIDs.push_back(task->taskID);
}

void AcceleratorSimulator::endThread(std::shared_ptr<Task> task, std::shared_ptr<Consumer> consumer){
    // Modify state variables to mark tasks's stop
    std::lock_guard<std::mutex> lock(this->resources);

    // Remove from currentTaskIDs
    for (auto it = this->currentTaskIDs.begin() ; it != this->currentTaskIDs.end(); ++it){
        if (*it == task->taskID){
            this->currentTaskIDs.erase(it);
            break;
        }
    }
    // Free up resources

    this->memoryInUse -= task->dataSize;
    this->computeCapacityInUse -= task->computeUnitsRequired;
    this->resourcesCV.notify_all();
    // Remove from thread queue as this should stop
    for (auto it = this->threadQueue.begin() ; it != this->threadQueue.end(); ++it){
        if (*it == consumer){
            this->threadQueue.erase(it);
            break;
        }
    }
}

void AcceleratorSimulator::startThread(std::shared_ptr<Task> task){
    std::shared_ptr<Consumer> consumer;
    {
        std::lock_guard<std::mutex> lock(this->resources);
        for (auto& thread: this->threadQueue){
            if (thread->task->taskID == task->taskID){
                consumer = thread;
                break;
            }
        }
    } // To ensure this thread is added to the thread queue

    std::this_thread::sleep_for(task->contextSwitchPenalty);
    task->contextSwitchPenalty = std::chrono::nanoseconds(0);
    std::unique_lock<std::mutex> memoryLock(this->memoryTransferLock);
    // Check for context switch during memory transfer
    std::unique_lock<std::mutex> contextSwitchLock(consumer->contextSwitchM);
    auto contextSwitch = consumer->contextSwitchCV.wait_for(contextSwitchLock, task->memoryOverhead);
    memoryLock.unlock();
    if (contextSwitch == std::cv_status::timeout){
        // Memory transfer successful
        // Check for context switch during task processing
        task->startTime = std::chrono::system_clock::now();
        double variance = rand() % (this->performanceVariance * 2);
        variance = variance >= this->performanceVariance ? (variance/2.0) : (-1*variance/2.0);
        variance /= 100.0;
        if (variance >= 0){
            task->timeToCompletion += std::chrono::nanoseconds((int)(variance*task->timeToCompletion.count()));
        } else{
            task->timeToCompletion -= std::chrono::nanoseconds((int)(variance*task->timeToCompletion.count()));
        }
        if (rand() % highVarianceProbability == 1){
            task->timeToCompletion *= (2 + ((rand()%highVariancePerf)/100));
        }
        outputFile << "taskStarted: " << task->taskID << " with cost " << (int)(task->timeToCompletion.count()/1000000) << std::endl;
        contextSwitch = consumer->contextSwitchCV.wait_for(contextSwitchLock, task->timeToCompletion);
        auto timeSpent = std::chrono::system_clock::now() - task->startTime;
        if (contextSwitch == std::cv_status::timeout){
            this->endThread(task, consumer);
            // Task completed 
            task->inProgress = false;
            task->isComplete = true; 
            std::lock_guard<std::mutex> lock(this->resources);
            outputFile << "Finished task " << task->taskID << std::endl;
            if (this->taskQueue.size() == 0){
                this->doneCV.notify_all();
            }

            while (this->taskQueue.size() >= 1){
                // Check if more tasks are available
                auto newTask = this->taskQueue[0];
                if (this->computeCapacityAvailableWithLock() >= newTask->computeUnitsRequired &&
                        this->memoryAvailableWithLock() >= newTask->dataSize){
                    // Start the task if enough resources are available
                    this->startTask(newTask);
                    std::thread t1(&AcceleratorSimulator::startThread, this, newTask);
                    t1.detach();
                    auto consumer = std::make_shared<Consumer>();
                    //consumer->currentThread = t1;
                    consumer->task = newTask;
                    this->threadQueue.push_back(consumer);
                    this->taskQueue.erase(this->taskQueue.begin());
                } else{
                    break;
                } 
            } 
            return;
        } else {
            // Task got interrupted due to a context switch
            // Transfer memory out
            memoryLock.lock();
            std::this_thread::sleep_for(task->memoryOverhead);
            memoryLock.unlock();
            // Task incomplete
            task->inProgress = false;
            task->isComplete = false;
            task->timeToCompletion -= std::chrono::duration_cast<std::chrono::nanoseconds>(timeSpent);
            this->endThread(task, consumer);
        }
    } else{
        // Memory transfer interrupted 
        this->endThread(task, consumer);
        // Task incomplete
        task->inProgress = false;
        task->isComplete = false;
    }
    /*{
        std::cout << "Locking resources" << std::endl;
        std::lock_guard<std::mutex> lock(this->resources);
        this->taskQueue.insert(this->taskQueue.begin(), task);
        std::cout << "Unlocking resources" << std::endl;
    }*/
}

bool compareConsumers(std::shared_ptr<Consumer> c1, std::shared_ptr<Consumer> c2){
    return (c1->task->timeToCompletion + c1->task->memoryOverhead >= c2->task->timeToCompletion + c2->task->memoryOverhead);
}

int AcceleratorSimulator::contextSwitch(int taskID, std::vector<std::shared_ptr<Task>>& tasksReplaced){
    std::unique_lock<std::mutex> lock(this->resources);
    std::shared_ptr<Task> task;
    for (auto it = this->taskQueue.begin() ; it != this->taskQueue.end(); ++it){
        if ((*it)->taskID == taskID){
            task = *it;
            task->contextSwitchPenalty = this->contextSwitchPenalty;
            if (this->computeCapacityAvailableWithLock() >= task->computeUnitsRequired &&
                    this->memoryAvailableWithLock() >= task->dataSize){
                // Start the task if enough resources are available
                this->startTask(task);
                std::thread t1(&AcceleratorSimulator::startThread, this, task);
                t1.detach();
                auto consumer = std::make_shared<Consumer>();
                //consumer->currentThread = t1;
                consumer->task = task;
                this->threadQueue.push_back(consumer);
                this->taskQueue.erase(it);
            }
            else{
                std::sort (this->threadQueue.begin(), this->threadQueue.end(), compareConsumers); 
                double freeCompute = this->computeCapacityAvailableWithLock();
                double freeMemory = this->memoryAvailableWithLock();
                int index = 0;
                while (freeCompute < task->computeUnitsRequired || freeMemory < task->dataSize){
                    freeCompute += threadQueue[index]->task->computeUnitsRequired;
                    freeMemory += threadQueue[index]->task->dataSize;
                    threadQueue[index]->contextSwitchCV.notify_all();
                    tasksReplaced.push_back(threadQueue[index]->task);
                    index++;
                }
                freeCompute = this->computeCapacityAvailableWithLock();
                freeMemory = this->memoryAvailableWithLock();
                while (freeCompute < task->computeUnitsRequired || freeMemory < task->dataSize){
                    this->resourcesCV.wait(lock);
                    freeCompute = this->computeCapacityAvailableWithLock();
                    freeMemory = this->memoryAvailableWithLock();
                }
                // Start the task if enough resources are available
                this->startTask(task);
                std::thread t1(&AcceleratorSimulator::startThread, this, task);
                t1.detach();
                auto consumer = std::make_shared<Consumer>();
                //consumer->currentThread = t1;
                consumer->task = task;
                this->threadQueue.push_back(consumer);
                this->taskQueue.erase(it);
            }
            return 1;
        }
    }
    return -1;
}

/*
   if (task->inProgress == false && task->isComplete == false){
   int currTask = getCurrentTaskID();
   if (currTask != -1){
   for (auto innerIt = this->taskQueue.begin() ; innerIt != this->taskQueue.end(); ++innerIt){
   auto innerTask = *innerIt;
   if (innerTask->taskID == currTask){
   innerTask->inProgress = false;
//std::chrono::time_point_cast<std::chrono::nanoseconds>(now)
auto timeSpent = std::chrono::system_clock::now() - innerTask->startTime;
if (timeSpent >= innerTask->memoryOverhead){
innerTask->timeToCompletion -= std::chrono::duration_cast<std::chrono::nanoseconds>(timeSpent) - innerTask->memoryOverhead;
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

bool AcceleratorSimulator::isAvailable(){
updateTaskQueue();
for (auto& task : this->taskQueue){
if (task->inProgress == true){
return false;
}
}
return true;
}

std::chrono::nanoseconds AcceleratorSimulator::getTimeUntilFree(){
updateTaskQueue();
std::chrono::nanoseconds timeLeft(0);
for (auto& task : this->taskQueue){
if (task->inProgress == true){
timeLeft += task->timeToCompletion;
}
else if (task->isComplete == false){
timeLeft += task->memoryOverhead + task->timeToCompletion;
}
}
return timeLeft;
}*/

void AcceleratorSimulator::emptyQueue(){
    std::lock_guard<std::mutex> lock(this->resources);
    this->taskQueue.clear();
}

bool AcceleratorSimulator::moveTask(int taskID){
    std::lock_guard<std::mutex> lock(this->resources);
    for (auto it = this->taskQueue.begin() ; it != this->taskQueue.end(); ++it){
        if ((*it)->taskID == taskID){
            it = this->taskQueue.erase(it);
            return true;
        }
    }
    return false;
}

int AcceleratorSimulator::getNumTasksInQueue(){
    std::lock_guard<std::mutex> lock(this->resources);
    return this->taskQueue.size() + this->threadQueue.size();
}

std::vector<int> AcceleratorSimulator::getCurrentTaskIDs(){
    std::lock_guard<std::mutex> lock(this->resources);
    std::vector<int> ret;
    for (auto& thread: this->threadQueue){
        ret.push_back(thread->task->taskID);
    }
    return ret;
}

double AcceleratorSimulator::computeCapacityAvailable(){
    std::lock_guard<std::mutex> lock(this->resources);
    return computeCapacityAvailableWithLock();
}

double AcceleratorSimulator::memoryAvailable(){
    std::lock_guard<std::mutex> lock(this->resources);
    return memoryAvailableWithLock();
}

double AcceleratorSimulator::computeCapacityAvailableWithLock(){
    return computeCapacity - computeCapacityInUse;
}

double AcceleratorSimulator::memoryAvailableWithLock(){
    return memorySize - memoryInUse;
}

void AcceleratorSimulator::returnWhenDone(){
    std::unique_lock<std::mutex> lock(this->resources);
    while (this->taskQueue.size() + this->threadQueue.size() != 0){
        this->doneCV.wait(lock);
    }
}

/*void AcceleratorSimulator::updateTaskQueue(){
  auto now = std::chrono::system_clock::now();
  for (auto& task: this->taskQueue){
  if (task->inProgress == true){
  std::chrono::nanoseconds timeLeft(0);
  if (task->startTime + task->timeToCompletion + task->memoryOverhead <= now){
  timeLeft = std::chrono::duration_cast<std::chrono::nanoseconds>(now - task->startTime) - task->memoryOverhead - task->timeToCompletion;
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
  }*/
