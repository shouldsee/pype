
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
from namedlist import namedlist as _namedlist
from namedlist import FACTORY
import collections
from typeguard import typechecked

def namedlist(*args,**kw):
    x = _namedlist(*args,**kw)
    collections.MutableSequence.register(x)
    return x
# from collections import OrderedDict,namedtuple
from ._internals import make_SafeOrderedDict,SafeOrderedDict
from filelock import FileLock
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

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class NonConcreteValueError(RuntimeError):
    pass
# def FORMAT(x):
#     return lambda y,x=x:x.format(**y)
class RuntimeObject(object):
    '''
    Bind caller to callee and delay the evaluation
    [TBC] adding lineno where binding happened for debugging
    '''
    _debug = 0
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
        # import pdb;pdb.set_trace()
        self.filename = os.path.realpath(self.frame.f_code.co_filename)
        self.lineno = int(self.frame.f_lineno)
        self.stack  = []
        # self.frame  = FRAME(1)
        return self

    def start_pdb(self):
        def _f(x,
            _self=self
            ):
            # *args,,**kw):
            self=_self
            pcs = self.print_call_stack
            pcs()
            import pdb; pdb.set_trace()
            return x
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
        for ele in stack:
            assert isinstance(ele,StackElement),ele
        # assert isinstance(stack,List[StackElement])
        # pprint(stack)
        eprint('-'*30)
        # eprint(inspect.stack().__len__())
        eprint(header)       
        # print_tb_stacks(stack)
        print_tb_frames(((x.frame,x.lineno) for x in stack))
        return 

    @property
    def stack_ele(self):
        return StackElement(self.frame,self.filename, self.lineno)

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
        self.stack = stack
        stacknew = stack + [StackElement(self.frame,  self.filename, (self.lineno) )]


        if isinstance(self, RuntimeSideEffect):
            '''
            If performing side effect, than execute
            func when upstreaming, then send signal to upstream.
            '''
            caller(self)

        if isinstance(callee, RuntimeObject):
            callee = callee.call(stacknew, strict)


        try:
            # print_tb_frames([(self.frame, self.lineno)])
            if isinstance(self,RuntimeSideEffect):
                '''
                RSE directly returns upstream value
                '''
                value = callee
            else:
                '''
                RO applys caller to callee
                '''
                value = caller(callee)

            if isinstance(value,dict):
                for k,v in value.items():
                    value[k] = v = RO(v,None,FRAME(1))() 
                    assert not isinstance(v, RO),(RO,v)
                    
            # elif isinstance(value,list):
            elif isinstance(value,collections.MutableSequence):
                for k,v in enumerate(value):
                    value[k] = v = RO(v,None,FRAME(1))() 
                    assert not isinstance(v,RO),(RO,v)
            elif isinstance(value,tuple):
                # if hasattr(value,'_fields'):
                #     value
                '''
                tuple is immutable
                '''
                value = tuple( RO(v,None,FRAME(1))() for k,v in enumerate(value))                    
                for v in value:
                    assert not isinstance(v, RO),(RO,v)
                if type(value)!=tuple:
                    wranings.warn('Putting RuntimeObject in tuple() is not advised since it is immutable ',)
                    self.print_call_stack(stacknew[-1:])
            '''
            the result of calling may also be a delayed value.
            But this is a bit advanced and I am not sure  how to manage this 
            signal yet. This is usually indicative of a broken calltree

            [TBC] if returned a iterable, needs to make sure 
            all elements are Concrete.
            '''
            # if isinstance(value, RuntimeObject):
            #     value = value.call(stacknew,strict)
            if strict and isinstance(value, RuntimeObject):                
                value.print_call_stack([value.stack_ele],header=f'Result of call is still an RO empty placeholder. ')
                raise NonConcreteValueError(f'Must NOT return RuntimeObject {value}')
            if self._debug:
                self.print_call_stack( stacknew,header=f'Result of call is still an RO empty placeholder. ')



            
                                
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
        caller = (lambda x,key=key: x.__getitem__(RO(key,None, frame)() )  )
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
        caller = lambda x: x.__gt__(RO(b,None,FRAME(1))())
        return RuntimeObject(self, caller)

    def __add__(self,b):
        caller = lambda x: x.__add__(RO(b,None,FRAME(1))())
        return RuntimeObject(self, caller,FRAME(1))

    def __getattr__(self,b):
        '''
        [DANGEROUS] with variadic expansion
         Calling func(*RuntimeObject) would hangs your program..        
        '''
        caller = lambda x: x.__getattribute__(RO(b,None,FRAME(1))())
        return RuntimeObject(self, caller,FRAME(1))

    # setattr(self, 'filename', os.path.realpath(self.frame.f_code.co_filename))

    # def __setitem__(self,key,value):
    #     raise Not
