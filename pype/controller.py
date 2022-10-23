
import urllib.request
import os
import shutil
import subprocess
import sys
import toml
import importlib.util
from pprint import pprint
import time

SEXE = sys.executable
from collections import OrderedDict,namedtuple
def s(cmd,shell=True,raw=False):
    ret= subprocess.check_output(cmd,shell=shell,executable='/bin/bash')
    if not raw:
        ret = ret.decode()
    return ret

def is_root():
    return (os.geteuid() == 0)

def test_is_root():
    if not is_root():
        sys.exit("[Exit]:You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    return



def check_done_file_1(fn,):
    if os.path.exists(fn) and toml.loads(open(fn).read())['DONE']==1:
        return True
    else:
        return False
def write_done_file_1(fn):
    with open(fn,'w') as f:
        f.write(toml.dumps(dict(DONE=1)))

check_write_1 = check_done_file_1, write_done_file_1
DefaultWriter = (lambda cctx:1)
DefaultChecker = (lambda cctx:False)
check_write_always= (DefaultChecker, DefaultWriter)
check_write_2 = (lambda cctx:os.path.exists(cctx)), DefaultWriter
check_write_single_target = check_write_2

def is_pypack_installed(package_name_list,):
	# package_name = 'pandas'
	ret = True
	for package_name in package_name_list:
		spec = importlib.util.find_spec(package_name)
		ret = ret & (spec is not None)
	return ret
check_write_pypack = (is_pypack_installed, DefaultWriter)

def sjoin(x,sep=' '):
    return sep.join(x)



def IdentityCaller(x):
    return x
RuntimeRoot = object()
class RuntimeObject(object):
    def __new__(cls, callee, caller=None):
    # def __init__(self, callee,caller):

        if callable(caller):
            pass
        elif isinstance(caller,str):
            # print(f'[RO.caller]{repr(caller)}')
            # caller = lambda x,caller=caller:[print('[RO.str]',caller,),caller.format(**x)][-1]
            caller = lambda x,caller=caller:[None,caller.format(**x)][-1]
        elif caller is None:
            caller = IdentityCaller
        else:
            raise NotImplementedError(repr(type(caller)))

        self = super().__new__(cls)
        self.callee = callee
        self.caller = caller
        return self

    def call(self,i=0):
        callee = self.callee
        caller = self.caller
        i = i+1
        value = None

        print(f'[RO.call,1] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')
        if isinstance(callee, RuntimeObject):
            callee = callee.call(i)
        print(f'[RO.call,2] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')

        value = caller(callee)
        print(f'[RO.call,3] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')
        # ,caller,callee,value)
        return value

    def __getitem__(self,key):
        # return RuntimeObject
        caller = (lambda x,key=key: x.__getitem__(key))
        return RuntimeObject(self, caller)

RO = RuntimeObject

ControllerNode = namedtuple('ControllerNode','control check_ctx run ctx name built')
NotInitObject = object()
class Controller(object):
    def __init__(self):
        self.state = OrderedDict()
        self.stats = {}
        self._runtime = {}
        self.runtime = RO(self._runtime)
        # self.runtime = (self._runtime)
        # self._buildtime = {}

    def __getitem__(self,k):
        return self.state.__getitem__(k)
        #[k]

    def run_node_with_control(self, control, check_ctx, run, ctx=None,name = None,built=None):
        t0 = time.time()
        # self.state[]
        check, write = control



        print(f'[RNWC.name]{name}')
        '''ctx could be delayed evaled if check failed'''

        print('check_ctx')
        check_ctx = RuntimeObject(check_ctx).call()
        print('ctx')
        ctx = RuntimeObject(ctx).call()
        print('run')
        run = RuntimeObject(run).call()
        for k in 'run check_ctx ctx'.split():
            print(k)
            # v = eval(k)
            # if not isinstance(v,RuntimeObject):
            #     v = RuntimeObject(v)
            # # v = v.call()
            # exec(f'{k}=v.call()')
            # exec(f'{k}=RuntimeObject({k}).call()')
            v = locals()[k]
            assert not isinstance(v, RuntimeObject),(k,v.caller,v.callee)
        '''
        if the passed is a string, then consider a command to be filled
        at runtime.
        '''
        if isinstance(run, str):
            cmd = run.format(**ctx)
            run = sc(cmd)


        if check(check_ctx, ):
            print(f'[SKIP]{repr(run)}({repr(ctx)})')
        else:
            print(f'[RUNN]{repr(run)}({repr(ctx)})')

            run(ctx)
            write(check_ctx, )

        t1 = time.time()
        k = repr(run)[:30]
        dt = t1-t0
        self.stats[k] = (k, int(dt*10**3), int(dt *10**6) % 1000)


    def pprint_stats(self):
        pprint(self.stats)
    @property
    def nodes(self):
        return self.state
    # def buildtime(self):
    #     return RO(self._buildtime)
    def register_node(self, control=check_write_always,
        check_ctx=None, run=None, ctx=NotInitObject, name = None, run_now = False, built=None):
        '''
        ctx defaults to Controller.runtime if not specified
        '''
        if ctx is NotInitObject:
            # ctx = RO(self.__dict__)['runtime']
            ctx = self.runtime
            # ctx = RO(self.__dict__, lambda x:x['runtime'])
            # ['runtime']

        assert run is not None, 'Must specify "run"'
        if name is None:
            name = '_defaul_key_%d'%(self.state.__len__())
        self.state[name]= node = ControllerNode(control, check_ctx, run, ctx, name, built)
        if run_now:
            self.run_node_with_control(*node)
    # RWC = run_node_with_control
    RWC = register_node

    def run(self, runtime= None):
        if runtime is None:
            runtime = {}
        self._runtime.update(runtime)
        rets = []
        for k,v in self.state.items():
            self.run_node_with_control(*v)
#            rets.append( v())
        return rets

    def build(self,*a,**kw):
        return self.run(*a,**kw)

    def lazy_wget(self, url,):
        # print(type(url))
        # assert not isinstance(url,RO),RO
        url = RO(url)
        target = RO(url, os.path.basename)
        def _lazy_wget(ctx,url=url):
            url = url.call()
            target = target.call()
            ret = urllib.request.urlretrieve(url, target+'.temp',)
            shutil.move(target+'.temp',target)

        return self.register_node(check_write_2, check_ctx=target, run=_lazy_wget)

    def lazy_apt_install(self, PACK):
        if not isinstance(PACK,(list,tuple)):
            PACK = PACK.split()


        ret = s(f'dpkg -s {sjoin(PACK)} | grep Package:').splitlines()
        # ret = s(f'''apt list --installed {sjoin(PACK)}''').splitlines()
        if len(ret) >= len(PACK):
            print(f'[SKIP]lazy_apt_install({PACK})')
        else:
#            test_is_root()
            s(f'''{"sudo" if not is_root() else ''} apt install -y {sjoin(PACK)}''')
        return

ctrl = Controller()
# RWC = ctrl.run_node_with_control
run_node_with_control = ctrl.run_node_with_control
RWC = run_node_with_control

class ShellCaller(object):
    def __init__(self,cmd):
        if 'set -e' not in cmd:
            cmd = 'set -e; ' + cmd
        self.cmd = cmd
    def __repr__(self):
        return f'ShellCaller(cmd="{self.cmd[:30]}")'
    def __call__(self,ctx=None):
        return s(self.cmd)


sc = ShellCaller
