
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
    if 'set -e' not in cmd:
        cmd = 'set -e; ' + cmd
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

'''
https://stackoverflow.com/a/1140513/8083313
'''
def DFRAME(frame):
    frame = FRAME(2) if frame is None else frame
    return frame
def FRAME( back = 0 ):
    return sys._getframe( back + 1 )
def LINE( back = 0 ):
    return sys._getframe( back + 1 ).f_lineno
def FILE( back = 0 ):
   return sys._getframe( back + 1 ).f_code.co_filename
def FUNC( back = 0):
    return sys._getframe( back + 1 ).f_code.co_name
def WHERE( back = 0 ):
   frame = sys._getframe( back + 1 )
   return "%s/%s %s()" % ( os.path.basename( frame.f_code.co_filename ), 
                           frame.f_lineno, frame.f_code.co_name )



def IdentityCaller(x):
    return x
RuntimeRoot = object()
THIS = object()
from functools import partial
import operator
import inspect,traceback
class InnerException(Exception):
    pass
class NonConcreteValueError(RuntimeError):
    pass
# def FORMAT(x):
#     return lambda y,x=x:x.format(**y)
class RuntimeObject(object):
    '''
    Bind caller to callee and delay the evaluation
    [TBC] adding lineno where binding happened for debugging
    '''
    def __new__(cls, callee, caller=None, frame= None):

        if callable(caller):
            pass
        elif isinstance(caller,str):
            # caller = caller.format
            # caller = FORMAT(caller)
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
        self.frame  = DFRAME(frame)
        self.lineno = int(self.frame.f_lineno)
        self.stack  = []
        # self.frame  = FRAME(1)
        return self

    def start_pdb(self):
        def _f(*args,__self=self,**kw):
            self=__self
            pcs = self.print_call_stack
            pcs()
            import pdb; pdb.set_trace()
        return self.chain_with(_f, _frame=FRAME(1))




    def chain_with(self, other, *a,_frame=None,**kw):
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

        return RuntimeObject(self, caller, frame = DFRAME(_frame))

    def __call__(self, stack = None):
        return self.call(stack)
    def print_call_stack(self, stack = None,header='Evaltime traceback:'):
        if stack is None:
            stack = self.stack[::-1]
            if not len(stack):
                raise Exception('Stack not specified yet!')
        # pprint(stack)
        eprint('-'*30)
        # eprint(inspect.stack().__len__())
        eprint(header)                        
        print_tb_frames(stack)
        return 

    @property
    def stackele(self):
        return (self.frame, self.lineno)

    def call(self, stack=None, strict=True):        
        '''
        Strict mode does not allow chaining mulitple runtime chain.
        A single call message must echo concrete values.
        
        running in strict mode promise the result of .call()
        would be concrete values, where nostrict mode does not 
        '''
        
        # frame = DFRAME(frame)
        callee = self.callee
        caller = self.caller
        value = None

        if stack is None:
            stack = []
            # print('[init.stack]')
        # print('[appending to stack]')
        # pprint(
        #     (FRAME(1),
        #     self.caller.__name__,
        #     self.frame.f_code.co_filename,
        #     self.lineno))
        #     # {FRAME(1)},{self.frame}')
        self.stack = stack
        stacknew = stack + [(self.frame, self.lineno)]
        if isinstance(callee, RuntimeObject):
            callee = callee.call(stacknew, strict)
            
        try:
            # print_tb_frames([(self.frame, self.lineno)])
            value = caller(callee)
            
            '''
            the result of calling may also be a delayed value.
            But this is a bit advanced and I am not sure  how to manage this 
            signal yet. This is usually indicative of a broken calltree
            '''
            # if isinstance(value, RuntimeObject):
            #     value = value.call(stacknew,strict)
            if strict and isinstance(value, RuntimeObject):                
                value.print_call_stack([value.stackele],header=f'Result of call is still an RO empty placeholder. ')
                raise NonConcreteValueError(f'Must NOT return RuntimeObject {value}')
                # assert not isinstance(value, RO), f'Must NOT return RuntimeObject {value}'
            # self.stack = stack

            '''
            [TBC] echoing back the value. maybe 
            '''
            return value            
        except Exception as e:
            self.stack = stacknew
            # if isinstance(e,InnerException):
            #     pass
            # else:
            # print(f'[L]{len(stack)}')
            self.print_call_stack()            
            eprint('-'*30)
            raise e




    def strip(self,): return RO(self, (lambda x:x.strip()))

    def __getitem__(self,key):
        frame = FRAME(1)
        caller = (lambda x,key=key: x.__getitem__(RO(key,None, frame)() ) )
        return RuntimeObject(self, caller, frame)

    def __lt__(self,b):
        frame = FRAME(1)
        caller = lambda x: x.__lt__(RO(b,None,frame)())
        return RuntimeObject(self, caller,frame)

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


