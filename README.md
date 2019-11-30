# memeify

Change all the symbol names and function names to different capitalizations of a given string.  
Note: This script has not been thoroughly tested, and the output may require some massaging.

test.py
```python
from math import pi

class Test(object):
    def __init__(self, n):
        self.n = n

    def test(self):
        return self.n * pi

    def boop(self):
        print(self.test())



x = Test(1)
x.boop()
```

```
python3 memeify.py test.py hee_hee Test,boop
python3 memeify.py [infile] [base name] [excludes]
```

out.py
```python
from math import pi

class Test(object):

    def __init__(self, hee_hee):
        self.hee_hee = hee_hee

    def Hee_hee(self):
        return (self.hee_hee * pi)

    def boop(self):
        print(self.Hee_hee())
hEe_hee = Test(1)
hEe_hee.boop()
```
