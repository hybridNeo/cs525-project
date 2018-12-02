import os
import asyncio


# Listener which asynchronously listens in for commands
# Implemented using linix fifo
class FifoListener():

    def __init__(self, filename, handler):
        self.filename = filename
        self.handler = handler
        try:
            os.mkfifo(filename)
        except:
            print("FileExistException: the file already exists.")


    async def listen(self):
        async def stream_as_generator(loop, stream):
            reader = asyncio.StreamReader(loop=loop)
            reader_protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: reader_protocol, stream)
            while True:
                line = await reader.readline()
                if not line: # EOF
                    break
                yield line
        fd = open(self.filename)
        loop = asyncio.get_event_loop()
        async for line in stream_as_generator(loop, fd):
            print(line)
            handler(line)

    def clean(self):
        os.remove(self.filename)


class FifoWriter():

    def __init__(self, filename):
        self.filename = filename
        try:
            os.mkfifo(filename)
        except:
            pass

    def write_to_stream(self, content):
        print('here')
        try:
            writer = open(self.filename)
        except:
            print("FileNotFoundException")
        writer.write(content)
