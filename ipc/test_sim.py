import asyncio
from driver_sim import Driver
from drivercontroller import DriverController, Handle
from fifo import FifoListener, FifoWriter
from multiprocessing import Process, Value

import sys
sys.path.insert(0,'../scheduler/')
import staticSchedule
import rrSchedule
import dynamicSchedule
from ctypes import Structure, c_double
import time
from multiprocessing import Process, Manager, Value


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
    def __init__(self, computeCost = [], tGraph = None, driverCount = 0):
        self.writer = FifoWriter('server_req')
        self.tasks = []
        self.finished_jobs = 0
        self.start_time = time.time()
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

    def startedTask(self, taskID, taskDuration, taskVal):
        self.progressTasks[taskID] = taskVal
        self.updatedCostList.append((taskID, taskVal['proc'], taskDuration))
        if (scheduler == "dynamic"):
            print (self.progressTasks)
            print (self.updatedCostList)
            reorgedTasks = dynamicSchedule.dynamicSchedule(self.progressTasks, self.updatedCostList, self.computeCost, self.tGraph)
            self.appendPendingTasks(reorgedTasks)

    def appendPendingTasks(self, reorgedTasks):
        for key, val in reorgedTasks.items():
            if key in self.pendingTasks and val['proc'] != self.pendingTasks[key]['proc']:
                print ("Moved pending task", key)
                self.pendingTasks[key] = val
                self.pendingTasksCopy[key] = val
            elif key not in self.progressTasks and val['proc'] != self.pendingTasksCopy[key]['proc']:
                print ("Moving scheduled task ", key)
                self.move_task(chr(ord('a') + self.pendingTasksCopy['proc']), key, chr(ord('a') + val['proc']))

    def setPendingTasks(self, pendingTasks):
        self.pendingTasks.clear()
        self.pendingTasksCopy.clear()
        for key, val in pendingTasks.items():
            self.pendingTasks[key] = val
            self.pendingTasksCopy[key] = val
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
                self.add_task(chr(ord('a') + taskInfo['proc']), ((str)((endTime - startTime)*(1000))), "100", "50", (str)(taskID))
                tasksAdded.append(taskID)

        for taskID in tasksAdded:
            del self.pendingTasks[taskID]

    def handler(self, response):
        print("[Querier] got response :" , response)
        if ("Finished task " in response):
            finishedTaskID = (int)(response.split()[2])
            self.finishedTasks.append(finishedTaskID)
            self.finished_jobs += 1
            self.addTasks()
            if(self.finished_jobs == self.taskCount.value):
                self.duration.value = time.time() - self.start_time
                print("[Querier] Test Completed : " , self.duration.value)

        elif ("taskStarted" in response):
            taskInfo = response.split(":")[1]
            details = taskInfo.split()
            taskID = (int)(details[0])
            taskDuration = ((int)(details[3]))/1000.0
            originalVal = self.pendingTasksCopy[taskID]
            startTime = time.time() - self.start_time
            endTime = startTime + taskDuration
            originalVal['time'] = (startTime, endTime)
            self.pendingTasksCopy[taskID] = originalVal
            self.startedTask(taskID, taskDuration, self.pendingTasksCopy[taskID])

        elif ("taskFlushed" in response):
            taskInfo = response.split()
            self.contextSwitchResponse(taskInfo[1:])
        elif ("computeCapacity" in response):
            self.computeCapacityResponse((int)(response.split()[1]))
        elif ("memoryAvailable" in response):
            self.memoryResponse((int)(response.split()[1]))
        elif ("numTasks" in response):
            self.numTasksResponse((int)(response.split()[1]))
        elif ("currentIDs" in response):
            self.currentTasksResponse(([(int)(i) for i in response.split()[1:]]))
        elif ("movedTask" in response):
            taskInfo = response.split(":")[1]
            details = taskInfo.split()
            taskID = (int)(details[0])
            destination = (details[2])
            originalVal = self.pendingTasksCopy[taskID]
            originalVal['proc'] = destination
            self.pendingTasks[taskID] = originalVal
        elif ("Done" in response):
            self.doneResponse("done")

    def empty_queue(self, driver_name):
        self.writer.write_to_stream(driver_name+";emptyQueue")

    def move_task(self, driver_name, taskID, destination):
        self.writer.write_to_stream(driver_name+";moveTask;"+(str)(taskID)+";"+destination)

    def add_task(self, driver_name, durationMs, memoryMb, computeUnits, taskId):
        self.taskCount.value += 1
        taskInfo = [driver_name, durationMs, memoryMb, computeUnits, taskId]
        self.writer.write_to_stream(taskInfo[0]+";addTask;"+";".join(taskInfo[1:]))
        #self.tasks.append([driver_name, durationMs, memoryMb, computeUnits, taskId]);

    def contextSwitch(self, driver_name, taskID, callback):
        self.contextSwitchResponse = callback
        self.writer.write_to_stream(driver_name+";contextSwitch;"+(str)(taskID))

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
        self.start_time = time.time()

def util(x):
    print (x)

def test_simple():

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

    tGraph = staticSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    taskSchedule = staticSchedule.staticSchedule(tGraph, computeCost)

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier()
    # lambda x: (x%2 == 0)
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

    #for i in bk:
    #    i.join()
    time.sleep(100)
    return q.duration.value


def test_rr():

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

    tGraph = rrSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    taskSchedule = rrSchedule.rrSchedule(tGraph, computeCost)

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier()
    # lambda x: (x%2 == 0)
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

    #for i in bk:
    #    i.join()
    time.sleep(100)
    return q.duration.value

def test_dynamic():
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

    tGraph = staticSchedule.taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    taskSchedule = staticSchedule.staticSchedule(tGraph, computeCost)

    drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ]

    for i in range(numProcs):
        drivers.append((chr(ord('a') + i), 100, 50, 10000, 0))

    q = Querier(computeCost, tGraph, len(drivers))
    # lambda x: (x%2 == 0)
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

    #for i in bk:
    #    i.join()
    time.sleep(100)
    return q.duration.value



def main():
    if len(sys.argv) < 2:
        print("Please Enter name of the test to run")
    else:
        global scheduler
        scheduler = sys.argv[1]

        if sys.argv[1] == 'simple':
            print (test_simple())
        elif sys.argv[1] == 'rr':
            print (test_rr())
        elif sys.argv[1] == 'dynamic':
            print (test_dynamic())



if __name__ == '__main__':
    main()
