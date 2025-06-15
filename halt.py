# halt.py

import timeit
import inspect


def halt(fnc=None):

    '''"halt" is intended to measure the running time of other functions
by specifying its arguments and name in the arguments of the "halt"
function methods, or by using "halt" as a decorator. In addition, when
using "halt" as a function with arguments, it is possible to output the
values ​​of the parameters and arguments of the target function.

==========
DO NOT USE "halt" both as usual function and as decorator in the same
code,this will lead to infinite recursion
==========

Using as function:
    halt.method([*args,] fnc=some_target_func [, **kwargs])

Methods defined here:
    time - returns running time of target function
    params - returns complete information about all parameters
             and arguments of a target function

As a return value, "halt" produces the result of calling the target
function, which allows you to use it in any intermediate section of the
code:

    print(halt(<...>))
    a = list(halt(<...>))
    etc.
'''

    def f_0(*args, **kwargs):
        if 'fnc' in kwargs:
            nonlocal fnc
            fnc = kwargs['fnc']
            del kwargs['fnc']
        res = fnc(*args, **kwargs)
        params = inspect.getfullargspec(fnc),\
            inspect.getcallargs(fnc, *args, **kwargs)
        print('\n\033[1m\033[7m\033[36m', fnc.__name__,
              '\033[0m', '\n', params, '\n')
        return res

    def f_1(*args, **kwargs):
        if 'fnc' in kwargs:
            nonlocal fnc
            fnc = kwargs['fnc']
            del kwargs['fnc']
        startt = timeit.default_timer()
        res = fnc(*args, **kwargs)
        timee = timeit.default_timer() - startt
        print('\n\033[1m\033[7m\033[32m',
              fnc.__name__, '\033[0m', 'time: ',)
        hourr = int(timee // 3600)
        minutee = int(timee % 3600 // 60)
        secondd = timee % 60
        print(f'{hourr:02d} h {minutee:02d} min {secondd:.8f} s\n')
        return res
    halt.params = f_0
    halt.time = f_1
    if fnc:
        return halt.time


halt()
