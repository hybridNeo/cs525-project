from fifo import FifoListener, FifoWriter
class Handle():
    def handler(str):
        print(str)

    def __init__(self, filename):
        def handler(str):
            print(str)
        self.filename = filename
        self.writer = FifoWriter('req_' + filename)
        self.reader = FifoListener('resp_' + filename, handler)

    async def start(self):
        await self.reader.listen()

    async def write(self,content):
        self.writer.write_to_stream(content)

class DriverController():

    def __init__(self, dlist):
        self.handles = {}
        self.server = FifoListener('server_req',self.handler)
        self.responder = FifoWriter('server_resp')
        for i in dlist:
            self.handles[i] = Handle(i)


    def handler(self, inp):
        a,b = inp.split(';')
        self.handles[i].write(b)

    async def listen(self):
        print('Started DC')
        for i in self.handles:
            await self.handles[i].start()
        await server.listen()

    def bad_handle(self,a,b):
        self.handles[a].write(b)

