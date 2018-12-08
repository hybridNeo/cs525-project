from fifo import FifoListener, FifoWriter
import asyncio

class Driver():

    def __init__(self,driver_name):
        self.driver_name = driver_name
        self.listener = FifoListener('req_' + driver_name, self.def_handler)
        self.writer = FifoWriter('resp_' + driver_name)

    def def_handler(self, str):
        self.writer.write_to_stream(str.lower())

    def start(self):
        print('Started driver' + self.driver_name)
        self.listener.listen()


