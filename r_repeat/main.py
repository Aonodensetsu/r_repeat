from __future__ import annotations
from random import random
from functools import wraps
from typing import Callable, Optional, TypeVar, Generic

T = TypeVar('T')


class ProgressBar:
    detail: int
    showPercent: bool
    symbols: list
    started: bool = False
    percent: float = 0
    filled: int = 0
    partial: int = 0

    def __init__(self, detail: int = 30, showPercent: bool = True, symbols: Optional[list] = None) -> None:
        """Create a simple progress bar"""
        self.detail = detail
        self.showPercent = showPercent
        self.symbols = symbols or [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']

    def draw(self) -> None:
        """Draw the current state of the progress bar"""
        self.clearline()
        print('[' +  # start of bar
              self.filled * self.symbols[-1] +  # filled boxes
              self.symbols[self.partial] +  # partially filled box
              (self.detail - 1 - self.filled) * self.symbols[0] +  # empty boxes
              ']',  # end of bar
              end='')  # do not go to next line
        if self.showPercent:
            print(f' {self.percent:.1f}%', end='')

    def progress(self, fraction: float) -> None:
        """Update the state of the progress bar"""
        self.percent = 100 * fraction
        filled = int(self.detail * fraction)
        decimal = self.detail * fraction - filled
        partial = len(self.symbols) - 1
        frac = 1/len(self.symbols)
        for i in range(len(self.symbols)):
            if i * frac <= decimal < (i + 1) * frac:
                partial = i
                break
        if not self.started:  # first time drawing
            self.filled = filled
            self.partial = partial
            self.started = True
            self.draw()
        elif filled > self.filled:
            self.filled = filled
            self.partial = 0
            self.draw()
        elif partial > self.partial:
            self.partial = partial
            self.draw()

    @staticmethod
    def clearline() -> None:
        """Clear the terminal line"""
        print('\r\033[K', end='')


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
          n: int = 10**3,
          repeat_enumerate: bool = False
          ) -> Repeatable[..., T] | Callable[[Callable[..., T]], Repeatable[..., T]]:
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
           collector_enumerate: bool = False,
           progressbar_detail: int = 30
           ) -> T:
    collector = collector or ((lambda a, b: a + b) if not collector_enumerate else (lambda a, b, i: a + b))
    pb = ProgressBar(progressbar_detail)
    pb.progress(0)
    res = next(f)
    for i, v in enumerate(f):
        if not collector_enumerate:
            res = collector(res, v)
        else:
            res = collector(res, v, i)
        pb.progress(i / len(f))
    pb.progress(1)
    pb.clearline()
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
