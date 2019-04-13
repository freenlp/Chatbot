#coding:utf-8
from multiprocessing import Process, Queue
import os, time, random, sys
from pyqtChatApp import PyqtChatApp
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def chat_qa(q):
    app = QApplication(sys.argv)
    pchat = PyqtChatApp(q)
    pchat.show()
    sys.exit(app.exec_())


def render_3d(q):
    while True:
        if not q.empty():
            value = q.get(True)
            print('Get %s from queue...' % value)
            print('process 3d')
            time.sleep(random.random())
        else:
            print('process 3d no message')
            time.sleep(random.random())


if __name__ == '__main__':
    print('start...')
    q = Queue()
    # 父进程的queue传递给子进程
    pw = Process(target=chat_qa, args=(q,))
    pr = Process(target=render_3d, args=(q,))

    # chat interface qa start
    pw.start()
    # 3d start
    pr.start()

    pw.join()
    if not pw.is_alive():
        pr.terminate()
    print('done...')