class RuntimeSideEffect(RuntimeObject):
    pass

    # def call(self, stack=None, strict=True):        
    #     '''
    #     Strict mode does not allow chaining mulitple runtime chain.
    #     A single call message must echo concrete values.
        
    #     running in strict mode promise the result of .call()
    #     would be concrete values, where nostrict mode does not 
    #     '''
        
    #     # frame = DFRAME(frame)
    #     callee = self.callee
    #     caller = self.caller
    #     value = None

    #     if stack is None:
    #         stack = []
    #         # print('[init.stack]')
    #     self.stack = stack
    #     stacknew = stack + [StackElement(self.frame,  self.filename, (self.lineno) )]

    #     if isinstance(self, RuntimeSideEffect):
    #         '''
    #         If performing side effect, than execute
    #         func when upstreaming
    #         '''
    #         caller(self)


    #     if isinstance(self, RuntimeSideEffect):
    #         '''
    #         If performing side effect, than execute
    #         func when upstreaming
    #         '''
    #         caller(self)

    #     if isinstance(callee, RuntimeObject):
    #         callee = callee.call(stacknew, strict)

    #     return callee


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
from traceback import print_list,FrameSummary
import linecache
# from traceback import StackSummary
# class MyStackSummary(StackSummary):
#     """A stack of frames."""
#     @classmethod
#     def extract_from_codes(klass, co_gen, *, limit=None, lookup_lines=False,
#             capture_locals=False):
#         """Create a StackSummary from a traceback or stack object.

#         :param frame_gen: A generator that yields (frame, lineno) tuples to
#             include in the stack.
#         :param limit: None to include all frames or the number of frames to
#             include.
#         :param lookup_lines: If True, lookup lines for each frame immediately,
#             otherwise lookup is deferred until the frame is rendered.
#         :param capture_locals: If True, the local variables from each frame will
#             be captured as object representations into the FrameSummary.
#         """
#         frame_gen = co_gen
#         assert lookup_lines is False
#         if limit is None:
#             limit = getattr(sys, 'tracebacklimit', None)
#             if limit is not None and limit < 0:
#                 limit = 0
#         if limit is not None:
#             if limit >= 0:
#                 frame_gen = itertools.islice(frame_gen, limit)
#             else:
#                 frame_gen = collections.deque(frame_gen, maxlen=-limit)

#         result = klass()
#         fnames = set()
#         # for f, lineno in frame_gen:
#         for co in frame_gen:
#             lineno = co.co_firstlineno
#             filename = co.co_filename
#             name = co.co_name
#             f_locals = {}
#             f_globals = {}
#             fnames.add(filename)
#             linecache.lazycache(filename, f_globals)
#             # Must defer line lookups until we have called checkcache.
#             result.append(FrameSummary(
#                 filename, lineno, name, lookup_line=False, locals=f_locals))
#         for filename in fnames:
#             linecache.checkcache(filename)
#         # If immediate lookup was desired, trigger lookups now.
#         if lookup_lines:
#             for f in result:
#                 f.line
#         return result
    
# def print_tb_codes(codes,limit=None,file=None):
#     return print_list(MyStackSummary.extract_from_codes(codes,limit=limit), file=file)

import warnings
def print_tb_frames(frame_gen,limit=None,file=None):
    '''
    [DANGEROUS]
    '''
    warnings.warn('[print_tb_frames,StackSummary] is not safe after os.chdir. StackSummary only shows relative path')
    return print_list( StackSummary.extract(frame_gen, limit=limit), file=file)






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

from pydantic import BaseModel,Extra,Field
from typing import Dict,List,Optional
from pydantic_yaml import YamlModelMixin
import yaml
from datetime import datetime
NotInitObject = object()

class YamlModel(YamlModelMixin, BaseModel):
    pass
