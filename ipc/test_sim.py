import asyncio
from driver_sim import Driver
from drivercontroller import DriverController, Handle
from fifo import FifoListener, FifoWriter
from multiprocessing import Process, Value
import subprocess
import signal

import sys
sys.path.insert(0,'../utils/')
from graph_maker import generate_random_dag, fft_graph, mpeg_graph, gauss_graph, mp3_graph

sys.path.insert(0,'../scheduler/')
import staticSchedule
import rrSchedule
import dynamicSchedule
from ctypes import Structure, c_double
import time
from multiprocessing import Process, Manager, Value
import os


manager = Manager()
scheduler = ""

def start_drivers(drivers):
    d = []
    for i in drivers:
        d.append(Driver(*i))

    res = []
    for i in d:
        res.append(Process(target = i.start))

    return res

class Querier():
    def __init__(self, computeCost = [], tGraph = None, driverCount = 0, dagCount = 1, singleDagNodeCount = -1):
        self.writer = FifoWriter('server_req')
        self.tasks = []
        self.finished_jobs = 0
        self.start_time = 0
        self.contextSwitchResponse = util
        self.computeCapacityResponse = util
        self.memoryResponse = util
        self.numTasksResponse = util
        self.currentTasksResponse = util
        self.doneResponse = util
        self.taskCount = Value('i', 0)
        self.duration = Value('f', 0)
        self.finishedTasks = []
        self.pendingTasks = manager.dict()
        self.pendingTasksCopy = manager.dict()
        self.progressTasks = manager.dict()
        self.updatedCostList = manager.list()
        self.computeCost = computeCost
        self.tGraph = tGraph
        self.driverCount = driverCount
        self.parentPID = os.getpid()
        self.dagCount = dagCount
        self.singleDagNodeCount = singleDagNodeCount
        self.start_time = time.time()
        self.dagPending = manager.list([0 for i in range(self.dagCount)])

    def startedTask(self, taskID, taskDuration, taskVal):
        print ("Task", taskID, "started execution.")
        self.progressTasks[taskID] = taskVal
        found = False
        for index in range(len(self.updatedCostList)):
            if (self.updatedCostList[index][0] == taskID):
                self.updatedCostList[index] = (taskID, taskVal['proc'], taskDuration)
                found = True
                break
        if (found == False):
            self.updatedCostList.append((taskID, taskVal['proc'], taskDuration))
        if (scheduler == "dynamic" or scheduler == "contextSwitchEnabled"):
            if (scheduler == "contextSwitchEnabled"):
                startRange = taskID - (taskID%self.singleDagNodeCount);
                endRange = startRange + self.singleDagNodeCount;
                localProgressTasks = {}
                localCostList = []
                for key, val in self.progressTasks.items():
                    if (key >= startRange and key < endRange):
                        localProgressTasks[key] = val
                for item in self.updatedCostList:
                    key = item[0]
                    if (key >= startRange and key < endRange):
                        localCostList.append(item)

                reorgedTasks = dynamicSchedule.dynamicSchedule(localProgressTasks, localCostList, self.computeCost, self.tGraph, startRange)
                self.appendPendingTasks(reorgedTasks)
            else:
                reorgedTasks = dynamicSchedule.dynamicSchedule(self.progressTasks, self.updatedCostList, self.computeCost, self.tGraph)
                self.appendPendingTasks(reorgedTasks)


    def appendPendingTasks(self, reorgedTasks):
        change = False
        for key, val in reorgedTasks.items():
            if key in self.pendingTasks and val['proc'] != self.pendingTasks[key]['proc']:
                change = True
                #print ("Moved pending task", key)
                self.pendingTasks[key] = val
                self.pendingTasksCopy[key] = val
            elif key not in self.progressTasks and val['proc'] != self.pendingTasksCopy[key]['proc']:
                #print ("Moving scheduled task ", key)
                change = True
                self.move_task(chr(ord('a') + self.pendingTasksCopy[key]['proc']), key, chr(ord('a') + val['proc']))
        if (change == True):
            print ("Updated schedule dynamically")

    def setPendingTasks(self, pendingTasks):
        print ("Loading the tasks into driver queues")
        self.pendingTasks.clear()
        self.pendingTasksCopy.clear()
        for key, val in pendingTasks.items():
            self.pendingTasks[key] = val
            self.pendingTasksCopy[key] = val
            if ("contextSwitch" in scheduler):
                parentDag = (int)(key/self.singleDagNodeCount);
                self.dagPending[parentDag] += 1
        self.addTasks()

    def addTasks(self):
        tasksAdded = []
        for taskID, taskInfo in self.pendingTasks.items():
            processor = taskInfo['proc']
            predecessors = taskInfo['predecessors']
            predsToRemove = [i for i in predecessors if i in self.finishedTasks]
            for pred in predsToRemove:
                predecessors.remove(pred)

            if (len(predecessors) == 0):
                startTime = taskInfo['time'][0]
                endTime = taskInfo['time'][1]
                self.add_task(chr(ord('a') + taskInfo['proc']), ((str)((endTime - startTime)*(100))), "100", "50", (str)(taskID))
                tasksAdded.append(taskID)
            self.pendingTasksCopy[taskID] = taskInfo

        for taskID in tasksAdded:
            del self.pendingTasks[taskID]


    def cleanup(self):
        os.system("make clean")

    def handler(self, response):
        #print("[Querier] got response :" , response)
        if ("Finished task " in response):
            print (response)
            finishedTaskID = (int)(response.split()[2])
            self.finishedTasks.append(finishedTaskID)
            self.finished_jobs += 1
            self.addTasks()
            if ("contextSwitch" in scheduler):
                parentDag = (int)(finishedTaskID/self.singleDagNodeCount);
                self.dagPending[parentDag] -= 1
                if (self.dagPending[parentDag] == 0):
                    for i in self.dagPending:
                        if i != 0:
                            return
                    dagDuration = time.time() - self.start_time
                    print("[Querier] DAG", parentDag, "Completed : " , dagDuration)

            if(self.finished_jobs == self.taskCount.value):
                duration = time.time() - self.start_time
                print("[Querier] Test Completed : " , duration)
                # process = subprocess.Popen(..)
                # process.send_signal(signal.SIGINT)
                time.sleep(2)
                self.cleanup()
                os.kill(self.parentPID, signal.SIGKILL)

        elif ("taskStarted" in response):
            taskInfo = response.split(":")[1]
            details = taskInfo.split()
            taskID = (int)(details[0])
            taskDuration = ((int)(details[3]))/100.0
            originalVal = self.pendingTasksCopy[taskID]
            startTime = time.time() - self.start_time
            endTime = startTime + taskDuration
            if (taskDuration > 10 and scheduler == "contextSwitchEnabled"):
                if (taskID < self.singleDagNodeCount):
                    csProcess = Process(target = self.delayedContextSwitch, args=(taskID, originalVal['proc'], 10, taskID+self.singleDagNodeCount))
                    csProcess.start()
                else:
                    csProcess = Process(target = self.delayedContextSwitch, args=(taskID, originalVal['proc'], 10, taskID-self.singleDagNodeCount))
                    csProcess.start()
            originalVal['time'] = (startTime, endTime)
            self.pendingTasksCopy[taskID] = originalVal
            self.startedTask(taskID, taskDuration, self.pendingTasksCopy[taskID])

        elif ("taskFlushed" in response):
            print ("Context switch sent a task back to driver controller")
            self.taskCount.value -= 1
            taskInfo = response.split(":")
            taskDetails = taskInfo[1].split()
            timeLeft = ((int)(taskDetails[0]))/100.0
            computeSize = (int)(taskDetails[2])
            memorySize = (int)(taskDetails[1])
            taskId = (int)(taskDetails[3])
            taskInfo = self.pendingTasksCopy[taskId]
            #self.pendingTasks[taskId] = self.pendingTasksCopy
            self.add_task(chr(ord('a') + taskInfo['proc']), ((str)((timeLeft)*(100))), (str)(memorySize),  (str)(computeSize), (str)(taskId))
            # taskFlushed: 3370 50 50 0

        elif ("computeCapacity" in response):
            self.computeCapacityResponse((int)(response.split()[1]))
        elif ("memoryAvailable" in response):
            self.memoryResponse((int)(response.split()[1]))
        elif ("numTasks" in response):
            self.numTasksResponse((int)(response.split()[1]))
        elif ("currentIDs" in response):
            self.currentTasksResponse(([(int)(i) for i in response.split()[1:]]))
        elif ("movedTask" in response):
            print ("Moving task to different accelerator")
            self.taskCount.value -= 1
            taskInfo = response.split(":")[1]
            details = taskInfo.split()
            taskID = (int)(details[0])
            destination = (details[2])
            originalVal = self.pendingTasksCopy[taskID]
            originalVal['proc'] = ord(destination) - ord('a')
            self.pendingTasks[taskID] = originalVal
        elif ("Done" in response):
            self.doneResponse("done")

    def delayedContextSwitch(self, taskID, process, delay, targetID):
        time.sleep(delay)
        self.contextSwitch((chr(ord('a') + process)), targetID, taskID)

    def empty_queue(self, driver_name):
        self.writer.write_to_stream(driver_name+";emptyQueue")

    def move_task(self, driver_name, taskID, destination):
        self.writer.write_to_stream(driver_name+";moveTask;"+(str)(taskID)+";"+destination)

    def add_task(self, driver_name, durationMs, memoryMb, computeUnits, taskId):
        self.taskCount.value += 1
        taskInfo = [driver_name, durationMs, memoryMb, computeUnits, taskId]
        self.writer.write_to_stream(taskInfo[0]+";addTask;"+";".join(taskInfo[1:]))
        #self.tasks.append([driver_name, durationMs, memoryMb, computeUnits, taskId]);

    def contextSwitch(self, driver_name, taskID, targetID):
        self.writer.write_to_stream(driver_name+";contextSwitch;"+(str)(taskID)+";"+(str)(targetID))

    def computeCapacityAvailable(self, driver_name, callback):
        self.computeCapacityResponse = callback
        self.writer.write_to_stream(driver_name+";computeCapacityAvailable")

    def memoryAvailable(self, driver_name, callback):
        self.memoryResponse = callback
        self.writer.write_to_stream(driver_name+";memoryAvailable")

    def getNumTasksInQueue(self, driver_name, callback):
        self.numTasksResponse = callback
        self.writer.write_to_stream(driver_name+";getNumTasksInQueue")

    def getCurrentTaskIDs(self, driver_name, callback):
        self.currentTasksResponse = callback
        self.writer.write_to_stream(driver_name+";getCurrentTaskIDs")

    def returnWhenDone(self, driver_name, callback):
        self.doneResponse = callback
        self.writer.write_to_stream(driver_name+";returnWhenDone")

    def querier(self):
        r = FifoListener('server_resp', self.handler)
        resp = Process(target = r.listen)
        resp.start()
        #await asyncio.sleep(2)

