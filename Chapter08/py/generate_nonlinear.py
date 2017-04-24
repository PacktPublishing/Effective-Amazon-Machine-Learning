import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
# %matplotlib

n_samples = 100
# de_linearize = lambda X: np.cos(1.5 * np.pi * X) + np.cos( 5 * np.pi * X )

de_linearize = lambda x: np.cos(1.5 * np.pi * x)  + 0.1 *x**3 + 0.5 * x**2 - 2* x + 3

x =  np.sort(np.random.rand(n_samples))  *4 -2
y = de_linearize(x) + np.random.randn(n_samples) * 0.1


fig, ax = plt.subplots(1,1, figsize=(6,6))
ax.plot(x,y, '.')

