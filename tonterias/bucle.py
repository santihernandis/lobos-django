import numpy as np

def bucle(a,b):
    a = a - b
    b = a + b
    a = b - 2*a
    return a,b

a = 12
b = 7

for i in range(100):
    a,b = bucle(a,b)
    print(a,b)