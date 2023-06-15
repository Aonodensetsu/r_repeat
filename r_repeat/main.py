from __future__ import annotations
from random import random
from functools import wraps
from typing import Callable, Optional, TypeVar, Generic
from tqdm import tqdm

T = TypeVar('T')


class Repeatable(Callable, Generic[T]):
    f: Callable[..., T]
    n: int
    repeat_enumerate: bool
    i: int
    args: tuple
    kwargs: dict

    def __init__(self, f: Callable[..., T], n: int, /, *args, repeat_enumerate: bool = False, **kwargs) -> None:
        self.f = f
        self.n = int(n)
        self.repeat_enumerate = repeat_enumerate
        self.i = 0
        self.args = args
        self.kwargs = kwargs

    def __call__(self, /, *args, repeat_enumerate: bool = False, **kwargs) -> Repeatable[..., T]:
        self.i = 0
        self.args = args
        self.kwargs = kwargs
        return self

    def __len__(self) -> int:
        return self.n

    def __iter__(self) -> Repeatable[..., T]:
        self.i = 0
        return self

    def __next__(self) -> T:
        if self.i < len(self):
            self.i += 1
            if not self.repeat_enumerate:
                return self.f(*self.args, **self.kwargs)
            else:
                return self.f(*self.args, **self.kwargs, enumeration=self.i)
        else:
            raise StopIteration


def repeat(
          func: Callable[..., T] = None,
          /,
          n: int | float = 1e3,
          repeat_enumerate: bool = False
          ) -> Repeatable[..., T] | Callable[[Callable[..., T]], Repeatable[..., T]]:
    n = int(n)  # if passed as 1e7, which is a float

    def g(f):
        return Repeatable(f, n, repeat_enumerate=repeat_enumerate)
    if func is None:
        return g
    else:
        return g(func)


def collect(
           f: Repeatable[..., T],
           /,
           collector: Optional[Callable[[T, T], T]] = None,
           collector_enumerate: bool = False
           ) -> T:
    collector = collector or ((lambda a, b: a + b) if not collector_enumerate else (lambda a, b, i: a + b))
    res = next(f)
    for i, v in tqdm(enumerate(f), total=len(f)):
        if not collector_enumerate:
            res = collector(res, v)
        else:
            res = collector(res, v, i)
    return res


def seed(
        func: Callable[..., T] = None,
        /,
        transform: Callable = lambda x: x,
        kwarg: str | list[str] = None
        ) -> Callable[..., T]:
    def g(f):
        if kwarg is None:
            @wraps(f)
            def h(*args, **kwargs):
                return f(*args, transform(random()), **kwargs)
        elif isinstance(kwarg, str):
            @wraps(f)
            def h(*args, **kwargs):
                kwargs[kwarg] = transform(random())
                return f(*args, **kwargs)
        else:
            @wraps(f)
            def h(*args, **kwargs):
                for i in kwarg:
                    kwargs[i] = transform(random())
                return f(*args, **kwargs)
        return h
    if func is None:
        return g
    else:
        return g(func)
