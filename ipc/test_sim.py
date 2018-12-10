import asyncio
from driver_sim import Driver
from drivercontroller import DriverController, Handle
from fifo import FifoListener, FifoWriter
from multiprocessing import Process, Value
import sys

import time

drivers = [
        # (Driver name, memory Size, compute Capacity, Memory transfer speed, contextSwitchPenalty)
        ('a', 100, 50, 10, 0),
        ('b', 50, 100, 50, 2)
        ]

def start_drivers():
    d = []
    for i in drivers:
        d.append(Driver(*i))

    res = []
    for i in d:
        res.append(Process(target = i.start))

    return res

class Querier():
    def __init__(self):
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
        self.taskCount = Value("i", 0)


    def handler(self, response):
        print("[Querier] got response :" , response)
        if ("Finished task " in response):
            self.finished_jobs += 1
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
        elif ("Done" in response):
            self.doneResponse("done")

        if(self.finished_jobs == self.taskCount.value):
            print("[Querier] Test Completed : " ,time.time() - self.start_time)

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
    q = Querier()
    # lambda x: (x%2 == 0)
    m = start_drivers()

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    for i in bk:
        i.start()
    q_process = Process(target = q.querier)
    q_process.start()

    #import time
    #time.sleep(1)
    q.add_task("a", "1000", "10", "10", "1")
    q.add_task("b", "1000", "10", "10", "2")
    q.computeCapacityAvailable("a", util)
    q.memoryAvailable("b", util)
    q.getNumTasksInQueue("a", util)
    q.getCurrentTaskIDs("b", util)
    q.returnWhenDone("a", util)
    q.returnWhenDone("b", lambda x : print("b finished"))

    #for i in bk:
    #    i.join()
    time.sleep(50)


def main():
    if len(sys.argv) < 2:
        print("Please Enter name of the test to run")
    else:
        if sys.argv[1] == 'simple':
            test_simple()



if __name__ == '__main__':
    main()
