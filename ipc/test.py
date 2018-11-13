import asyncio
from driver import Driver
from drivercontroller import DriverController, Handle


drivers = ['a','b']
def start_drivers(loop):
    d = []
    for i in drivers:
        d.append(Driver(i))

    res = []
    for i in d:
        res.append(loop.create_task(i.start()))

    return res


async def main():
    m = start_drivers(loop)
    dc = DriverController(drivers)
    bk = [loop.create_task(dc.begin())]
    for i in m:
        bk.append(i)
    await asyncio.wait(bk)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
