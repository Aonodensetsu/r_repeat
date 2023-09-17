## Simple library for gathering results from stochastic functions

![size](https://img.shields.io/github/languages/code-size/aonodensetsu/r_repeat) ![files](https://img.shields.io/github/directory-file-count/aonodensetsu/r_repeat)   
![py dep](https://img.shields.io/pypi/pyversions/r-repeat) [![version](https://img.shields.io/pypi/v/r-repeat)](https://pypi.org/project/r-repeat/0.3.6/)  
![license](https://img.shields.io/pypi/l/r-repeat) [![downloads](https://img.shields.io/badge/releases-here-green?logo=pypi)](https://pypi.org/project/r-repeat/#history)  
[![downloads](https://img.shields.io/badge/wiki-here-pink)](https://github.com/Aonodensetsu/r_repeat/blob/main/WIKI.md) [![downloads](https://img.shields.io/badge/changelog-here-pink)](https://github.com/Aonodensetsu/r_repeat/blob/main/CHANGELOG.md)  

# Usage:
1. `pip install r_repeat`
2. Open up [the wiki](https://github.com/Aonodensetsu/r_repeat/blob/main/WIKI.md) to see how everything works or check the examples
3. Enjoy

# Example:
```python
from r_repeat import repeat, seed
@repeat(n=1e6)  # run this function 1000000 times
@seed(kwarg=['rng1', 'rng2'])  # insert random numbers into rng1 and rng2
def f(rng1, bias, rng2):
	return (rng1 + bias) >= rng2

g = f(bias=0.078)  # pass remaining arguments
sum = g.collect()  # gather all results
print(f'{sum} wins and {len(g)-sum} losses')
```
Output:
```
22%|██▏       | 217913/1000000 [00:21<01:18,  9952.1it/s]    (while working)
574945 wins and 425055 losses    (after finished)
```
