from fifo import FifoListener
import asyncio

def handler(str):
    print(str)

def main():
    print('In main')
    loop = asyncio.get_event_loop()
    listener = FifoListener("test", handler)
    loop.run_until_complete(listener.listen())

if __name__ == '__main__':
    main()
