from fifo import FifoListener, FifoWriter
from multiprocessing import Process

class Handle():
    def handler(self, str):
        self.respond(str)

    def __init__(self, filename, responder):
        self.filename = filename
        self.writer = FifoWriter('req_' + filename)
        self.reader = FifoListener('resp_' + filename, self.handler)
        self.responder = responder

    def start(self):
        self.reader.listen()

    def respond(self,content):
        self.responder.write_to_stream(content)

    def write(self,content):
        self.writer.write_to_stream(content)

class DriverController():

    def __init__(self, dlist):
        self.handles = {}
        self.server = FifoListener('server_req',self.handler)
        responder = FifoWriter('server_resp')
        for i in dlist:
            self.handles[i] = Handle(i, responder)


    def handler(self, inp):
        a,b = inp.split(';')
        self.handles[a].write(b)

    def listen(self):
        print('[DRIVER_CONTROLLER]Starting')
        for i in self.handles:
            p = Process(target=self.handles[i].start)
            p.start()
        self.server.listen()

    def bad_handle(self,a,b):
        self.handles[a].write(b)

