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


## know functions

`know` functions let a controller knows something, typically the required envrionment.


`know_my_cli.py`

```python3
from pype import Controller
def know_my_cli(ctl):
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
if __name__=='__main__':
    ctl = Controller()
    ctl.build()
```
 