class PypeExecResult(YamlModel,extra=Extra.forbid):
    name: str
    co_name: Optional[str ]
    suc: int = 1
    skipped: int = -1

    last_run: datetime  = Field(default_factory=datetime.now)
    run_ms: int=-1

    last_check: datetime = Field(default_factory=datetime.now)
    cur_ms: int=-1

    file: Optional[str]
    lineno: Optional[int]
    # source: Optional[List[str]]
    source: List[str]=[]
    stdout: Optional[List[str]]
    stderr: Optional[List[str]]

class PypeExecResultList(YamlModel,extra=Extra.forbid):
    data: List[PypeExecResult]
    # def __getitem__(self,key)
    # def get(self,key,default=)
    @property
    def datadict(self):
        v = {v.name: v for v in self.data}
        return v
    def append(self,v ):
        assert isinstance(v, PypeExecResult)
        return self.data.append(v)


StackElement = namedlist('StackElement', 'frame filename lineno')

class StackElement(StackElement):
    @classmethod
    def from_frame(cls,frame):
        return cls(
            frame,
            os.path.realpath(frame.f_code.co_filename),
            int(frame.f_lineno),)

# ControllerNode = namedtuple('ControllerNode','control check_ctx run ctx name built stack_ele')
'''
namedlist is my chosen solution to
the SO question 
https://stackoverflow.com/questions/29290359/
on "existence-of-mutable-named-tuple-in-python"
'''
ControllerNode = namedlist('ControllerNode',
[
    ('control',None),
    ('check_ctx',None),
    ('run',None),
    ('ctx',None),
    ('name',None),
    ('built',FACTORY(lambda :NotInitObject)),
    ('stack_ele',FACTORY(lambda :StackElement.from_frame(FRAME(1)))),
    ('controller',None),
    # None),
]
)

# _ControllerNode = namedlist('_ControllerNode',
# 'control check_ctx run ctx name built stack_ele')

class ControllerNode(ControllerNode):
    # pass
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        # super().__init__()
        # assert isinstance(self.name, str), self.name
        assert self.built!=NotInitObject, self.built
    # @classmethod
    # def __new__(cls, 
    #     control=None, 
    #     check_ctx=None, 
    #     run=None, ctx=None, name=None, built=None, stack_ele=None):
    #     cls(control)
    #     # super().__new__()
    #     pass

# x = ControllerNode(a=1,b=2,c=StackElement(1,2,3))
# class ControllerNode(ControllerNode):
#     pass
#     @classmethod
#     def from_dict( cls,)
# x = ControllerNode
# import pdb;pdb.set_trace()

import re
from inspect import getsourcefile,linecache,getfile

def print_tb_stacks(stacks:List[StackElement]):
    print_tb_frames([(x.frame,x.lineno)  for x in stacks])
    if 0:
        for stack_ele in stacks:
            for line in get_frame_lineno(*stack_ele):
                eprint(line)
def print_tb_stacks_2(stacks:List[StackElement]):
    # print_tb_frames([(x.frame,x.lineno)  for x in stacks])
    # if 0:
    for stack_ele in stacks:
        for line in get_frame_lineno(*stack_ele):
            eprint(line)

# # def configure_injection(binder):
# #     binder.bind(FrameworkClass, FrameworkClass(my_func))

# import parso.python.parser
# from parso.python.parser import Parser
# # import parso
# class _myp(Parser):
#     def _pop(self):
#         tos = self.stack.pop()
#         # If there's exactly one child, return that child instead of
#         # creating a new node.  We still create expr_stmt and
#         # file_input though, because a lot of Jedi depends on its
#         # logic.
#         if len(tos.nodes) == 1:
#             new_node = tos.nodes[0]
#         else:
#             new_node = self.convert_node(tos.dfa.from_rule, tos.nodes)

#         self.stack[-1].nodes.append(new_node)
#         # assert 0


# inject.configure(configure_injection)
# # parso.python.parser.__dict__['Parser'] = _myp

from parso import load_grammar,parse
from parso.python.tree import PythonNode

