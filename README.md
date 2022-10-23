# pype: A PYthon PlannEr


## Objective:

We seek a python suite that allows easier composition
of build time complexities.

## Design Principles:

- RuntimeObject(callee,caller) to enable low level composition
of argument-less callables.
- Batteries included for apt,git,pip
- Same language for 
   - file-based-lazy, argless, buildtime functions. reused when migrated to new env. (see "know" functions)
   - runtime functions with runtime inputs. reused when calling on a new argument.
   - allowing runtime functions to check buildtime deps when initing.
- [TBC] simpler error messages with lineno
- much more debuggable than bash scripts.
- compatible with in-package relative module import 

## Installation:

As a python package

`python3 -m pip install https://github.com/shouldsee/pype/tarball/master`

## example: know functions

`know` functions let a controller knows something, typically the required envrionment.

`know_my_cli.py`

```python3
from pype import Controller
def know_my_cli(ctl):
    #ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')
    
if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build()
    ctl.pprint_stats()
```
 
`python3 know_my_cli.py`
