
import urllib.request
import os
import shutil
import subprocess
import sys
import toml
import importlib.util
from pprint import pprint
import time
import io
SEXE = sys.executable
from collections import OrderedDict,namedtuple
def s(cmd,shell=True,raw=False):
    ret= subprocess.check_output(cmd,shell=shell,executable='/bin/bash')
    if not raw:
        ret = ret.decode()
    return ret
CWD = os.getcwd

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
THIS = object()
from functools import partial
import operator
class RuntimeObject(object):
    '''
    Bind caller to callee and delay the evaluation
    [TBC] adding lineno where binding happened for debugging
    '''
    def __new__(cls, callee, caller=None):

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

    def chain_with(self, other,*a,**kw):
        # a =
        ct = []
        for k,v in kw.items():
            if v is THIS:
                ct.append((kw.__setitem__,k))
        a = list(a)
        for i,v in enumerate(a):
            if v is THIS:
                ct.append((a.__setitem__,i))
        assert len(ct)<=1, ct
        if not len(ct):
            if not len(a):
                a.append(None)
            ct.append((a.__setitem__, 0))
        setter, k = ct[0]
        def caller(x):
            setter(k,x)
            return other(*a,**kw)

        return RuntimeObject(self, caller)

    def __call__(self):
        return self.call()

    def call(self):
        callee = self.callee
        caller = self.caller
        value = None
        # print(f'[RO.call,1] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')
        if isinstance(callee, RuntimeObject):
            callee = callee.call()
        # print(f'[RO.call,2] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')
        value = caller(callee)
        # print(f'[RO.call,3] i:{i}, caller:{caller}, callee:{repr(callee)[:30]}, value:{repr(value)[:30]}')
        # ,caller,callee,value)
        '''
        the result of calling may also be a delayed value.
        '''
        if isinstance(value, RuntimeObject):
            value = value.call()

        '''
        An intact callchain should not return a runtime object
        '''
        assert not isinstance(value, RO), f'Must NOT return RuntimeObject {value}'
        return value
    def strip(self,): return RO(self, (lambda x:x.strip()))

    def __getitem__(self,key):
        caller = (lambda x,key=key: x.__getitem__(RO(key)() ) )
        return RuntimeObject(self, caller)

    def __lt__(self,b):
        caller = lambda x: x.__lt__(RO(b)())
        return RuntimeObject(self, caller)

    def __le__(self,b):
        caller = lambda x: x.__le__(RO(b)())
        return RuntimeObject(self, caller)

    def __ne__(self,b):
        caller = lambda x: x.__ne__(RO(b)())
        return RuntimeObject(self, caller)

    def __eq__(self,b):
        caller = lambda x: x.__eq__(RO(b)())
        return RuntimeObject(self, caller)

    def __and__(self,b):

        caller = lambda x: x.__and__(RO(b)()) if x else False
        # caller = lambda x:[print(f'[and]{x}'),x.__and__(RO(b)())][1]
        return RuntimeObject(self, caller)

    def __ge__(self,b):
        caller = lambda x: x.__ge__(RO(b)())
        return RuntimeObject(self, caller)

    def __gt__(self,b):
        caller = lambda x: x.__gt__(RO(b)())
        return RuntimeObject(self, caller)


    # def __setitem__(self,key,value):
    #     raise Not

def TransformDummmyRun(*a,**kw):
    '''
    no matter the input, return the dummy runner
    '''
    def func(ctx):
        return ctx
    return func
RO = RuntimeObject

