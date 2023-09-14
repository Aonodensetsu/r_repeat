from __future__ import annotations
from typing import Callable, TypeVar, Generic, Iterable
from functools import wraps, reduce
from contextlib import suppress
from random import random
from tqdm import tqdm

T = TypeVar('T')


class Repeatable(Callable, Generic[T]):
    f: Callable[..., T]
    args: tuple
    kwargs: dict
    i: int
    n: int
    repeat_enumerate: bool
    keep_cache: bool
    cache: list[T]

    __slots__ = ('f', 'args', 'kwargs', 'i', 'n', 'repeat_enumerate', 'keep_cache', 'cache')

    def __init__(self,
                 f: Callable[..., T],
                 /,
                 n: int,
                 repeat_enumerate: bool = False,
                 keep_cache: bool = False
                 ) -> None:
        self.f = f
        self.i = 0
        self.n = int(n)
        self.repeat_enumerate = repeat_enumerate
        self.keep_cache = keep_cache

    def __call__(self, *args, **kwargs) -> Repeatable[..., T]:
        """
        Passing the function parameters to the inner for ease of use.
        """
        self.args = args
        self.kwargs = kwargs
        self.i = 0
        return self

    def __len__(self) -> int:
        return self.n

    def __iter__(self) -> Repeatable[..., T]:
        self.i = 0
        return self

    def __next__(self) -> T:
        """
        Python magic for Iterables, allows this class to behave nicely in loops
        """
        if self.i >= len(self):
            raise StopIteration
        kwarg = self.kwargs
        if self.repeat_enumerate:
            kwarg['enumeration'] = self.i
        r = self.f(*self.args, **self.kwargs)
        if self.keep_cache:
            self.cache.append(r)
        self.i += 1
        return r

    def collect(self,
                collector: Callable[[T, T], T] | Callable[[T, T, int], T] | None = None,
                collector_enumerate: bool = False
                ) -> T:
        """
        Params:
            collector - the function to reduce the result set

            collector_enumerate - whether to pass the current index to the collector

        Returns:
             The reduced value
        """
        collector = collector or ((lambda a, b: a + b) if not collector_enumerate else (lambda a, b, i: a + b))
        if len(self.cache):
            res = reduce(collector, self.cache)
        else:
            res = next(self)
        for i, v in tqdm(enumerate(self), initial=self.i, total=self.n):
            if collector_enumerate:
                res = collector(res, v, self.i + i)
            else:
                res = collector(res, v)
        return res

    def drop(self, n: int) -> Repeatable[..., T]:
        """
        Params:
            n - the amount of items to drop, cache-first

        Returns:
             Self, for method chaining
        """
        n = int(n)  # allows for passing floats
        with suppress(StopIteration):
            for _ in range(n - len(self.cache)):
                next(self)
        if self.keep_cache:
            self.cache = self.cache[n:]
        return self


def repeat(
        func: Callable[..., T] = None,
        /,
        n: int = 1000,
        repeat_enumerate: bool = False,
        keep_cache: bool = False
        ) -> Repeatable[..., T] | Callable[[Callable[..., T]], Repeatable[..., T]]:
    """
    This is a decorator.

    Params:
        func - the function to wrap

        n - the number of repeats

        repeat_enumerate - whether to pass the index into the wrapped function

        keep_cache - whether to remember already generated results

    Returns:
        A Repeatable class instance based on the function decorated
    """
    n = int(n)  # if passed as 1e7, which is a float

    def g(f):
        return Repeatable(f, n, repeat_enumerate, keep_cache)
    if func is None:  # decorator magic to make calls without brackets work
        return g
    return g(func)


def seed(func: Callable[..., T] = None,
         /,
         kwarg: str | Iterable | None = None,
         transform: Callable = lambda x: x
         ) -> Callable[..., T]:
    """
    This is a decorator.

    Params:
        func - the function to seed randomness into

        kwarg - the parameter(s) to insert randomness into

        transform -  a function that wraps the random() call, used to change probability distribution

    Returns:
        A wrapped function, which will insert randomness on call
    """
    def g(f):
        @wraps(f)
        def h(*args, **kwargs):
            match kwarg:
                case [*_]:  # generic sequence
                    for i in kwarg:
                        kwargs[i] = transform(random())
                case str():
                    kwargs[kwarg] = transform(random())
                case _:
                    args = (*args, transform(random()))
            return f(*args, **kwargs)
        return h
    if func is None:  # decorator magic to make calls without brackets work
        return g
    return g(func)
