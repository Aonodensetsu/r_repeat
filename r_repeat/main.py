from math import floor
from random import random
from functools import wraps


class ProgressBar:
    started = 0
    percent = 0
    length = 0
    filled = 0
    partial = 0
    symbols = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']

    def __init__(self, length):
        self.length = length

    def draw(self):
        print('\r[' + self.filled * self.symbols[8] + self.symbols[self.partial] + (self.length - 1 - self.filled) * ' ' + '] ' + f'{self.percent:.2f}%', end='')

    def progress(self, percent):
        self.percent = 100 * percent
        filled = floor(self.length * percent)
        decimal = self.length * percent - filled
        if 0 <= decimal < 0.125:
            partial = 0
        elif 0.125 <= decimal < 0.25:
            partial = 1
        elif 0.25 <= decimal < 0.375:
            partial = 2
        elif 0.375 <= decimal < 0.5:
            partial = 3
        elif 0.5 <= decimal < 0.625:
            partial = 4
        elif 0.625 <= decimal < 0.75:
            partial = 5
        elif 0.75 <= decimal < 0.875:
            partial = 6
        elif 0.875 <= decimal < 1:
            partial = 7
        else:
            partial = 8
        if not self.started:
            self.started = 1
            self.draw()
        elif filled > self.filled:
            self.filled = filled
            self.partial = 0
            self.draw()
        elif partial > self.partial:
            self.partial = partial
            self.draw()

    def clear(self):
        print('\r\033[K', end='')


class Repeater:
    pb: ProgressBar

    def __init__(self, progressbar_length=30):
        self.pb = ProgressBar(progressbar_length)

    def collect(self, f, /, *args, col=lambda a, b: a + b, **kwargs):
        self.pb.progress(0)
        gen = f(*args, **kwargs)
        res = next(gen)
        for i, v in enumerate(gen):
            res = col(res, v)
            self.pb.progress(i / len(gen))
        self.pb.progress(1)
        self.pb.clear()
        return res

    @staticmethod
    def repeat(func=None, /, n=1):
        def g(f):
            class H:
                def __init__(self, *args, **kwargs):
                    self.i = 0
                    self.args = args
                    self.kwargs = kwargs

                def __call__(self, *args, **kwargs):
                    self.__init__(*args, **kwargs)
                    return self

                def __len__(self):
                    return int(n)

                def __iter__(self):
                    self.i = 0
                    return self

                def __next__(self):
                    if self.i < len(self):
                        self.i += 1
                        return f(*self.args, **self.kwargs)
                    else:
                        raise StopIteration
            return H
        if func is None:
            return g
        else:
            return g(func)

    @staticmethod
    def seed(func=None, /, transform=lambda x: x, kwarg=None):
        def g(f):
            @wraps(f)
            def h(*args, **kwargs):
                if kwarg is None:
                    return f(*args, transform(random()), **kwargs)
                else:
                    kwargs[kwarg] = transform(random())
                    return f(*args, **kwargs)
            return h
        if func is None:
            return g
        else:
            return g(func)
