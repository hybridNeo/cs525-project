import asyncio
from driver import Driver
from drivercontroller import DriverController, Handle
from fifo import FifoListener, FifoWriter
from multiprocessing import Process

import time



drivers = [('a',),('b',)]
def start_drivers():
    d = []
    for i in drivers:
        d.append(Driver(i[0]))

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

    def handler(self, str):
        print("[Querier] got response :" , str)
        self.finished_jobs += 1
        if(self.finished_jobs == len(self.tasks)):
            print("[Querier] Test Completed : " ,time.time() - self.start_time)

    def add_task(self, driver_name, func):
        self.tasks.append(driver_name + ';' + func)

    def querier(self):
        r = FifoListener('server_resp', self.handler)
        resp = Process(target = r.listen)
        resp.start()
        #await asyncio.sleep(2)
        self.start_time = time.time()
        for i in self.tasks:
            self.writer.write_to_stream(i)

def main():
    q = Querier()
    q.add_task("a","Helo")
    q.add_task("a","TEST")
    m = start_drivers()

    dc = DriverController(drivers)
    bk = [Process(target = dc.listen)]

    for i in m:
        bk.append(i)
    print(bk)
    for i in bk:
        i.start()
    q_process = Process(target = q.querier)
    q_process.start()

    for i in bk:
        i.join()

if __name__ == '__main__':
    main()
