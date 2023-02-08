from pype import Controller
from pype import RuntimeObject as RO
from datetime import datetime
from pype import Controller
from pype import ShellCaller,ShellRun
import time
import shutil

import tempfile

tempf  = tempfile.mkstemp()
tempfn = tempf[1]

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

def know_task_wget(ctl):
    ctl.RWC(run=lambda x:time.sleep(0.01))
    ctl.lazy_wget(f'file://{tempfn}')



t1 = Controller.from_func(know_task_1)
t2 = Controller.from_func(know_task_2)

from pprint import pprint 
import os,sys

from threading import Thread


def test_wget():
    if os.path.exists('./build'):
        shutil.rmtree('./build')
    Controller.from_func(know_task_wget).build('./build/wget/')
    ret = os.listdir('./build/wget/')
    pprint(ret)
    assert os.path.basename(tempfn) in ret,ret
    # assert 0,ret



def test_git():
    tempgit = tempfile.mkdtemp()
    ShellRun(f'git -C {tempgit} init .')
    ShellRun(f'git -C {tempgit} commit -m cm0 --allow-empty')
    tempgit_hash = ShellRun(f'git -C {tempgit} rev-parse HEAD').strip()
    # assert 0,[tempgit_hash]

    pdr = './build/git/'
    if os.path.exists(pdr):
        shutil.rmtree(pdr)

    def _f(ctl):
        ctl.RWC(run=lambda x:time.sleep(0.01))
        # ctl.lazy_git_url_commit(f'file://{tempgit}','HEAD')
        ctl.lazy_git_url_commit(f'{tempgit}','master', tempgit_hash)

    Controller.from_func(_f).build(pdr)
    ret = os.listdir(pdr)
    pprint(ret)
    assert os.path.basename(tempgit) in ret,ret
    # assert 0,ret


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
