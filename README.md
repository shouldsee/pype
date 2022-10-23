# pype: A PYthon PlannEr


## Objective:

We seek a python suite that allows easier composition
of build time complexities.

## Design Principles:

- RuntimeObject(callee,caller) to enable low level composition
of argument-less callables.
- Batteries included for apt,git,pip
- Runtime arguments via `Controller.runtime`
- easier composition via `know` functions
- [TBC] simpler error messages with lineno
- compatible with in-package relative module import 
