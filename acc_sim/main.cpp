#include "acc-simulator.h"
#include <chrono>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <iterator>

int main(int argc, char * argv[]){
    if (argc != 6 && argc != 7){
        std::cout << "Usage: " << argv[0] << " <driverName> <memorySize in MB> <computeCapacity> <DRAMSpeed in Mb/s> <performanceVariance> <contextSwitchPenalty in milliseconds (optional)> \n";
        return 0;
    } 
    std::string fileInput = "req_" + (std::string(argv[1]));
    std::string fileOutput = "resp_" + (std::string(argv[1]));
    int memorySize = atoi(argv[2]);
    int computeCapacity = atoi(argv[3]);
    int DRAMSpeed = atoi(argv[4]);
    int performanceVariance = atoi(argv[5]);
    int contextSwitchPenalty = 0;
    if (argc == 7){
        int contextSwitchPenalty = atoi(argv[6]);
    } 
    std::ofstream outputFifo(fileOutput);
    std::ifstream inputFifo(fileInput);
    AcceleratorSimulator acc(memorySize, computeCapacity, DRAMSpeed, std::chrono::milliseconds(contextSwitchPenalty), outputFifo, performanceVariance);
    std::string line;
    if (inputFifo.is_open())
    {
        while ( getline (inputFifo,line) )
        {
            std::istringstream iss(line);
            std::vector<std::string> tokens(std::istream_iterator<std::string>{iss},
                    std::istream_iterator<std::string>());
            if (tokens[0] == "addTask"){
                auto taskDuration = std::chrono::milliseconds(std::stoi(tokens[1]));
                int taskMemorySize = std::stoi(tokens[2]);
                int taskComputeSize = std::stoi(tokens[3]);
                int taskID = std::stoi(tokens[4]);
                outputFifo << acc.addTask(taskDuration, taskMemorySize, taskComputeSize, taskID) << std::endl;
            }
            else if (tokens[0] == "contextSwitch"){
                int taskID = std::stoi(tokens[1]);
                int targetID = std::stoi(tokens[2]);
                std::vector<std::shared_ptr<Task>> tasksReplaced;
                outputFifo << acc.contextSwitch(taskID, tasksReplaced, targetID) << " " << tasksReplaced.size() << std::endl;
                for (auto taskPtr : tasksReplaced){
                     //std::chrono::duration_cast<std::chrono::minutes>(sec).count()
                    outputFifo << "taskFlushed: " << (std::chrono::duration_cast<std::chrono::milliseconds>(taskPtr->timeToCompletion)).count() << " " << taskPtr->dataSize << " " << taskPtr->computeUnitsRequired << " " << taskPtr->taskID << std::endl;
                }
            }
            else if (tokens[0] == "computeCapacityAvailable"){
                outputFifo << "computeCapacity " << acc.computeCapacityAvailable() << std::endl;
            }
            else if (tokens[0] == "memoryAvailable"){
                outputFifo << "memoryAvailable " << acc.memoryAvailable() << std::endl;
            }
            else if (tokens[0] == "getNumTasksInQueue"){
                outputFifo << "numTasks " << acc.getNumTasksInQueue() << std::endl;
            }
            else if (tokens[0] == "getCurrentTaskIDs"){
                outputFifo << "currentIDs ";
                for (int taskID : acc.getCurrentTaskIDs()){
                    outputFifo << taskID << " ";
                }
                outputFifo << std::endl; 
            }
            else if (tokens[0] == "returnWhenDone"){
                acc.returnWhenDone(); 
                outputFifo << "Done" << std::endl;
                return 0;
            } 
            else if (tokens[0] == "emptyQueue"){
                acc.emptyQueue(); 
            }
            else if (tokens[0] == "moveTask"){
                int taskID = std::stoi(tokens[1]);
                std::string destination = tokens[2]; 
                bool moved = acc.moveTask(taskID);
                if (moved == true){
                    outputFifo << "movedTask:" << taskID << " to " << destination << std::endl;
                }
            }
            else{
                outputFifo << "Invalid input " << std::endl;
            }
        }
        acc.returnWhenDone();
        outputFifo << "Done" << std::endl;
        inputFifo.close();
        outputFifo.close();
    } else std::cout << "Unable to open file" << std::endl;

}

//    using namespace std::chrono_literals;

//AcceleratorSimulator acc(100 /*memorySize*/, 50 /*computeCapacity*/, 10 /*DRAMSpeed */, 1s /*contextSwitchPenalty */);
//   int task1 = acc.addTask(2s, 200 /* datasize */, 10 /*computeSize*/, 1 /* taskID*/);
//   int task2 = acc.addTask(2s, 10, 200, 0);
//  int task3 = acc.addTask(2s, 10 /* datasize */, 10 /*computeSize*/, 2 /* taskID*/);
/* int task4 = acc.addTask(4s, 100, 10, 3);
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
}*/

/*
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main () {
string line;
ifstream myfile ("example.txt");
if (myfile.is_open())
{
while ( getline (myfile,line) )
{
cout << line << '\n';
}
myfile.close();
}

else cout << "Unable to open file";

return 0;
}*/
