import numpy
import matplotlib.pyplot as plt

# read numpy array map from file
map = numpy.load("or_map_new_6x6.npy")
print(map[3][1])
print(map[30][30]) # 0.956891128451
print(map.max()) # 0.99

# show map
plt.figure()
# pylab.imshow( map[7:-3,4:-6], interpolation='none', cmap='hsv')
plt.imshow( map, interpolation='none', cmap='hsv')
plt.show()