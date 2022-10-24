import pytest
from pype import Controller,RO,s,THIS
from pype import NonConcreteValueError
def know_my_cli(ctl):
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')

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
  File "/repos/shared/repos/pype/examples/test_base.py", line 14, in test_error
    x = x.chain_with(lambda x: (_ for _ in ()).throw(myexe))
  File "/repos/shared/repos/pype/examples/test_base.py", line 15, in test_error
    x = x.chain_with(lambda x:[][1])
  File "/repos/shared/repos/pype/examples/test_base.py", line 16, in test_error
    x = x.chain_with(lambda x:[x])
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
    for i,l in enumerate(expected.splitlines()):
        gotline = gots[i]
        pre = l.strip('-').split('line')[0]
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
  File "/repos/shared/repos/pype/examples/test_base.py", line 56, in test_print_stack
    x = x.chain_with(lambda y,x=x:x.print_call_stack())
  File "/repos/shared/repos/pype/examples/test_base.py", line 57, in test_print_stack
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

    


def test_strict_call():
    with pytest.raises(NonConcreteValueError) as einfo:
        ctl = Controller()
        x = RO(None)
        y = RO([x])[0]
        value = y.call()
    

# if __name__=='__main__':
#     ctl = Controller()
#     know_my_cli(ctl)
#     ctl.build()
#     ctl.pprint_stats()

#     test_strict_call()