from pype import Controller
from pype import RuntimeObject as RO
from datetime import datetime
from pype import Controller
import time
import shutil
def know_task_1(ctl):
    ctl.RWC(run=lambda x:time.sleep(1.))
    ctl.RWC(run='touch task1')
    ctl.RWC(run='echo done:task1')


def know_task_2(ctl):
    ctl.RWC(run=lambda x:time.sleep(1.))
    ctl.RWC(run='touch task2')
    ctl.RWC(run='echo CWD: {_CWD}')
    ctl.RWC(run='echo PWD: $PWD')
    ctl.RWC(run='echo done:task2')

t1 = Controller.from_func(know_task_1)
t2 = Controller.from_func(know_task_2)

from pprint import pprint 
import os,sys

from threading import Thread

def test_thread_safe():
    if os.path.exists('./build'):
        shutil.rmtree('./build')
    t1t = Thread( target=t1.build,args=(('./build/test-1/',)),daemon=True)
    t2t = Thread( target=t2.build,args=(('./build/test-2/',)),daemon=True)

    t1t.start()
    t2t.start()

    # t1.build('./build/test-1/')

    t1t.join(2.)
    t2t.join(2.)
    # t1t.stop()
    # t2t.stop()

    ret = [os.listdir('build/'),
    # ret = 
    os.listdir('build/test-1/'),
    os.listdir('build/test-2/'),]

    # ret = os.listdir('build/test-2/')
    pprint(ret)
    assert 'task1' in ret[1]
    assert 'task2' in ret[2]

if __name__== '__main__':
    test_thread_safe()
