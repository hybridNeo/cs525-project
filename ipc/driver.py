from fifo import FifoListener, FifoWriter

class Driver():

    def __init__(self,driver_name):
        self.driver_name = driver_name
        self.listener = FifoListener('req_' + driver_name, self.def_handler)
        self.writer = FifoWriter('resp_' + driver_name)

    def def_handler(str):
        self.writer.write(str.lower())

    async def start(self):
        print('Started driver' + self.driver_name)
        await self.listener.listen()


