#pragma once

#include <vector>
#include <chrono>
#include <memory>

/**
 * Questions to consider:
 *      1) Should GPUs be allowed to run multiple jobs at once?
 *      2) Should GPU automatically switch to a previous job after a context switch job is done?
 */

struct Task {
    // GPU assigned taskID
    int taskID;
    
    // When the task was started
    std::chrono::system_clock::time_point startTime;

    // Duration to completion
    std::chrono::microseconds timeToCompletion;

    // Overhead each time task is started. Calculated based on DRAMSpeed
    std::chrono::microseconds memoryOverhead;

    // The size of data used by the task in Mb
    int dataSize;

    // Whether the task is complete yet
    bool isComplete;
    
    // Whether the task is being progressed right now if its on the queue
    // False even if its completed
    bool inProgress;
};

class GPUSimulator{
    private:
        // Used to ensure that jobs can fit in the GPU memory. Size in Mb
        int memorySize; 

        // Used to calculate how long it takes for a context switch and job initialization. In Mb/s
        double DRAMSpeed; 

        // Record all the tasks ran on this GPU. Arranged in order of addition unless context switch happens
        std::vector<std::shared_ptr<Task>> taskQueue;

        // taskID being executed right now
        int currentTaskID;

        void updateTaskQueue();

    public:
        
        // Constructor with initial properties
        GPUSimulator(int memorySize, double DRAMSpeed);

        // Add a task to the end of the queue. Returns -1 if cannot put on GPU.
        // Else returns the taskID. dataSize in Mb
        int addTask(std::chrono::microseconds duration, int dataSize);

        // Pass in a taskID to which the GPU should context switch out of order. Method sleeps to account for 
        // memory copying overhead. Returns -1 if task is not found. Else returns 1
        int contextSwitch(int taskId);

        // Returns true if cache is available to immediately process new jobs
        bool isAvailable();

        // Returns the number of tasks left to be processed right now
        int getNumTasksInQueue();

        // Returns the time for GPU to finish processing all pending tasks
        std::chrono::microseconds getTimeUntilFree();

        // Returns the current taskID being executed. -1 if no task is being run
        int getCurrentTaskID();
};