def get_frame_lineno(frame, file=None, lineno=None,strip=True):
    '''
    runtime source file locating is dangerous after os.chdir
    weird because StackSummary does not seems vulnerable
    '''
    object = frame
    if file is None:
    # if 1:
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
        # print(file,os.path.exists(file))
    lines = linecache.getlines(file)
    # if not hasattr(object, 'co_firstlineno'):
    #     raise OSError('could not find function definition')
    # lnum = object.co_firstlineno - 1
    lnum = lineno - 1

    method ='parso'
    if method=='parso':
        par = load_grammar()
        #### [TBC] Possible optimisation by 
        ### 1.use tokenizor
        ### 2.specify ending lineno 
        # x = par._tokenizer(lines[lnum:])
        # pprint(list(x))
        x = parse(''.join(lines[lnum:]))
        x = [xx for xx in x.children if isinstance(xx,PythonNode)]
        if not len(x):
            ret = ['']
        else:
            x=x[0]
            ret = lines[lnum:][x.start_pos[0]-1:x.end_pos[0]-1]
            # print(ret)
            # import pdb;pdb.set_trace()

            # ret = ls
            # return ls
            # return [xx.rstrip() for xx in x.get_code().splitlines()]

        
    elif method == 'regex':
        # pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        pat = re.compile(
            r'^(\s*def\s)|'
            r'^(.*ctl\..*\()|'
            r'^(.*RWC\()'
            )
        lnum0 = lnum
        
        while lnum > 0:
            # print(repr(lines[lnum]))
            print('[matching]'+lines[lnum])
            if pat.match(lines[lnum]): break
            lnum = lnum - 1
        ret = lines[lnum:lnum0+1]

    if strip:
        ret = [x.rstrip() for x in ret]
    return ret
    # return lines, lnum

from prettytable import PrettyTable
from json import JSONDecoder, JSONDecodeError
import re
NOT_WHITESPACE = re.compile(r'[^\s]')
def json_decode_stacked(document, pos=0, decoder=JSONDecoder()):
    '''
    Source: https://stackoverflow.com/a/50384432/8083313
    '''
    while True:
        match = NOT_WHITESPACE.search(document, pos)        
        if not match:
            return
        pos = match.start()
        
        try:
            obj, pos = decoder.raw_decode(document, pos)
        except JSONDecodeError:
            # do something sensible if there's some error
            raise
        yield obj

def fstr(fstring_text, locals, globals=None):
    """
    Dynamically evaluate the provided fstring_text
    """
    locals = locals or {}
    globals = globals or {}
    ret_val = eval(f'f\'\'\'{fstring_text}\'\'\'', locals, globals)
    return ret_val

class SafeOrderedDict_ControllerNode(SafeOrderedDict):
    eletype = ControllerNode
    def __setitem__(self,k,v):
        # assert k not in self
        # if k in self:
        #     warnings.warn(f'Overwriting key {key} in a {self.__class__}')
        super().__setitem__(k,v)
        if v.name is None:
            v.name = k
        v.controller = self.controller
        # v.controller = self['_CONTROLLER']
        # if not isinstance()
NULL = object()


class ValueNotReadyError(ValueError):
    '''
    raised when accessing some value 
    that is not ready
    '''
    pass

# from pype import AppendTypeChecker,ControllerNode,Controller
# def ParentBuiltChecker(x):
#     if not x.controller.built:
#         raise ValueNotReadyError(
#             'Accessing ControllerNode value '
#             'before Controller.build()'
#             f'{controller}')
#     return x

# def AppendParentBuiltChecker(x):
#     x = AppendTypeChecker(x,ControllerNode)
#     return x.chain_with(ParentBuiltChecker)

class PlaceHolder(object):
    # @classmethod
    def __init__(self,name,value=NotInitObject):
        self.name = name
        self.value = value
        self.stack_ele = StackElement.from_frame(FRAME(1))
        self.use_pdb = 0 
    def check_built(self, x):
        if self.use_pdb:
            import pdb; pdb.set_trace()
        if self.value is NotInitObject:
            eprint('-'*30)
            eprint('ValueNotReady traceback: ')
            print_tb_frames([(self.stack_ele.frame, self.stack_ele.lineno)],)
            raise ValueNotReadyError(
                f'Placeholder not fulfilled {self.name!r}, {self.value}')

    def call(self, x):
        frame = FRAME(1)
        self.check_built(None)
        return RO(self.value, None, frame)()

    @property
    def built(self):
        return RO(None, self.call,FRAME(1))

    def put(self, v):
        self.value = v
    
    def set_pdb(self):
        self.use_pdb = 1
        return self

    
    # def __new__(cls,name):
    #     self = super().__new__()
    #     self.name = name
    #     self.value = NotInitObject
    #     return self

    # return 


