from fifo import FifoListener
from multiprocessing import Process
import asyncio
import os

def handler(str):
    print(str)

def test():
    print('In test')
    try:
        os.mkfifo('test')
    except:
        print("[test] FileExists")

    fd = open('test', 'w')
    print('[test] opened file')
    print('opened')
    fd.write('Test')

def main():
    print('In main')
    listener = FifoListener("test", handler)

    a = Process(target=listener.listen)
    a.start()
    b = Process(target=test)
    b.start()
    print('here 2 ')
    bk = [a,b]
    print('here 3')

    for i in bk:
        i.join()

if __name__ == '__main__':
    main()
