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

    async def start():
        await reader.listen()

    async def write(content):
        writer.write(content)

class DriverController():

    def __init__(self, dlist):
        self.handles = {}
        self.server = FifoListener('server',self.handler)
        self.responder = FifoWriter('server')
        for i in dlist:
            self.handles[i] = Handle(i)


    def handler(inp):
        a,b = inp.split(';')
        handles[i].write(b)

    async def listen(self):
        for i in self.handles:
            await i.listen()
        await server.listen()

    def bad_handle(self,a,b):
        self.handles[a].write(b)

