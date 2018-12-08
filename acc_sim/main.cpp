#include "acc-simulator.h"
#include <chrono>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <iterator>

int main(int argc, char * argv[]){
    if (argc != 5 || argc != 6){
        std::cout << "Usage: " << argv[0] << "<driverName> <memorySize in MB> <computeCapacity> <DRAMSpeed in Mb/s> <contextSwitchPenalty in microseconds (optional)> \n";
        return 0;
    } 
    std::string fileInput = "req_" + (std::string(argv[1]));
    std::string fileOutput = "resp_" + (std::string(argv[1]));
    int memorySize = atoi(argv[2]);
    int computeCapacity = atoi(argv[3]);
    int DRAMSpeed = atoi(argv[4]);
    int contextSwitchPenalty = 0;
    if (argc == 6){
        int contextSwitchPenalty = atoi(argv[5]);
    } 
    AcceleratorSimulator acc(memorySize, computeCapacity, DRAMSpeed, std::chrono::microseconds(contextSwitchPenalty));
    std::ifstream inputFifo(fileInput);
    std::ofstream outputFifo(fileOutput);
    std::string line;
    if (inputFifo.is_open())
    {
        while ( getline (inputFifo,line) )
        {
            std::istringstream iss(line);
            std::vector<std::string> tokens(std::istream_iterator<std::string>{iss},
                    std::istream_iterator<std::string>());
            if (tokens[0] == "addTask"){
                auto taskDuration = std::chrono::microseconds(std::stoi(tokens[1]));
                int taskMemorySize = std::stoi(tokens[2]);
                int taskComputeSize = std::stoi(tokens[3]);
                int taskID = std::stoi(tokens[4]);
                outputFifo << acc.addTask(taskDuration, taskMemorySize, taskComputeSize, taskID) << std::endl;
            }
            else if (tokens[0] == "contextSwitch"){
                int taskID = std::stoi(tokens[1]);
                outputFifo << acc.contextSwitch(taskID) << "\n";
            }
            else if (tokens[0] == "computeCapacityAvailable"){
                outputFifo << acc.computeCapacityAvailable() << "\n";
            }
            else if (tokens[0] == "memoryAvailable"){
                outputFifo << acc.memoryAvailable() << "\n";
            }
            else if (tokens[0] == "getNumTasksInQueue"){
                outputFifo << acc.getNumTasksInQueue() << "\n";
            }
            else if (tokens[0] == "getCurrentTaskIDs"){
                for (int taskID : acc.getCurrentTaskIDs()){
                    outputFifo << taskID << " ";
                }
                outputFifo << "\n";
            }
            else if (tokens[0] == "returnWhenDone"){
                acc.returnWhenDone(); 
                outputFifo << "Done \n";
                return 0;
            }
            else{
                outputFifo << "Invalid input \n";
            }
        }
        inputFifo.close();
        outputFifo.close();
    } else std::cout << "Unable to open file";

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
