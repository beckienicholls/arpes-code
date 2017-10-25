import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# generate dummy data (graphene tight binding band structure)
kvec = np.linspace(-2*np.pi,2*np.pi,101)
kx,ky = np.meshgrid(kvec,kvec)
E = np.sqrt(1+4*np.cos(np.sqrt(3)*kx/2)*np.cos(ky/2) + 4*np.cos(ky/2)**2)

# plot full dataset
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(kx,ky,E,cmap='viridis_r',vmin=-E.max(),vmax=E.max(),rstride=1,cstride=1)
ax.plot_surface(kx,ky,-E,cmap='viridis_r',vmin=-E.max(),vmax=E.max(),rstride=1,cstride=1)


plt.savefig('tightbinding.jpg')
ax.set_xlabel('kx')
ax.set_ylabel('ky')
ax.set_zlabel('E')
ax.grid('off')
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
plt.show()
'''import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# generate dummy data (graphene tight binding band structure)

def fun(kx,ky):
    return np.sqrt(1+4*np.cos(np.sqrt(3)*kx/2)*np.cos(ky/2) + 4*np.cos(ky/2)**2)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
x = y = np.arange(-2*np.pi, 2*np.pi, 0.02)
kx, ky = np.meshgrid(x,y)
zs = np.array([fun(x,y) for x,y in zip(np.ravel(kx), np.ravel(ky))])
E = fun(kx,ky)
ax.plot_surface(kx,ky,E)
plt.show()
#fig = plt.figure()
#im = plt.imshow(E, cmap='inferno_r', interpolation='bicubic')  # Want to fix scale on each image
#cbar = plt.colorbar(im)

# focus on Dirac cones
#Elim = 1  #threshold
#E[E>Elim] = np.nan

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.plot_surface(kx2,ky2,E2,cmap='viridis',vmin=-Elim,vmax=Elim)
#ax.plot_surface(kx2,ky2,-E2,cmap='viridis',vmin=-Elim,vmax=Elim)
#ax.plot_surface(kx,ky,E,cmap='viridis',rstride=1,cstride=1,vmin=-Elim,vmax=Elim)
#ax.plot_surface(kx,ky,-E,cmap='viridis',rstride=1,cstride=1,vmin=-Elim,vmax=Elim)'''
