# Decorator magic
### This is what you're here for
This section describes functions you can use
<details><summary>Basic usage</summary>

```python
from r_repeat import repeat  # Import the used function

@repeat  # Repeat this function 1000 times
def f(args):
    ...

g = f('args')  # Start - here you can give function parameters as usual
# "g" is now an iterator, which will lazily give you results up to 1000 times
```
</details>
<details><summary>"Advanced" usage</summary>

```python
@repeat(n=1e6)  # Repeat a million times instead
```
</details>
<details><summary>Semi-advanced usage</summary>

Some functions might need to know how many times they have been run already    
This option is exposed by the `repeat_enumerate` keyword and inserts the current index into the "enumeration" parameter
```python
@repeat(repeat_enumerate=True)
def f(enumeration):
    ...
```
You might also want to log a few elements before collecting the results, but don't want to lose those initial values  
This can be achieved by the `keep_cache` keyword
```python
@repeat(keep_cache=True)
def f():
    ...
```
The function will keep track of the generated values until they're collected.
</details>
<details><summary>Simple result gathering</summary>

I'm continuing the code from Basic usage  
We now have a (lazy-loaded) list of 1000 results, so we need to gather the results somehow  
Usually this will end up being the average  
Native way:
```python
sum = 0 
for i in g:  # Gather all the results
    sum += i
average = sum / len(g)  # Get the average
```
This library provides a simple way to do just that
```python
average = g.collect() / len(g)  # Gather all the results and get the average
```
Note: This will also create a progess bar while the operation takes place, the option above would leave the terminal empty (and seemingly frozen) for the entire duration:
```
32%|███▏      | 318/1000 [00:15<00:47,  21.24it/s]
```
</details>
<details><summary>Advanced result gathering</summary>

Sometimes summing the results is not what we want, so we need to collect the results differently.  
This can be done by using the "collector" keyword in the collect function.  
The collector is a Callable, so you can use lambdas for simple colection.
The first argument is the current result, the second is the next element to collect
```python
# The default if you don't specify a collector
g.collect(collector=lambda a, b: a + b)
# Something else
g.collect(collector=lambda a, b: a * (b + 1))
```
For more complex collectors, you can define a function
```python
@repeat(n=10**3)
def f():
    # it's like
    return {'step forward': 1, 'steps back': 2}

def col(a, b):
    # Here, simply add each dictionary key separately
    a['step forward'] += b['step forward']
    a['steps back'] += b['steps back']
    return a

f().collect(collector=col)  # Use the col function for collecting
```
</details>
<details><summary>Some more advanced result gathering</summary>

Sometimes you also need the index while collecting results instead of just the elements themselves.  
This is available by setting the `collector_enumerate` keyword. The index is passed as the *third* parameter - so your collector function needs to change accordingly.
```python
# By default if you give the flag but don't specify the collector, the index will just be ignored
g.collect(collector_enumerate=True, collector=lambda a, b, i: a + b)
# A rolling average without knowing the length, using some math principles
g.collect(collector_enumerate=True, collector=lambda a, b, i: (a*(i+1)+b)/(i+2))
```
</details>
<details><summary>Seeding RNG</summary>

Many probabilistic functions need a few random values, which - when repeating the function many times - you need to remember to update  
When using the collect function, you can't change parameters in the middle of repeating, so you have to use the random functions directly in your code  
This will be totally usable in most circumstances, however you might sometimes have a function whose source code is out of your control  
This problem can be solved by `seeding` the function with random values via its parameters:
```python
from r_repeat import seed
@seed
def f(rng):
    # No access to the source code
    ...
```
By simply decorating the function with `@seed`, the last argument will be replaced by a random value on each run of the function  
You can specify the name of the parameter to fill:
```python
@seed(kwarg='rng')
def f(rng, bias):
    # "rng" has the random value, despite not being last
    ...
```
Or even seed multiple parameters:
```python
@seed(kwarg=['rng1', 'rng2', 'bias'])
def f(rng1, rng2, bias):
    # All parameters have a random value
    ...
```
</details>
<details><summary>Combined usage</summary>

Due to how decorators work in Python, their order matters a lot. In this case, the seeding needs to be applied before repeating, decorators are applied from closest to the function.
```python
@repeat  # applied second, the function that will be repeated has the random values inside it already
@seed  # applied first, the function itself gets the random values
def f():
    ...
```
WRONG:
```python
@seed  # applied to the repeating itself, will apply the same randomness to all calls
@repeat
def f():
    ...
```
</details>
<details><summary>Discarding results</summary>

You might want to keep only results after some initial tests, maybe for machine learning purposes.
You can drop the initial values by calling a function, which will first drop from cache if used, then generate and discard results
```python
g.cache  # [3, 2, 1]
g.drop(10)
g.cache  # []
# also generated 7 new results and discarded them
# dropping advances the index
```
*Actually*, first generates the results, then drops them from the cache at once
The drop method returns Self, to allow for method chaining
</details>
<details><summary>Complex example</summary>

```python
@repeat(n=1e4)
@seed(transform=lambda x: x**2)
def f(threshold, rng):
   return rng <= threshold

f(0.5).drop(1e3).collect(collector=lambda a, b, i: (a*(i+1)+b)/(i+2), collector_enumerate=True)
# average of 9000 values, where a random value squared is less than or equal one half
```
</details>

# Repeatable
### A data type used internally
This combines a Callable with an Iterator, allowing for usage that seems natural of the repeated functions
<details><summary>Available parameters</summary>

```python
f: Callable
# The function to repeat
n: int = 1000
# The amount of times to repeat
repeat_enumerate: bool = False
# Whether the inner function uses the index
keep_cache: bool = False
# Whether to keep uncollected results
```
</details>
