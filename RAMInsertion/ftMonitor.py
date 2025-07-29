from typing import Type
from NetFT import Sensor
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from time import sleep
import csv


def animate(i, ax, x_val: list, y_val: list, sensor: Sensor):
    if not isinstance(sensor, Sensor):
        raise(TypeError)
    fz = sensor.getForce()[2]*(-1.0)
    x_val.append(x_val[-1]+0.01)
    y_val.append(fz)

    x_val_disp = x_val[-100:]
    y_val_disp = y_val[-100:]

    ax.clear()
    ax.plot(x_val_disp, y_val_disp)






style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

x_val = [0]
y_val = [0]

sensor = Sensor('192.168.0.101')
myfile = open('foce_data.csv', 'w')


ani = animation.FuncAnimation(fig, animate, fargs=(ax1, x_val, y_val, sensor), interval=10)
plt.show()

writer = csv.writer(myfile)
writer.writerows(zip(x_val, y_val))

fig2 = plt.figure()
plt.plot(x_val, y_val)
plt.show()