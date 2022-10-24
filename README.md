# pype: A PYthon PlannEr


## Design Principles:

- Functional low-level batteries: RuntimeObject(callee,caller) to enable low level composition
of argument-less callables.
- Buildtime high-level batteries included for apt,git,pip
- Same language for 
   - file-based-lazy, argless, buildtime functions. reused when migrated to new env. (see "know" functions)
   - runtime functions with runtime inputs. reused when calling on a new argument.
   - allowing runtime functions to check buildtime deps when initing.
- portable `know` functions that can be imported to compose larger systems. 
- [DONE] simpler error messages with lineno, much more debuggable than bash scripts.
   - added: `evaltime traceback` to show which RuntimeObject chain throws the error
- [TBC] log control
   - during `Controller.build()`, printing context of `Controller.RWC`
    ```
    [SKIP](name='_defaul_key_0', code 'know_my_cli', file='/repos/shared/repos/pype/tests/test_base.py', line 8)
    File "/repos/shared/repos/pype/tests/test_base.py", line 8, in know_my_cli
        ctl.lazy_apt_install('nano git proxychains4'.split())

    [SKIP](name='_defaul_key_1', code 'know_my_cli', file='/repos/shared/repos/pype/tests/test_base.py', line 11)
    File "/repos/shared/repos/pype/tests/test_base.py", line 11, in know_my_cli
        target_dir='temp_pype')
    ```
    
- [TBC] typical project structures? 
    - pype eats python functions, which needs to be installed before using. import a function from http is risky?
    - onefile pype: needs to specify python depedencies before eating the actual `know` function
    - example situation: 
       - pype A lazy git install pype B. pype B lazy git install pype C. encourage explicit management of a package index,
       where a pacakge is just a folder in the index like 'sites-package'.
- Linear chain execution within pype.
- compatible with in-package relative module import 
- typical project workflow
    - init apt deps
    - init project.sites-package,prepare and check functions
    - workload: run some tests, build some binaries
    - start some servers
    - watch for signal that triggers workload and sends back stats.


## Installation:

As a python package

`python3 -m pip install https://github.com/shouldsee/pype/tarball/master`

## example: know functions

`know` functions let a controller knows something, typically the required envrionment.

`know_my_cli.py`

```python3
from pype import Controller
def know_my_cli(ctl):
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')
    
if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build()
    ctl.pprint_stats()
```
 
`python3 know_my_cli.py`

## evaltime traceback for RuntimeObject


This pytest function shows what's expected when an error-raising function
is composed into the chain. on `x.call()`, the lambda funcs got executed
and a traceback outlines the call chain that leads to the error.

[TBC] adds optional echo stream to trace the whole RuntimeObject chain
to the start of chain.

```python
import pytest
from pype import RuntimeObject as RO
def test_error(capfd):
    myexe = Exception('foobar')
    with pytest.raises(Exception) as einfo:
        x = RO(None)
        x = x.chain_with(lambda x:x)
        x = x.chain_with(lambda x: (_ for _ in ()).throw(myexe))
        x = x.chain_with(lambda x:[][1])
        x = x.chain_with(lambda x:[x])
        x.call()

        '''
        The above is equivalent to 
        x = RO(None)
        x = RO(x,lambda x: (_ for _ in ()).throw(myexe))
        x = RO(x,lambda x:[][1])
        x = RO(x,lambda x:[x])
        x.call()
        '''

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

```