def util(x):
    print (x)

def test_simple(adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost):


    tGraph = staticSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    # computeCost = [[int(i/6) for i in j] for j in computeCost]
    taskSchedule = staticSchedule.staticSchedule(tGraph, computeCost)
    print ("Obtained schedule.")

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier()
    # lambda x: (x%2 == 0)
    print ("Starting the simulators")
    m = start_drivers(drivers)

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    for i in bk:
        i.start()
    #q_process = Process(target = q.querier)
    #q_process.start()
    q.querier()
    q.setPendingTasks(taskSchedule)


    #import time
    #time.sleep(1)
    """q.add_task("a", "1000", "10", "10", "1")
    q.add_task("b", "1000", "10", "10", "2")
    q.computeCapacityAvailable("a", util)
    q.memoryAvailable("b", util)
    q.getNumTasksInQueue("a", util)
    q.getCurrentTaskIDs("b", util)
    q.returnWhenDone("a", util)
    q.returnWhenDone("b", lambda x : print("b finished"))"""

    for i in bk:
        i.join()
    #time.sleep(100)
    return q.duration.value


def test_rr(adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost):

    tGraph = rrSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    taskSchedule = rrSchedule.rrSchedule(tGraph, computeCost)
    print ("Obtained schedule.")

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier()
    # lambda x: (x%2 == 0)
    print ("Starting the simulators")
    m = start_drivers(drivers)

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    for i in bk:
        i.start()
    #q_process = Process(target = q.querier)
    #q_process.start()
    q.querier()
    q.setPendingTasks(taskSchedule)


    #import time
    #time.sleep(1)
    """q.add_task("a", "1000", "10", "10", "1")
    q.add_task("b", "1000", "10", "10", "2")
    q.computeCapacityAvailable("a", util)
    q.memoryAvailable("b", util)
    q.getNumTasksInQueue("a", util)
    q.getCurrentTaskIDs("b", util)
    q.returnWhenDone("a", util)
    q.returnWhenDone("b", lambda x : print("b finished"))"""

    for i in bk:
        i.join()
    #time.sleep(100)
    return q.duration.value

