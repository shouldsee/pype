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
