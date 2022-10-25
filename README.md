# pype: A PYthon PlannEr

## Installation:

As a python package

`python3 -m pip install https://github.com/shouldsee/pype/tarball/master`

## quick example: a simple pype

`know` functions let a controller knows something, typically the required envrionment.

`know_my_cli.py`

```python
from pype import Controller
def know_my_cli(ctl):
    '''
    [TBC] adds lazy_apt_update to avoid 
    update too often and not doing update.

    https://superuser.com/questions/1524610/detect-if-apt-get-update-is-necessary
    '''

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


## Design Principles:

- Functional low-level batteries: RuntimeObject(callee,caller) to enable low level composition
of argument-less callables.
- Buildtime high-level batteries included for apt,git,pip
- Same language for 
   - file-based-lazy, argless, buildtime functions. reused when migrated to new env. (see "know" functions)
   - runtime functions with runtime inputs. reused when calling on a new argument.
   - allowing runtime functions to check buildtime deps when initing.
- portable `know` functions that can be imported to compose larger systems. 
- [TBC] adding bash wrapper to interact with stdin? clear or append to meta file?
- [TBC,important] 
  - `Pype` can be linear chained, or parallel chained, to create larger Pypes.
  - [DONE] Each `Pype` knows where it is defined.
  - [DONE] Each `Pype` manages its own meta file
  - [DONE] usually each Pype would bind to a directory, with some runtime variable.
    - `-C` to change directory before execution
    - `--meta-file` to specify meta file other than `PYPE.toml`
    - consider warnings if multiple Pype / multiple runtimes executed against the same meta file.
      - option_1: only accepts empty file
      - option_2: allow overwrite if Pype name matches
      and runtime matches. (needs to specify fields to check)
      - option_3: allow overwrite if Pype name matches,ignore runtime stream.
      - option 4: allow overwrite what-so-ever
    - use a constructor to delay the specification of directory until runtime.
  - [needtest] also allows binds to a single file.
  - [DONE] when Pype is executed, the bound meta file gets updated.
    - possible back-injection by file-watching?
  - when creating new directories, consider new Pypes.
  - contextManager to construct `Pype`. 
- [DONE] simpler error messages with lineno, much more debuggable than bash scripts.
   - added: `evaltime traceback` to show which RuntimeObject chain throws the error
- [DONE] log control
   - during `Controller.build()`, printing context of `Controller.RWC`
   - finer-grain?
- [TBC] typical project structures? 
    - pype eats python functions, which needs to be installed before using. import a function from http is risky?
    - onefile pype: needs to specify python depedencies before eating the actual `know` function
    - example situation: 
       - pype A lazy git install pype B. pype B lazy git install pype C. encourage explicit management of a package index,
       where a pacakge is just a folder in the index like 'sites-package'.
- [TBC] exec logging to disk.
  - write last execution time to cache, with runtime.
  - if execution depends on runtime, th
- Linear chain execution within pype.
- compatible with in-package relative module import 
- typical project workflow
    - init apt deps
    - init project.sites-package,prepare and check functions
    - workload: run some tests, build some binaries
    - start some servers
    - watch for signal that triggers workload and sends back stats.



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

### example stderr log:

```
[BULD](name='lazy_apt_install/0', code 'know_my_cli', file='/repos/shared/repos/pype/examples/know_my_cli.py', line 4)
  File "/repos/shared/repos/pype/examples/know_my_cli.py", line 4, in know_my_cli
    ctl.lazy_apt_install('nano git proxychains4'.split())
[CHCK][SKIP]

[BULD](name='lazy_wget/1', code 'know_my_cli', file='/repos/shared/repos/pype/examples/know_my_cli.py', line 6)
  File "/repos/shared/repos/pype/examples/know_my_cli.py", line 6, in know_my_cli
    'toml pyyaml'.split())
[CHCK][RUNN]

[BULD](name='lazy_git/2', code 'know_my_cli', file='/repos/shared/repos/pype/examples/know_my_cli.py', line 7)
  File "/repos/shared/repos/pype/examples/know_my_cli.py", line 7, in know_my_cli
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')
[CHCK][SKIP]
```

### example summary log `Controller.pprint_stats`:

```
+--------------------+-------------+--------+---------+--------+--------+--------------------------------------------------+
| name               | co_name     | lineno | skipped | cur_ms | run_ms | file                                             |
+--------------------+-------------+--------+---------+--------+--------+--------------------------------------------------+
| _PYPE_START        | None        | None   | -1      | -1     | -1     | None                                             |
| lazy_apt_install/0 | know_my_cli | 4      | 1       | 35     | 4520   | /repos/shared/repos/pype/examples/know_my_cli.py |
| lazy_wget/1        | know_my_cli | 6      | 0       | 6141   | 6141   | /repos/shared/repos/pype/examples/know_my_cli.py |
| lazy_git/2         | know_my_cli | 7      | 1       | 8      | -1     | /repos/shared/repos/pype/examples/know_my_cli.py |
| _PYPE_END          | None        | None   | -1      | -1     | -1     | None                                             |
+--------------------+-------------+--------+---------+--------+--------+--------------------------------------------------+
```