class Controller(object):


    def __init__(self):
        self._state = SafeOrderedDict_ControllerNode()
        self._state.controller = self
        self.stats = {}
        self._runtime = {}
        self._runtime_copy = {}
        self.runtime = RO(self)._runtime_copy
        self._use_pdb = 0
        self.meta = None

        ###
        self._target_dir = None
        self.init_cd(None)
        self.is_built= False
        self._is_compiled = False
    @classmethod
    def from_func(cls, f, *args,**kwargs):
        ctl = cls()
        f(ctl,*args,**kwargs)
        return ctl
    # def state(self,)
    def use_pdb(self): 
        self._use_pdb = 1

    def __getitem__(self,k):
        return self._state.__getitem__(k)
        
    def export(self, k, v, t=object):
        self._state[k] = ControllerNode(
            built=AppendTypeChecker(v,t,FRAME(1)),
            stack_ele=StackElement.from_frame(FRAME(1)))
    
    def init_cd(self, x):
        '''
        target_dir is relative to rundir
        Because Pype are considered sub-components before built
        '''
        if isinstance(x,str):
            assert not os.path.isabs(x),x
            x = lambda rundir, runtime, x=x: rundir+'/'+ x
        elif x is None:
            x = lambda x,y:x
        elif callable(x):
            x
        else:
            raise NotImplementedError(type(x))
        self._target_dir = x
        return x
    @property
    def target_dir(self):return self._target_dir
    

    def apply(self,x):
        return x(self)
    def F(self, run):
        '''
        a delayed fstring filled from runtime
        '''
        tocall = RO(self.runtime, lambda x,run=run:fstr(run,x))
        return tocall

    def run_node_with_control(self, control, check_ctx, run, 
        runtime=None,name = None,built=None, stack_ele=None, 
        controller=None,frame=None):
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
        del controller ## extra reference to self

        frame=DFRAME(frame)
        if control is None:
            control = (None,None)
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
            # tocall = RO(runtime, lambda x,run=run:run.format(**x))
            # tocall = RO(runtime, lambda x,run=run:fstr(run,x))
            tocall = self.F(run)
            tocall = tocall.chain_with(s)
        else:
            run = RuntimeObject(run, None, frame).call()
            tocall = RO(runtime, run)


        if self._use_pdb:
            import pdb;pdb.set_trace()


        def msg(head):
            f, filename, lineno = stack_ele
            co = f.f_code
            eprint('')
            eprint(f'{head}(name={name!r}, code {co.co_name!r}, file={co.co_filename!r}, line {lineno!r})')
            eprint(f'  File "{filename!r}", line {lineno}, in {co.co_name})')
            print_tb_stacks_2([stack_ele])

        msg   ('[BULD]')
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

        return checked

        '''
        [return-value?]
        is affected by check()
        '''
    def pprint_stats(self):
        x = PrettyTable()
        x.field_names = ["name", 
            "co_name", 
            # "source",
            "lineno", "skipped","cur_ms", "run_ms","file"]        
        for v in self.meta.data:
            # xx = []
            # for xn in x.field_names:
            #     vv = getattr(v,xn)
            #     # if xn =='source':
            #     #     vv = '\n'.join(vv)
            #     xx.append(vv)                
            # x.add_row(xx)
            x.add_row([getattr(v,xn) for xn in x.field_names])        
        x.align='l'
        eprint(x.get_string())
        # pprint(self.meta)

    @property
    def nodes(self):
        return self._state


    class BuiltView(object):
        def __init__(self, c, data):
            assert isinstance(c,Controller)
            assert isinstance(data,SafeOrderedDict_ControllerNode),data
            self.c = c
            self.data = data
        def __getitem__(self,k):
            def CheckIsBuilt(x):
                if not self.c.is_built:
                    raise ValueNotReadyError(
                        'Accessing ControllerNode value '
                        'before Controller.build()'
                        f'{self.c}')                 
                return None       
            v = RuntimeSideEffect( self.data[k].built, CheckIsBuilt, FRAME(1))
            return v

    @property
    def built(self,BuiltView=BuiltView):
        '''
        return a view so that
        self.built[key] => 
            ( (check self.is_built) >> (return self.state[key]) )
        '''
        return BuiltView(self, self._state)

        # def _f(x):
        #     assert self.is_built,f'Must call Controller.build() before access .built for :{self!r}'
        #     return x
        # return RO(self, _f, FRAME(1))
        # self._state[]
        # return RO(self,frame=FRAME(1)).chain_with()

    @property
    def is_compiled(self):
        return self._is_compiled
    # @property
    def runtime_initer(self, k, v, t=object):
        assert not self.is_compiled,(
            'Trying to reinit inputs during running.'
            '\nuse Controller.runtime_setter(k,v) instead!'
            '\nfor variables local to this pype.'
        )
        self._runtime.__setitem__(k,AppendTypeChecker(v,t,FRAME(1)))
        return (self,k,v,t)
        # return self._runtime

    # @property
    def runtime_setter(self,k,v,t=object):
        assert self.is_compiled,(
            'Trying to set runtime variable during compiling'
            '\nuse Controller.runtime_initer(k,v) instead!'
            '\nfor variables local to this pype.'
        )
        
        self._runtime_copy.__setitem__(k,AppendTypeChecker(v,t,FRAME(1)))
        return (self,k,v,t)
        # return self._runtime_copy


    def register_node(self, 
        control=check_write_always,
        check_ctx=None, run=None, ctx=NotInitObject, name = None, run_now = False, built=None, frame=None):
        '''
        ctx defaults to Controller.runtime if not specified
        frame: 
          the frame would be used to format traceback.
          if calling RWC within some function, better to pass down calling context 
          to level the traceback
        '''
        frame = DFRAME(frame)
        stack_ele = StackElement.from_frame(frame)

        if ctx is NotInitObject:
            ctx = self.runtime

        if name is None:
            name = lambda x:f'_defaul_key_{x}'

        _name = (self._state.__len__())
        if not isinstance(name,str):
            name = name(_name)

        assert run is not None, 'Must specify "run"'
        assert isinstance(name,str),name

        self._state[name]= node = ControllerNode(control, check_ctx, run, ctx, name, built, stack_ele)
        # if run_now:
        #     '''            
        #     '''
        #     self.run_node_with_control(*node)
        return node

    # RWC = run_node_with_control
    RWC = register_node
    def run(self,*args,**kwargs):
        return self.build(*args,**kwargs)
    def build(self, rundir=None, metabase=None, runtime= None, 
        target_dir=NotInitObject):
        '''
        return: a list indicates whether each step is skipped or executed

        stdout redirecting?


        '''
        self._is_compiled = 1
        if runtime is None:
            runtime = {}
        self._runtime.update(runtime)
        self._runtime_copy.clear()
        self._runtime_copy.update(self._runtime)
        # self._runtime_copy = RO(self._runtime.copy(),None,FRAME(1))
        rets = []



        if rundir is None:
            rundir = os.getcwd()
        rundir = os.path.realpath(os.path.expandvars(os.path.expanduser(rundir)))
        if target_dir is not NotInitObject:
            '''
            Allow overridding
            '''
            self.init_cd(target_dir)

        rundir = self.target_dir(rundir, self.runtime)
        rundir = os.path.realpath(rundir)
        os.makedirs(rundir) if not os.path.exists(rundir) else None
        
        self.rundir = rundir

        # rundir = RuntimeObject( (rundir, self._runtime), self.target_dir).call()

        ### upon running, needs to chdir to rundir
        ### always consult self.target_dir about which
        os.chdir(rundir)

        if os.path.isfile(rundir):
            meta_file = rundir
        else: 
            if metabase is None:
                metabase = 'PYPE.json'
            meta_file = rundir +'/' +metabase

        eprint(f'[AcquirngLock]{meta_file}')
        with FileLock(meta_file+'.lock'):
            self.meta = meta = PypeExecResultList(data=[])
            diskmeta = PypeExecResultList(data=[])
            try:
                with open(meta_file,'r') as f:
                    it = json_decode_stacked(f.read())
                    [diskmeta.append(PypeExecResult(**x)) 
                        for x in it]
                shutil.move( meta_file, meta_file+'.last') 
                if not len(diskmeta.data):
                    raise ValueError('Empty Json') 
            except Exception as e:
                eprint(f'[Controller.run] Unable to load metafile:{meta_file} {e}')
                # raise e

            with open(meta_file,'w',1) as f:
                def push(ret):
                    self.meta.append(ret)
                    f.write(ret.json(indent=2)+'\n')
                    return 

                ret = PypeExecResult(
                    name='_PYPE_START',
                    suc=1,                    
                )
                push(ret)


                for k,v in self._state.items():
                    out = StdoutDup(io.StringIO())
                    err = StderrDup(io.StringIO())
                    v
                    t0 = time.time()
                    suc = 1
                    checked = 1
                    # assert isinstance(v, ControllerNode),'Must'
                    try:
                        # print(*v)
                        # print(type(v))
                        # print(f'[staring]{k}{v}')
                        checked = self.run_node_with_control(*v)
                        # print(f'[finishn]{k}{v}')
                    except Exception as e:
                        suc = 0
                        raise e
                    finally:
                        skipped = int(checked)
                        dt = time.time()-t0
                        cur_ms = dtms = int(dt*1000)
                        out.seek(0)
                        err.seek(0)
                        disknode = diskmeta.datadict.get(k,None)
                        run_ms = None
                        if (disknode is not None) and skipped:
                            run_ms = disknode.run_ms
                            last_run = disknode.last_run
                            # print(f'[1]{run_ms}')
                        else:
                            if skipped:
                                run_ms = -1
                                last_run = datetime.fromtimestamp(0)
                            else:
                                run_ms = dtms
                                last_run = datetime.now()
                            # print(f'[2]{run_ms}')
                        co  = v.stack_ele.frame.f_code
                        ret = PypeExecResult(
                            name   = v.name,
                            suc    = suc,
                            co_name= co.co_name,
                            # co_name=repr(v.run)[:30],
                            # co_name= v.run.__code__.co_name,
                            skipped= skipped,
                            last_run=last_run,
                            # end_time = datetime.datetime.now(),
                            run_ms = run_ms,
                            cur_ms = cur_ms,
                            stdout = out.read().splitlines(), 
                            stderr = err.read().splitlines(),
                            file   = os.path.realpath(co.co_filename),
                            lineno = v.stack_ele.lineno,
                            source = (get_frame_lineno(*v.stack_ele)),
                        )
                        push(ret)

                ret = PypeExecResult(
                    name='_PYPE_END',
                    suc=1,                    
                )
                push(ret)
            self.is_built = True
            return self.meta


    def lazy_wget(self, url, name=lambda x:f'lazy_wget/{x}'):
        '''
        fix cwd at runtime
        '''
        # print(type(url))
        # assert not isinstance(url,RO),RO
        url = RO(url)
        target = RO(url, os.path.basename)#.start_pdb()
        def _lazy_wget(ctx,url=url,target=target):
            url = url.call()
            target = target.call()

            # import pdb;pdb.set_trace()
            ret = urllib.request.urlretrieve(url, target+'.temp',)
            shutil.move(target+'.temp',target)

        return self.register_node(
            check_write_2, check_ctx=target, run=_lazy_wget,
            name=name,
             built=target,)

    def lazy_apt_install(self, PACK,name=None):
        if name is None:
            name = lambda x:f'lazy_apt_install/{x}'
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
            name=name,
            )

    def lazy_pip_install(self, TARGET_LIST,pre_cmd='',
    flags='install --upgrade',
    name=lambda x:f'lazy_wget/{x}'):
        TARGETS = sjoin(TARGET_LIST)
        return self.RWC([is_pypack_installed, None], TARGET_LIST, f'''
        {pre_cmd}
        {SEXE} -m pip {flags} {TARGETS}
        ''',built=TARGET_LIST,
        name=name,
        frame=FRAME(1),)

        # frame=FRAME(1))


    def lazy_git_url_commit(self, url, commit, target_dir=None,
    name=lambda x:f'lazy_git/{x}',
    ):
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
    return RuntimeObject(TARGET).chain_with(lambda TARGET:s(f'''
        set -e; set -o allexport; source {TARGET} &>/dev/null;
        {PY_DUMP_ENV_TOML("/dev/stdout")}
        '''),).chain_with(io.StringIO).chain_with(run_load_toml_env, keys=keys, toml_file=THIS
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


def TypeCheckCaller(x, t):
    if not isinstance(x,t):
        raise TypeError(f'Value must be of type {t} not {type(x)} for {x!r}')
    # assert isinstance(x,t),f'Type Checking failed, (t,x)
    return x

def AppendTypeChecker(x,t,frame=None):
    '''
    Chaining a type-checker function
    '''
    if not isinstance(x, RuntimeObject):
        x = RuntimeObject(x,None,DFRAME(frame))
    return x.chain_with(TypeCheckCaller, t= t, _frame=DFRAME(frame))
