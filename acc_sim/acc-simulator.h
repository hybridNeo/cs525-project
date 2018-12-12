#pragma once

#include <vector>
#include <chrono>
#include <memory>
#include <thread>
#include <mutex>
#include <fstream>
#include <sstream>
#include <condition_variable>


struct Task {
    // Scheduler assigned taskID
    int taskID;

    // When the task was started
    std::chrono::system_clock::time_point startTime;

    // Duration to completion
    std::chrono::nanoseconds timeToCompletion;

    // Time required to copy the data
    std::chrono::nanoseconds memoryOverhead;

    // The number of compute units required concurrently
    double computeUnitsRequired;

    // The size of data used by the task in Mb
    double dataSize;

    // Whether the task is complete yet
    bool isComplete;

    // Whether the task is being progressed right now if its on the queue
    // False even if its completed
    bool inProgress;

    // If this task comes from a context switch, it can have an arbitrary penalty on first start
    std::chrono::nanoseconds contextSwitchPenalty;
};

struct Consumer {
    //std::thread* currentThread;
    std::shared_ptr<std::thread> currentThread;

    //std::thread* task;
    std::shared_ptr<Task> task;
    // Mutex to indicate context switch
    std::mutex contextSwitchM;

    // Condition variable to control context switch
    std::condition_variable contextSwitchCV;
};

class AcceleratorSimulator{
    private:
        // Used to ensure that jobs can fit in the accelerator memory. Size in Mb
        double memorySize; 

        // Used to calculate how long it takes for a context switch and job initialization. In Mb/s
        double DRAMSpeed;

        // The max number of compute units available concurrently. Used for concurrency.
        double computeCapacity;

        // Record all the tasks ran on this accelerator. Arranged in order of addition unless context switch happens
        std::vector<std::shared_ptr<Task>> taskQueue;

        // List of Task IDs being executed right now
        std::vector<int> currentTaskIDs;

        // Mutex for controlling shared resources such as task queue and resource monitors
        std::mutex resources;

        // Condition variable for marking when resources are freed
        std::condition_variable resourcesCV;

        // Condition variable for monitoring when all tasks are done
        std::condition_variable doneCV;

        // Mutex for controlling access over DRAM
        std::mutex memoryTransferLock;

        // Compute capacity currently in use
        double computeCapacityInUse;

        // Memory currently in use
        double memoryInUse;

        // Additional penalty on a context switch
        std::chrono::nanoseconds contextSwitchPenalty;

        // Vector of threads representing currently executing tasks
        std::vector<std::shared_ptr<Consumer>> threadQueue;

        // Helper method to start a thread
        void startThread(std::shared_ptr<Task> task);

        // Helper method to start a task
        void startTask(std::shared_ptr<Task> task);

        // Helper method to end a thread
        void endThread(std::shared_ptr<Task> task, std::shared_ptr<Consumer> consumer);

        void updateTaskQueue();

        // Returns the compute capacity currently available in the accelerator
        double computeCapacityAvailableWithLock();

        // Returns the amount of memory currently available in the accelerator
        double memoryAvailableWithLock();

        std::ofstream& outputFile;

        int performanceVariance = 20;
        int highVarianceProbability = 4;
        int highVariancePerf = 100;

    public:
        // Constructor with initial properties
        // memorySize in Mb
        // DRAMSpeed in Mb/s
        AcceleratorSimulator(double memorySize, double computeCapacity, double DRAMSpeed, std::chrono::nanoseconds contextSwitchPenalty, std::ofstream& outputFile);

        // Add a task to the end of the queue. Returns -1 if cannot put on accelerator or task is invalid.
        // Else returns the taskID. dataSize in Mb
        int addTask(std::chrono::nanoseconds duration, double dataSize, double computeSize, int taskID);

        // Pass in a taskID to which the GPU should context switch out of order. Method sleeps to account for 
        // memory copying overhead. Returns -1 if task is not found or already being executed. Else returns 1
        int contextSwitch(int taskId, std::vector<std::shared_ptr<Task>>& tasksReplaced, int targetID);

        // Returns the compute capacity currently available in the accelerator
        double computeCapacityAvailable();

        // Returns the amount of memory currently available in the accelerator
        double memoryAvailable();

        // Returns the number of tasks left to be processed right now
        int getNumTasksInQueue();

        // Returns the current taskIDs being executed. Empty vector if no task is being run
        std::vector<int> getCurrentTaskIDs();

        // Waits for all tasks in queue to complete and then returns
        void returnWhenDone();

        // Empty out all the pending tasks
        void emptyQueue();

        // Move the task out if its still in task queue
        bool moveTask(int taskID);
};
