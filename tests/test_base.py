import pytest
from pype import Controller,RO,s,THIS
from pype import NonConcreteValueError
from pype import PlaceHolder,ValueNotReadyError
#from .examples.know_my_cli import know_my_cli
#from .examples.know_my_cli import know_my_cli

def test_know_my_cli():
    '''
    Better to cleanup before running
    '''
    def know_my_cli(ctl):
        ctl.lazy_apt_install('nano git proxychains4'.split())
#        ctl.lazy_pip_install('toml pyyaml'.split())
        ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97',
            target_dir='temp_pype')
        return ctl
    ctl = know_my_cli(Controller())
    ctl.build()

def test_error(capfd):
    myexe = Exception('foobar')
    with pytest.raises(Exception) as einfo:
        x = RO(None)
        x = x.chain_with(lambda x:x)
        x = x.chain_with(lambda x: (_ for _ in ()).throw(myexe))
        x = x.chain_with(lambda x:[][1])
        x = x.chain_with(lambda x:[x])
        x.call()
    assert einfo.value is myexe
    expected = '''
------------------------------
Evaltime traceback:
  File "/repos/shared/repos/pype/tests/test_base.py", line 14, in test_error
    x = x.chain_with(lambda x: (_ for _ in ()).throw(myexe))
  File "/repos/shared/repos/pype/tests/test_base.py", line 15, in test_error
    x = x.chain_with(lambda x:[][1])
  File "/repos/shared/repos/pype/tests/test_base.py", line 16, in test_error
    x = x.chain_with(lambda x:[x])
------------------------------
'''

    out, err = capfd.readouterr()
    assert_similar_tb(expected, err)



def test_error_simple(capfd):
    myexe = Exception('foobar')
    with pytest.raises(Exception) as einfo:
        x = RO(None)
        x = RO(x,lambda x: (_ for _ in ()).throw(myexe))
        x = RO(x,lambda x:[][1])
        x = RO(x,lambda x:[x])
        x.call()
    assert einfo.value is myexe
    expected = '''
------------------------------
Evaltime traceback:
  File "/repos/shared/repos/pype/tests/test_base.py", line 40, in test_error_simple
    x = RO(x,lambda x: (_ for _ in ()).throw(myexe))
  File "/repos/shared/repos/pype/tests/test_base.py", line 41, in test_error_simple
    x = RO(x,lambda x:[][1])
  File "/repos/shared/repos/pype/tests/test_base.py", line 42, in test_error_simple
    x = RO(x,lambda x:[x])
------------------------------
'''
    out, err = capfd.readouterr()
    assert_similar_tb(expected, err)




def test_no_stack():
    with pytest.raises(Exception) as einfo:

        ctl = Controller()
        x = RO(None)
        x = x.chain_with(lambda x:(x,1))
        x = x.chain_with(lambda x:(x,2))
        x = x.print_call_stack()
        x = x.chain_with(lambda x:(x,3))
        x = x.chain_with(lambda x:[][2])
        x.call()
    assert 'Stack not specified' in str(einfo.value)
                
from pprint import pprint
def assert_similar_tb(expected, got):
    expected = expected.lstrip()
    
    print('[EXPECTED]')
    print(expected)
    print('[GOT]')
    print(got)
    gots = got.splitlines()
    for i,el in enumerate(expected.splitlines()):
        gotline = gots[i]
        if ('File "' in el) and ("line" in el):
            print(f'[skip file lineno]{el}')
            continue
        pre = el.strip('-').split('line')[0]
        assert gotline.startswith(pre),(gotline,pre)
        # assert l.split('')

    # assert err == expected,pprint([err,expected])
    # "Hello World!"    
    # ctl.RWC(run=x)
    return 

def test_print_stack(capfd):
    expected = '''
------------------------------
Evaltime traceback:
  File "/repos/shared/repos/pype/tests/test_base.py", line 56, in test_print_stack
    x = x.chain_with(lambda y,x=x:x.print_call_stack())
  File "/repos/shared/repos/pype/tests/test_base.py", line 57, in test_print_stack
    x = x.chain_with(lambda x:(x,3))
'''.lstrip()


    ctl = Controller()
    x = RO(None)
    x = x.chain_with(lambda x:(x,1))
    x = x.chain_with(lambda x:(x,2))
    x = x.chain_with(lambda y,x=x:x.print_call_stack())
    x = x.chain_with(lambda x:(x,3))
    # x = x.chain_with(lambda x:[][2])
    x.call()            
    out, err = capfd.readouterr()
    assert_similar_tb(expected, err)