def test_dynamic(adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost):

    tGraph = staticSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    taskSchedule = staticSchedule.staticSchedule(tGraph, computeCost)
    print ("Obtained schedule.")

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier(computeCost, tGraph, len(drivers))
    # lambda x: (x%2 == 0)
    print ("Starting the simulators")
    m = start_drivers(drivers)

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    for i in bk:
        i.start()
    #q_process = Process(target = q.querier)
    #q_process.start()
    q.querier()
    q.setPendingTasks(taskSchedule)


    #import time
    #time.sleep(1)
    """q.add_task("a", "1000", "10", "10", "1")
    q.add_task("b", "1000", "10", "10", "2")
    q.computeCapacityAvailable("a", util)
    q.memoryAvailable("b", util)
    q.getNumTasksInQueue("a", util)
    q.getCurrentTaskIDs("b", util)
    q.returnWhenDone("a", util)
    q.returnWhenDone("b", lambda x : print("b finished"))"""

    for i in bk:
        i.join()
    time.sleep(100)
    return q.duration.value

def test_contextSwitch(adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost):

    tGraph = staticSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    taskSchedule = staticSchedule.staticSchedule(tGraph, computeCost)
    taskSchedule2 = staticSchedule.staticSchedule(tGraph, computeCost, len(taskSchedule))

    taskSchedule.update(taskSchedule2)
    print ("Obtained schedule.")

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    dagCount = 2
    singleDagNodeCount = len(taskSchedule)/2
    q = Querier(computeCost, tGraph, len(drivers), 2, singleDagNodeCount)
    # lambda x: (x%2 == 0)
    print ("Starting the simulators")
    m = start_drivers(drivers)

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    for i in bk:
        i.start()
    #q_process = Process(target = q.querier)
    #q_process.start()
    q.querier()
    q.setPendingTasks(taskSchedule)


    #import time
    #time.sleep(1)
    """q.add_task("a", "1000", "10", "10", "1")
    q.add_task("b", "1000", "10", "10", "2")
    q.computeCapacityAvailable("a", util)
    q.memoryAvailable("b", util)
    q.getNumTasksInQueue("a", util)
    q.getCurrentTaskIDs("b", util)
    q.returnWhenDone("a", util)
    q.returnWhenDone("b", lambda x : print("b finished"))"""

    for i in bk:
        i.join()
    time.sleep(100)
    return q.duration.value


