import asyncio
from driver import Driver
from drivercontroller import DriverController, Handle
from fifo import FifoListener, FifoWriter

drivers = ['a','b']
def start_drivers(loop):
    d = []
    for i in drivers:
        d.append(Driver(i))

    res = []
    for i in d:
        res.append(loop.create_task(i.start()))

    return res

class Querier():
    def __init__(self):
        print('In ctr')
        self.writer = FifoWriter('server_req')

    def handler(str):
        print(str)

    async def querier(self):
        print('In querier')
        #await asyncio.sleep(2)
        # self.writer.write_to_stream('a;Helo')
        # r = FifoReader('server_resp', handler)
        print('Eneded')
        await r.listen()

async def main():
    q = Querier()
    m = start_drivers(loop)
    dc = DriverController(drivers)
    bk = [loop.create_task(q.querier()),loop.create_task(dc.listen())]

    for i in m:
        bk.append(i)
    print(bk)
    await asyncio.wait(bk)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())
    loop.close()