def test_print_stack_cd(capfd):
    import os
    expected = '''
------------------------------
Evaltime traceback:
  File "/repos/shared/repos/pype/tests/test_base.py", line 56, in test_print_stack
    x = x.chain_with(lambda y,x=x:x.print_call_stack())
  File "/repos/shared/repos/pype/tests/test_base.py", line 57, in test_print_stack
    x = x.chain_with(lambda x:(x,3))
'''.lstrip()


    x = RO(None)
    x = x.chain_with(lambda x:(x,1))
    x = x.chain_with(lambda x:(x,2))
    x = x.chain_with(lambda y,x=x:x.print_call_stack())
    x = x.chain_with(lambda x:(x,3))
    # x = x.chain_with(lambda x:[][2])
    os.chdir('/tmp/')
    x.call()            
    out, err = capfd.readouterr()
    assert_similar_tb(expected, err)    

    


def test_strict_call():
    '''
    Now performs auto expansion of iterables
    like dict,list,namedlist, even if they 
    do not look like RuntimeObject as a whole.
    '''
    # with pytest.raises(NonConcreteValueError) as einfo:
    if 1:
        ctl = Controller()
        x = RO(None)
        y = RO([x])[0]
        value = y.call()
        assert value == None

    


def test_ph_1(capfd):
    with pytest.raises(ValueNotReadyError) as einfo:
        input1 = PlaceHolder('input1')   
        input1.built()

    input1.put('123')
    input1.built()

    input1.put(RO('123'))
    input1.built()

def test_runtime_setters(capfd):
    '###!!! [test] runtime_setter() and runtime_initer()'
    if 0:
        ctl.runtime_initer('GMX',  GMX, str)
        ctl.RWC(run=lambda x:ctl.runtime_setter('PDB_ID',12))
        ctl.RWC(run=lambda x:ctl.runtime_setter('PDC',12))    
    # ctl.RWC(run=ctl.F('[dbg]{PDC}').chain_with(print).start_pdb())
    # ctl.RWC(run=ctl.F('[dbg]{PDB_ID}').chain_with(print).start_pdb()
    raise NotImplementedError

def test_tb_typecheck(capfd):
    '''
    [TBC,Debuggability]: make sure type check fails with a nice traceback
    '''
    expected = '''
  warnings.warn('[print_tb_frames,StackSummary] is not safe after os.chdir. StackSummary only shows relative path')
  File "/root/catsmile/pype/examples/depend_mol.py", line 145, in know_gromacs
    ctl.export('GMX', GMX, int)
  File "/root/catsmile/pype/examples/task_gromacs.py", line 339, in main
    GMX    = pype1.built["GMX"],
  File "/root/catsmile/pype/examples/task_gromacs.py", line 49, in build
    ctl.runtime_initer('GMX',  GMX, str)
  File "/root/catsmile/pype/pype/controller.py", line 226, in call
    callee = callee.call(stacknew, strict)
    '''.lstrip()
    raise NotImplementedError


def test_built_attr(capfd):
    '''
    [] 
    '''
    ctl = Controller()
    ctl.RWC(name='GMX', run='echo /usr/local/bin/gmx')

    pype1 = ctl
    ctl.export('ret', RO('1'), int)
    ctl.export('ret2', RO('1'), str)
   # [test] raise error to non-compiled nodes
    pype1.built["GMX"]
    with pytest.raises(KeyError) as einfo:
        pype1.built['blah']
    
    ## stop runtime access to non-built nodes
    with pytest.raises(ValueNotReadyError) as einfo:
        pype1.built['GMX'].call()

    ctl.build()

    ## allow runtime access to built nodes
    if 1:
        pype1.built['GMX'].call()
    
    ## performs type check on exported variable
    ## mismatched type
    with pytest.raises(TypeError) as einfo:
        ctl.built['ret']()

    ## matched type
    ctl.built['ret2']()

 
        # ctl = Controller.from_func(lambda ctl,x:None,x=input1)
        # ctl.run()
        # assert isinstance()


# if __name__=='__main__':
#     ctl = Controller()
#     know_my_cli(ctl)
#     ctl.build()
#     ctl.pprint_stats()

#     test_strict_call()