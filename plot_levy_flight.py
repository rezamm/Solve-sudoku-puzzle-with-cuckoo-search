import numpy as np
import matplotlib.pyplot as plt


def f(t):
    return np.power(t, -1.0 / 3.0)


x = np.arange(0.0001, 0.9999, 0.000001)
y = f(x)

# more than 2 count
count = len(np.where(y > 1.7)[0])
all = len(y)
print('More than 2: {}%'.format((count / all)))

plt.figure(1)
plt.subplot(211)
plt.plot(x, y, 'bo', markersize=1)
plt.show()
