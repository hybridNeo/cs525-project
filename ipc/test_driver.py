from driver import Driver
from multiprocessing import Process
from fifo import FifoListener, FifoWriter
import asyncio
import os

def handler(str):
    print('[test] output from driver is ' + str)



def test_listener():
    t_listener = FifoListener('resp_test', handler)
    t_listener.listen()


def test():
    try:
        os.mkfifo('req_test')
    except:
        print("[test] FileExists")

    fd = open('req_test', 'w')
    print('[test] opened file')
    fd.write('Test')
    print('[test] wrote to file')

def main():
    print('In main')
    driver = Driver("test")

    a = Process(target=driver.start)
    a.start()
    b = Process(target=test)
    b.start()
    c = Process(target=test_listener)
    c.start()
    bk = [a,b,c]

    for i in bk:
        i.join()

if __name__ == '__main__':
    main()
