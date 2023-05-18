# Repeater
### This is what you're here for
This section describes functions you can use
<details><summary>Basic usage</summary>

```python
from r_repeat import repeat  # Import the used function

@repeat  # Repeat this function 1000 times
def f():
    ...

g = f()  # Start - here you can give function parameters as usual
# "g" is now a generator, which will lazily give you results up to 1000 times
```
</details>
<details><summary>"Advanced" usage</summary>

```python
@repeat(n=10**6)  # Repeat a million times instead
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
</details>
<details><summary>Simple result gathering</summary>

I'm continuing the code from above  
We now have a (lazy-loaded) list of 10000 results, so we need to gather the results somehow  
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
from r_repeat import collect
average = collect(g) / len(g)  # Gather all the results and get the average
```
Note: This will also create a progess bar while the operation takes place, the option above would leave the terminal empty (and seemingly frozen) for the entire duration:
```
[███████▋                      ] 25.2%
```
<details><summary>Equivalent without collect</summary>

The equivalent code without using the collect function (but still using this library for the ProgressBar) would be the following:
```python
from r_repeat import ProgressBar
sum = 0
pb = ProgressBar()  # Create the bar
for i, v in enumerate(g):  # You need to track the progress with enumerate
    sum += v
    pb.progress(i / len(g))  # Update the bar to the currently completed fraction
pb.clearline()  # Clear the line
average = sum / len(g)
```
<details><summary>Equivalent without library (for fun, don't actually use this)</summary>

```python
sum = 0
for i, v in enumerate(g):  # You need to track the progress with enumerate
    sum += v
    # Update the bar to the currently completed fraction
    symbols = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    fraction = i / len(g)
    percent = 100 * fraction
    filled = int(30 * fraction)
    decimal = 30 * fraction - filled
    partial = 7
    frac = 1/8
    for j in range(8):
        if j * frac <= decimal < (j + 1) * frac:
            partial = j
            break
    print('\r\033[K[' + filled * symbols[-1] + symbols[partial] + (29 - filled) * symbols[0] + ']' + f' {percent:.1f}%', end='')
print('\r\033[K', end='')
average = sum / len(g)
```
</details>
</details>

You may also choose to forgo calling the function at all if you use the collect function

```python
sum = collect(f)
# len() still needs a "started" function, so you need the parentheses, they can be empty even if your function takes parameters
average = sum / len(f())
```
</details>

<details><summary>Advanced result gathering</summary>

Sometimes summing the results is not what we want, so we need to collect the results differently.  
This can be done by using the "collector" keyword in the collect function.  
The collector is a Callable, so you can use lambdas for simple colection.
The first argument is the current result, the second is the next element to collect
```python
# The default if you don't specify a collector
collect(f, collector=lambda a, b: a + b)
# Something else
collect(f, collector=lambda a, b: a * (b + 1))
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

collect(f, collector=col)  # Use the col function for collecting
```
</details>
<details><summary>Some more advanced result gathering</summary>

Sometimes you also need the index while collecting results instead of just the elements themselves.  
This is available by setting the `collector_enumerate` keyword. The index is passed as the *third* parameter - so your collector function needs to change accordingly.
```python
# By default if you give the flag but don't specify the collector, the index will just be ignored
collect(f, collector_enumerate=True, collector=lambda a, b, i: a + b)
```
</details>
<details open><summary>Seeding RNG</summary>

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

# Repeatable
### A data type used internally
This combines a Callable with a Generator, allowing for usage that seems natural of the repeated functions
<details><summary>Available parameters</summary>

```python
f: Callable[..., Any]
# The function to repeat
n: int
# The amount of times to repeat
```
</details>

# ProgressBar
### A simple, nice looking progress bar
Also used in the collect function
<details><summary>Available parameters</summary>

```python
detail: int = 30
# Determines the length of the progress bar in characters
showPercent: bool = True
# Whether to show the current percentage as well
symbols: list = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
# The list of symbols to use in the progress bar, sorted from "emptiest" to "fullest"
```
</details>
