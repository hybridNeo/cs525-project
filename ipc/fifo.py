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
            pass
            # print("FileExistException: the file already exists.")


    def listen(self):
        print ("Initiated listener for", self.filename)

        # print('[' + self.filename + '] In Listen')
        while True:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.listen_helper())

    async def listen_helper(self):
        async def stream_as_generator(loop, stream):
            reader = asyncio.StreamReader(loop=loop)
            reader_protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: reader_protocol, stream)
            while True:
                line = await reader.readline()
                if not line: # EOF
                    break
                print ("In FifoListener, just read from ", self.filename, " got ", line)
                yield line

        fd = open(self.filename )

        loop = asyncio.get_event_loop()
        async for line in stream_as_generator(loop, fd):
            line = line.decode("utf-8").rstrip()
            # print('[' + self.filename + ']' + str(line))
            self.handler(line)

    def clean(self):
        os.remove(self.filename)


class FifoWriter():

    def __init__(self, filename):
        self.filename = filename
        self.writer = None
        try:
            os.mkfifo(filename)
        except Exception as e:
            pass

    def write_to_stream(self, content):
        # print(self.filename)

        try:
            self.writer = open(self.filename, 'w')
        except Exception as e:
            print (e, "while opening", self.filename)
            pass
            # print("FileNotFoundException")
        self.writer.write(content + '\n' )
        print ("In FifoWriter, just wrote to ", self.filename, " got ", content)
        self.writer.close()