# import traceback as tb
# import traceback
from traceback import *
from traceback import print_list,linecache,FrameSummary
# from traceback import StackSummary
# import linecache
class MyStackSummary(StackSummary):
    """A stack of frames."""
    @classmethod
    def extract_from_codes(klass, co_gen, *, limit=None, lookup_lines=False,
            capture_locals=False):
        """Create a StackSummary from a traceback or stack object.

        :param frame_gen: A generator that yields (frame, lineno) tuples to
            include in the stack.
        :param limit: None to include all frames or the number of frames to
            include.
        :param lookup_lines: If True, lookup lines for each frame immediately,
            otherwise lookup is deferred until the frame is rendered.
        :param capture_locals: If True, the local variables from each frame will
            be captured as object representations into the FrameSummary.
        """
        frame_gen = co_gen
        assert lookup_lines is False
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', None)
            if limit is not None and limit < 0:
                limit = 0
        if limit is not None:
            if limit >= 0:
                frame_gen = itertools.islice(frame_gen, limit)
            else:
                frame_gen = collections.deque(frame_gen, maxlen=-limit)

        result = klass()
        fnames = set()
        # for f, lineno in frame_gen:
        for co in frame_gen:
            lineno = co.co_firstlineno
            filename = co.co_filename
            name = co.co_name
            f_locals = {}
            f_globals = {}
            fnames.add(filename)
            linecache.lazycache(filename, f_globals)
            # Must defer line lookups until we have called checkcache.
            result.append(FrameSummary(
                filename, lineno, name, lookup_line=False, locals=f_locals))
        for filename in fnames:
            linecache.checkcache(filename)
        # If immediate lookup was desired, trigger lookups now.
        if lookup_lines:
            for f in result:
                f.line
        return result
    
def print_tb_codes(codes,limit=None,file=None):
    return print_list(MyStackSummary.extract_from_codes(codes,limit=limit), file=file)
def print_tb_frames(frame_gen,limit=None,file=None):
    return print_list( StackSummary.extract(frame_gen, limit=limit), file=file)



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
ControllerNode = namedtuple('ControllerNode','control check_ctx run ctx name built stack_ele')
NotInitObject = object()



class PipeDupPrototype(object):    
    def __init__(self, file):
        self.file = file 
        # print(sys, self.key, self)
        setattr(sys, self.key, self)

    def reset(self):
        setattr(sys, self.key, self.real)
        self.file.close()

    def write(self, message):
        self.real.write(message)
        self.file.write(message)  

    def flush(self,):
        self.real.flush()
        self.file.flush()

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.reset()
    def read(self,*args):
        return self.file.read(*args)
    def seek(self,*args):
        return self.file.seek(*args)

class StderrDup(PipeDupPrototype):
    real = sys.stderr
    key = 'stderr'

class StdoutDup(PipeDupPrototype):
    real = sys.stdout
    key = 'stdout'

from pydantic import BaseModel,Extra
from typing import Dict,List
from pydantic_yaml import YamlModelMixin
# from pydantic_yaml import ?YamlModel,YamlModelMixin
import yaml
class YamlModel(YamlModelMixin, BaseModel):
    pass
class PypeExecResult(YamlModel,extra=Extra.forbid):
    name: str
    co_name: str
    skipped: int
    run_ms: int
    file: str
    lineno: int
    source: List[str]
    stdout: List[str]
    stderr: List[str]

class PypeExecResultList(YamlModel,extra=Extra.forbid):
    data: List[PypeExecResult]
    # def __getitem__(self,key)
    # def get(self,key,default=)
    @property
    def datadict(self):
        v = {v.name: v for v in self.data}
        return v