def main():
    if len(sys.argv) < 2:
        print("Please Enter name of the test to run")
    else:
        global scheduler
        scheduler = sys.argv[1]
        if(len(sys.argv) == 2):
            adjMatrix = [[0,1,1,1,1,1,0,0,0,0],
                    [-1,0,0,0,0,0,0,1,1,0],
                    [-1,0,0,0,0,0,1,0,0,0],
                    [-1,0,0,0,0,0,0,1,1,0],
                    [-1,0,0,0,0,0,0,0,1,0],
                    [-1,0,0,0,0,0,0,1,0,0],
                    [0,0,-1,0,0,0,0,0,0,1],
                    [0,-1,0,-1,0,-1,0,0,0,1],
                    [0,-1,0,-1,-1,0,0,0,0,1],
                    [0,0,0,0,0,0,-1,-1,-1,0]]
            entryNode = 0
            exitNode = 9
            numTasks = 10
            numProcs = 3
            computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]
        else:
            if(sys.argv[2] == 'fft'):
                adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost = fft_graph()
            elif(sys.argv[2] == 'mpeg'):
                adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost = mpeg_graph()
            elif(sys.argv[2] == 'gauss'):
                adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost = gauss_graph()
            elif(sys.argv[2] == 'mp3'):
                adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost = mp3_graph()
            else:
                adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost = generate_random_dag(int(sys.argv[2]), 3, 1)

        print ("Generating the schedule")
        if sys.argv[1] == 'simple':
            print (test_simple(adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost))
        elif sys.argv[1] == 'rr':
            print (test_rr( adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost))
        elif sys.argv[1] == 'dynamic':
            print (test_dynamic( adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost))
        elif sys.argv[1] == 'contextSwitchEnabled':
            print (test_contextSwitch( adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost))
        elif sys.argv[1] == 'contextSwitchDisabled':
            print (test_contextSwitch( adjMatrix,entryNode,exitNode,numTasks,numProcs,computeCost))



if __name__ == '__main__':
    main()
