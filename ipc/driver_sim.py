from fifo import FifoListener, FifoWriter
import subprocess

import asyncio

class Driver():

    def __init__(self, driver_name, memory_size, compute_size, memory_speed, context_switch_penalty, performanceVariance):
        self.driver_name = driver_name
        self.memory_size = (str)(memory_size)
        self.compute_size = (str)(compute_size)
        self.memory_speed = (str)(memory_speed)
        self.performanceVariance = (str)(performanceVariance)
        self.context_switch_penalty = (str)(context_switch_penalty)
        #self.listener = FifoListener('req_' + driver_name, self.def_handler)
        #self.writer = FifoWriter('resp_' + driver_name)

    #def def_handler(self, response):
    #    pass
    #    self.writer.write_to_stream(response)

    def start(self):
        print('[DRIVER_SIMULATOR {}] Starting'.format(self.driver_name))
        subprocess.Popen(["./simulator", self.driver_name, self.memory_size, self.compute_size, self.memory_speed, self.performanceVariance, self.context_switch_penalty])
        #self.listener.listen()