import re
from inspect import getsourcefile,linecache,getfile
def get_frame_lineno(frame,lineno,strip=True):
    object = frame
    file = getsourcefile(object)
    if file:
        # Invalidate cache if needed.
        linecache.checkcache(file)
    else:
        file = getfile(object)
        # Allow filenames in form of "<something>" to pass through.
        # `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        if not (file.startswith('<') and file.endswith('>')):
            raise OSError('source code not available')
    lines = linecache.getlines(file)
    # if not hasattr(object, 'co_firstlineno'):
    #     raise OSError('could not find function definition')
    # lnum = object.co_firstlineno - 1
    lnum = lineno - 1
    # pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
    pat = re.compile(r'^(.*ctl\..*\()|^(.*RWC\()')
    lnum0 = lnum
    while lnum > 0:
        # print(repr(lines[lnum]))
        if pat.match(lines[lnum]): break
        lnum = lnum - 1
    ret = lines[lnum:lnum0+1]
    if strip:
        ret = [x.rstrip() for x in ret]
    return ret
    # return lines, lnum

NULL = object()
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

    def run_node_with_control(self, control, check_ctx, run, runtime=None,name = None,built=None, stack_ele=None,frame=None):
        '''
        control: (checker, writer)
        checker:
          decide whether the function needs to be run
        writer: 
          bookkeeping function to satisfy control. 
          not much different from run 
        run: payload to run if checker failed
        runtime:
          default to runtime.
        name:
          name of node run
        built:
          meta information once built
        '''
        t0 = time.time()

        frame=DFRAME(frame)
        check, write = control
        if check is None:
            check = DefaultChecker
        if write is None:
            write = DefaultWriter
        

        '''ctx could be delayed evaled if check failed'''

        runtime   = RuntimeObject(runtime, None, frame).call()
        check_ctx = RuntimeObject(check_ctx, None, frame).call()

        if isinstance(run, str):
            '''
            if the passed is a string, consider a command to be filled
            at runtime.
            '''
            # RO(run,)
            # run = lambda ctx,run=run: s(run.format(**ctx))
            tocall = RO(runtime, lambda x,run=run:run.format(**x))
            tocall = tocall.chain_with(s)
        else:
            run = RuntimeObject(run, None, frame).call()
            tocall = RO(runtime, run)


        if self._use_pdb:
            import pdb;pdb.set_trace()


        def msg(head):
            f,lineno = stack_ele
            co = f.f_code
            eprint('')
            eprint(f'{head}(name={name!r}, code {co.co_name!r}, file={co.co_filename!r}, line {lineno!r})')
            print_tb_frames([stack_ele])

        msg('[BULD]')
        eprint('[CHCK]',end='')
        check = RuntimeObject(check).call()
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
            
            # print(f'[SKIP]({name},{co.co_name},)')
            # print(f'[SKIP]({name},{stack_ele})')
            # msg('[SKIP]')
            eprint('[SKIP]')
        else:
            eprint('[RUNN]')
            # msg('[RUNN]')
            # print(f'[RUNN]({name},{stack_ele})')
            # run(runtime)
            tocall.call()
            write(check_ctx, )

        t1 = time.time()
        k = repr(run)[:30]
        dt = t1-t0
        self.stats[k] = (k, int(dt*10**3), int(dt *10**6) % 1000)
        return checked

        '''
        [return-value?]
        is affected by check()
        '''
    def pprint_stats(self):
        pprint(self.stats)

    @property
    def nodes(self):
        return self.state

    @property
    def runtime_setter(self):
        return self._runtime


    def register_node(self, control=check_write_always,
        check_ctx=None, run=None, ctx=NotInitObject, name = None, run_now = False, built=None, frame=None):
        '''
        ctx defaults to Controller.runtime if not specified
        frame: 
          the frame would be used to format traceback.
          if calling RWC within some function, better to pass down calling context 
          to level the traceback


        '''
        frame = DFRAME(frame)
        stack_ele = (frame,int(frame.f_lineno))
        if ctx is NotInitObject:

            #### this does not work yet
            #### the getted value is returned directly
            #### the caller
            #### the callee is evaluated before apply to caller

            # ctx = RO(self.__dict__)['runtime']
            # ctx = RO(self._runtime)
            ctx = self.runtime
            # ctx = self.runtime
            # ctx = RO(self.__dict__, lambda x:x['runtime'])
            # ['runtime']

        assert run is not None, 'Must specify "run"'
        if name is None:
            name = '_defaul_key_%d'%(self.state.__len__())
        self.state[name]= node = ControllerNode(control, check_ctx, run, ctx, name, built, stack_ele)
        if run_now:
            '''
            
            '''
            self.run_node_with_control(*node)
        return node
    # RWC = run_node_with_control
    RWC = register_node
    def run(self, runtime= None,rundir=None, metabase=None):
        '''
        return: a list indicates whether each step is skipped or executed

        stdout redirecting?


        '''
        if runtime is None:
            runtime = {}
        self._runtime.update(runtime)
        rets = []



        if rundir is None:
            rundir = os.getcwd()

        if os.path.isfile(rundir):
            meta_file = rundir
        else: 
            if metabase is None:
                metabase = 'PYPE.yaml'
            meta_file = rundir +'/' +metabase
            
        meta = PypeExecResultList(data=[])
        try:            
            buf = ''
            with open(meta_file,'r') as f:
                buf = f.read()
            meta = PypeExecResultList.parse_raw(buf)            
        except Exception as e:
            eprint(f'[Controller.run] Unable to load metafile:{meta_file} {e}')

        for k,v in self.state.items():
            out = StdoutDup(io.StringIO())
            err = StderrDup(io.StringIO())
            v
            t0 = time.time()
            checked = self.run_node_with_control(*v)
            dt = time.time()-t0
            dtms = int(dt*1000)
            out.seek(0)
            err.seek(0)
            disknode = meta.datadict.get(k,None)
            run_ms = None
            if disknode is not None:
                run_ms = disknode.run_ms
            else:
                run_ms = dtms
            co  = v.stack_ele[0].f_code
            ret = PypeExecResult(
                 name   = v.name,
                 co_name= co.co_name,
                 skipped= 1 - int(checked),
                 run_ms = run_ms,
                 stdout = out.read().splitlines(), 
                 stderr = err.read().splitlines(),
                 file   = os.path.realpath(co.co_filename),
                 lineno = v.stack_ele[1],
                 source = (get_frame_lineno(*v.stack_ele)),
            )
            rets.append(ret)

        rets = PypeExecResultList(data=rets)
        with open(meta_file, 'w') as f:
            f.write(rets.yaml())
            # (rets.dict()))
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
        def _lazy_wget(ctx,url=url,target=target):
            url = url.call()
            target = target.call()
            ret = urllib.request.urlretrieve(url, target+'.temp',)
            shutil.move(target+'.temp',target)

        return self.register_node(
            check_write_2, check_ctx=target, run=_lazy_wget, built=target)

    def lazy_apt_install(self, PACK):
        if not isinstance(PACK,(list,tuple)):
            PACK = PACK.split()
        def checker(x,PACK=PACK):
            with open(os.devnull,'w') as devnull:
                retval = subprocess.call(['dpkg','-s',]+list(PACK), stdout=devnull)
            checked = retval==0
            return checked
        return self.RWC([checker,None],
            run= f'''{"sudo" if not is_root() else ''} apt install -y {sjoin(PACK)}''',
            frame=FRAME(1),
            )

    def lazy_pip_install(self, TARGET_LIST,pre_cmd=''):
        TARGETS = sjoin(TARGET_LIST)
        return self.RWC([is_pypack_installed, None], TARGET_LIST, f'''
        {pre_cmd}
        {SEXE} -m pip install --upgrade {TARGETS}
        ''',built=TARGET_LIST,
        frame=FRAME(1),)

        # frame=FRAME(1))


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
            run = run_git_url_commit(url,commit,target_dir), built=target_dir,name=name,
            frame=FRAME(1),)

ctrl = Controller()
# RWC = ctrl.run_node_with_control
run_node_with_control = ctrl.run_node_with_control
RWC = run_node_with_control

class ShellCaller(object):
    def __init__(self, cmd):
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
            # .chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])
            ==url
        ) &
        (
            RO(None,sc(f'git -C {target_dir} rev-parse HEAD')).strip()
            # .chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])
            ==commit)
        )
        # ).chain_with(lambda x:[print(f'[git]{repr(x)}'),x,][1])

    return caller