ControllerNode = namedtuple('ControllerNode','control check_ctx run ctx name built')
NotInitObject = object()
class Controller(object):
    def __init__(self):
        self.state = OrderedDict()
        self.stats = {}
        self._runtime = {}
        self.runtime = RO(self._runtime)
        self._use_pdb = 0
        # self.runtime = (self._runtime)
        # self._buildtime = {}
    def use_pdb(self):
        self._use_pdb = 1
    def __getitem__(self,k):
        return self.state.__getitem__(k)

        #[k]

    def run_node_with_control(self, control, check_ctx, run, ctx=None,name = None,built=None):
        t0 = time.time()
        # self.state[]
        check, write = control
        if check is None:
            check = DefaultChecker
        if write is None:
            write = DefaultWriter


        # print(f'[RNWC.name]{name}')
        '''ctx could be delayed evaled if check failed'''

        # print('check_ctx')
        check_ctx = RuntimeObject(check_ctx).call()
        # print('ctx')
        ctx = RuntimeObject(ctx).call()
        # print('run')
        run = RuntimeObject(run).call()
        '''
        if the passed is a string, then consider a command to be filled
        at runtime.
        '''
        if isinstance(run, str):
            cmd = run.format(**ctx)
            run = sc(cmd)

        if self._use_pdb:
            import pdb;pdb.set_trace()

        check = RuntimeObject(check).call()

        # if isinstance(check,callacbkebool):
        #     checked = check
        # else:
        '''
        Dangerous and needs a way to chain to the left?
        '''
        if callable(check):
            checked = check(check_ctx, )
        else:
            checked = check
        ## int is much safer than bool
        checked = int(checked)
        if checked==1:
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

    @property
    def runtime_setter(self):
        return self._runtime


    # def buildtime(self):
    #     return RO(self._buildtime)
    def register_node(self, control=check_write_always,
        check_ctx=None, run=None, ctx=NotInitObject, name = None, run_now = False, built=None):
        '''
        ctx defaults to Controller.runtime if not specified
        '''
        if ctx is NotInitObject:

            #### this does not work yet
            #### the getted value is returned directly
            #### the caller
            #### the callee is evaluated before apply to caller

            ctx = RO(self.__dict__)['runtime']
            # ctx = self.runtime
            # ctx = RO(self.__dict__, lambda x:x['runtime'])
            # ['runtime']

        assert run is not None, 'Must specify "run"'
        if name is None:
            name = '_defaul_key_%d'%(self.state.__len__())
        self.state[name]= node = ControllerNode(control, check_ctx, run, ctx, name, built)
        if run_now:
            self.run_node_with_control(*node)
        return node
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
        '''
        fix cwd at runtime
        '''
        # print(type(url))
        # assert not isinstance(url,RO),RO
        url = RO(url)
        target = RO(url, os.path.basename)
        def _lazy_wget(ctx,url=url):
            url = url.call()
            target = target.call()
            ret = urllib.request.urlretrieve(url, target+'.temp',)
            shutil.move(target+'.temp',target)

        return self.register_node(check_write_2, check_ctx=target, run=_lazy_wget, built=target)

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

    def lazy_pip_install(self, TARGET_LIST,pre_cmd=''):
        TARGETS = sjoin(TARGET_LIST)
        return self.RWC([is_pypack_installed, None], TARGET_LIST, f'''
        {pre_cmd};
        {SEXE} -m pip install --upgrade {TARGETS}
        ''',built=TARGET_LIST)


    def lazy_git_url_commit(self, url, commit, target_dir=None,name=None):
        '''
        fix cwd at runtime
        '''
        # if target_prefix is None:
        #     target_prefix = CWD()
        # target_dir = os.path.join(target_prefix,os.path.basename(url))
        if target_dir is None:
            target_dir = os.path.basename(url)

        return self.RWC(
            [check_git_url_commit(url,commit,target_dir),None],
            run = run_git_url_commit(url,commit,target_dir), built=target_dir,name=name)

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

def PY_DUMP_ENV_TOML(TARGET,is_sorted=True,SEXE=SEXE):
    '''
    depends: python3-toml
    a bash one-liner to dump environment to a toml file.
    :param is_sorted: whether to sort toml keys
    '''
# PY_DUMP_ENV_TOML = lambda TARGET:
    return f'''
{SEXE} <<EOF
import toml,os;
from collections import OrderedDict;
toml.dump(OrderedDict({"sorted" if is_sorted else ''}(dict(os.environ).items())),
open('{TARGET}','w'))
EOF
'''

def run_load_env_from_bash_script(TARGET,keys=None):
    '''
    This runtime object loads the env state
    after running a bash script.
    '''
    return RuntimeObject(f'''
        set -e; set -o allexport; source {TARGET} &>/dev/null;
        {PY_DUMP_ENV_TOML("/dev/stdout")}
        ''', s).chain_with(io.StringIO).chain_with(run_load_toml_env, keys=keys, toml_file=THIS
        ).chain_with(TransformDummmyRun)

# import os
def run_load_toml_env(ctx=None, keys:list=None, toml_file: str=None, os=os):
    '''
    ### loads environ from bash file

    '''
    if isinstance(toml_file,str):

        with open(toml_file,'r') as f:
            buf = f.read()
    else:
            buf = toml_file.read()
    xd = dict(toml.loads(buf))

    # if template is not None:
    # assert template is not None
    # for k,v in
    if keys is None:
        keys = xd
    for k in keys:
        k =k
        os.environ[k] = xd[k]
    # else:
    #     for k in xd

    # for line in template.strip().splitlines():
    #     k = line.split('=',1)
    #     if len(k)!=2:
    #         continue
    #
    #     k =k[0].strip()
    #     if k:
    #         os.environ[k] = xd[k]
def config_extract_keys(template:str):
    '''
    extract keys from a bash-config like file
    split the "=" sign of each line and take the non-empty RHS
    '''
    ret = []
    for line in template.strip().splitlines():
        k = line.split('=',1)
        if len(k)!=2:
            continue

        k =k[0].strip()
        ret.append(k)
    return ret




def run_git_url_commit(url,commit,target_dir):
    # prefix=None,):
    '''
    fetch a commit from a repository
    '''


    caller = sc(f'''
    mkdir -p {target_dir} && cd {target_dir}

    git init .
    git remote add origin {url}

    # fetch a commit (or branch or tag) of interest
    # Note: the full history up to this commit will be retrieved unless
    #       you limit it with '--depth=...' or '--shallow-since=...'

    git fetch origin --depth 1 {commit}
    git reset --hard FETCH_HEAD
    ''')
    return caller

def check_git_url_commit(url,commit,target_dir):
    # prefix=None,):
    '''
    fetch a commit from a repository
    '''

    caller =(
        (
            RO(target_dir, os.path.exists)
        ) &
        (
            RO(None,sc(f'''git -C {target_dir} config --get remote.origin.url''')).strip()
            .chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])
            ==url
        ) &
        (
            RO(None,sc(f'git -C {target_dir} rev-parse HEAD')).strip()
            .chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])
            ==commit)

        ).chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])

    return caller
