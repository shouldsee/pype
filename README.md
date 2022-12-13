#! https://zhuanlan.zhihu.com/p/577668335

# 8514-pype: A PYthon PlannEr

[CATSMILE-8514](http://catsmile.info/8514-pype-readme.html)

[Github:shouldsee/pype](http://github.com/shouldsee/pype)

## 前言

- 目标: 
- 结论: 
- 背景与动机: 
    - 替换bash脚本并加强其路棒性,简化其维护.
- {备注:[], 关键词:[pipeline], 相关篇目:[], 完成度:爱好, 主要参考:[]} 
- 展望方向: [] 
- 相关篇目: [] 
- CHANGLOG:
    - 20221027 v0.0.4

## Installation:

As a python package

`python3 -m pip install https://github.com/shouldsee/pype/tarball/master`

## Design Principles

- Readbility: Focus on transformation by chaining functions 
(aka. Functional Programming)
 via `RuntimeObject(callee,caller)`
- Compositionality: Easy specification of objects with connectable endpoints, 
via core functions:
    - `Controller.built`,`PlaceHolder.built`:deferred reference, 
    - `Controller.export(k,v,t)`: exported to be available via `.built`
    - `Controller.runtime_init(k,v,t)`: variable loading to fire callables against.
- Debuggability: via tracebacks, logged stdout/stderr, and type checkers
- Integrable: All of and more than python packages.
- Simplicity: capture re-occurring patterns and replace with simpler syntaxes 
- Stateful Laziness: Skip an operation if its target already achieved

### quick example: `python3 examples/know_my_cli.py`

```python
from pype import Controller
from pype import RuntimeObject as RO
from datetime import datetime
def know_my_cli(ctl):

    ctl.init_cd('./cli-simple')
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype',
      '598b7a2b1201d138260c22119afd7b4d5449fe97',
      'temp_pype')
    ctl.export('done_ts', RO(None, lambda x:datetime.now()), datetime )
    
if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build('$HOME/')
    ctl.pprint_stats()
    print('[DONE]',ctl.built['done_ts'].call())
```

### example with variables: `python3 examples/know_my_cli_adv.py`

With more features demonstrated

```python
from pype import Controller
from pype import RuntimeObject as RO
from pype import PlaceHolder
import yaml
import os
def know_my_cli(ctl, host, user, key, password_file):
    '''
    [TBC] adds lazy_apt_update to avoid 
    update too often and not doing update.

    https://superuser.com/questions/1524610/detect-if-apt-get-update-is-necessary
    '''
    ctl.runtime_initer('host',host,str)
    ctl.runtime_initer('user',user,str)
    ctl.runtime_initer('key',key,str)
    ctl.init_cd('./cli/')
    def load_pass(x):
        with open(password_file,'r') as f:
            v = yaml.safe_load(f.read())
            ctl.runtime_setter("passwds",v,object) 
        
    ctl.RWC(run=load_pass)

    ctl.lazy_apt_install('nano git proxychains4'.split())

    ### skipper criteria needs rewrite
    # ctl.lazy_pip_install('toml pyyaml'.split())  
     
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype',
    '598b7a2b1201d138260c22119afd7b4d5449fe97',
    'temp_pype')
    SH_CONN = RO(ctl).rundir +'/connect-' + ctl.runtime['key'] +'.sh'
    ctl.RWC(run = lambda rt:
        open( SH_CONN(),'w').write(
        f'''
        sshpass -p "{rt["passwds"][rt["key"]]}" | ssh -p22 {rt["user"]}@{rt["host"]} -vvv 
        ''')
    )
    ctl.export('SH_CONN', SH_CONN, str)
    
if __name__=='__main__':
    
    key = PlaceHolder('key')
    host = PlaceHolder('host')
    user = PlaceHolder('user')
    ctl = Controller.from_func(know_my_cli, host.built, user.built, key.built, 
        os.path.realpath('examples/passwd.yaml'))
    ### same as
    # ctl = Controller()
    ## then
    # know_my_cli(ctl, '127.0.0.1', 'ubuntu')

    for k,h,u in [
        'here 127.0.0.1 ubuntu'.split(),
        'remote 192.168.12.133 ubuntu'.split()

    ]:
        key.put(k)
        host.put(h)
        user.put(u)
        ctl.build('$HOME/')
        
    ctl.pprint_stats()
    '''
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
| name               | co_name     | lineno | skipped | cur_ms | run_ms | file                              |
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
| _PYPE_START        | None        | None   | -1      | -1     | -1     | None                              |
| _defaul_key_0      | know_my_cli | 22     | 0       | 1      | 1      | /root/cli/examples/know_my_cli.py |
| lazy_apt_install/1 | know_my_cli | 24     | 1       | 13     | -1     | /root/cli/examples/know_my_cli.py |
| lazy_git/2         | know_my_cli | 29     | 1       | 10     | 1787   | /root/cli/examples/know_my_cli.py |
| _defaul_key_3      | know_my_cli | 33     | 0       | 1      | 1      | /root/cli/examples/know_my_cli.py |
| SH_CONN            | know_my_cli | 39     | 0       | 0      | 0      | /root/cli/examples/know_my_cli.py |
| _PYPE_END          | None        | None   | -1      | -1     | -1     | None                              |
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
    '''

    '''
$ls $HOME/cli
drwxr-xr-x 6 root root  165 10月 27 02:41 temp_pype
-rwxr-xr-x 1 root root    0 10月 27 02:41 PYPE.json.lock
-rw-r--r-- 1 root root 3.7K 10月 27 02:41 PYPE.json.last
-rw-r--r-- 1 root root   71 10月 27 02:41 connect-here.sh
-rw-r--r-- 1 root root 3.7K 10月 27 02:41 PYPE.json
-rw-r--r-- 1 root root   75 10月 27 02:41 connect-remote.sh

    '''
```

### Example: debuggability: evaltime traceback for RuntimeObject


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

### #xample stderr log:

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

### Example summary log `Controller.pprint_stats`:

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

## Listed Features

- typical workflows
    - `.runtime_init()` to load runtime variables
    - `.init_cd()` to specify working directory
    - `.RWC()`  to register callables in a linear chain, with `checker` skip criteria
        - optional double `checker(check_ctx)` after `run()` and `writer()`
    - `.lazy_*()` to register convenience workflows
    - `.export()` to make variables available

- Functional low-level batteries: RuntimeObject(callee,caller) to enable low level composition
of argument-less callables.
- Buildtime high-level batteries included for apt,git,pip
- Same language for 
   - file-based-lazy, argless, buildtime functions. reused 
   when migrated to new env. (see "know" functions)
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

### ToDo

- [TBC] `print_frame_lineno()` adapt parso to save parsing

