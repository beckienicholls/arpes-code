"""Program to kWarp ARPES data directly from NeXus files. Program outputs the kWarped cube as a new NeXus file which
can be displayed in DAWN."""

import h5py
import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
from scipy import interpolate
from NeXus_warping_GUI import *
from nexusformat.nexus import *

try:
    f = h5py.File(filename, 'r')
    programtype = f['/entry1/program_name']
except:
    print("Invalid filename. Program terminated.")
    sys.exit()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#      This section should be adapted when new versions are implemented     #
#                                                                           #
#      Change the choice names 'GDA X.X.X.' to the relevant versions        #
#                                                                           #
#      Change the path names to what they appear as in the .nxs tree        #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if choice == 'User Specified':
    try:
        print(datapath, energypath)
        dset1 = f[datapath]
        dset2 = f[energypath]
        dset3 = f[anglespath]
        dset4 = f[anapolarpath]
    except:
        print("Invalid paths within nxs file. Try a different version of DAWN or check the nxs tree.")
        sys.exit()

if choice == 'GDA 8.52.0':  # This works for the file i05-1-3475.nxs;
    try:
        dset1 = f['/entry1/instrument/analyser/data']  # 3D Intensity Datacube
        dset2 = f['/entry1/instrument/analyser/energies']  # 1D Energy Vector
        dset3 = f['/entry1/instrument/analyser/angles']  # 1D Angles (theta) Vector
        dset4 = f['/entry1/instrument/anapolar/anapolar']  # 1D Anapolar Angle (phi) Vector

    except:  # If the paths do not match up with those inside the nxs file, program terminates
        print("Invalid paths within nxs file. Try a different version of DAWN or check the nxs tree.")
        sys.exit()

elif choice == 'GDA 9.1.0':  # This is the version for files i05-1-5470.nxs, i05-1-5370.nxs
    try:
        dset1 = f['/entry1/instrument/analyser/data']
        dset2 = f['/entry1/instrument/analyser/energies']
        dset3 = f['/entry1/instrument/analyser/angles']
        dset4 = f['/entry1/instrument/analyser/analyser_polar_angle']
    except:
        print("Invalid paths within nxs file. Try a different version of DAWN or check the nxs tree.")
        sys.exit()

# Datacube comes in form (x,y,z) where x = anapolar, y = angles, z = energies
# Want to rotate the cube to put it in the form (z,y,x) to make the slicing easier later on
chunkCube = np.rot90(dset1, axes=(0, -1))
chunkCube = chunkCube[::-1, :, :]
dimInfoWave = np.shape(chunkCube)  # Defines the dimensions of the rotated datacube (ChunkChube)
deltaInfoWave = [dset2[1] - dset2[0], dset3[1] - dset3[0], dset4[1] - dset4[0]]  # Defines step sizes for E, theta, phi
offsetInfoWave = [dset2[0], dset3[0], dset4[0]]  # Defines start points for E, theta, phi

alpha = 0.512317  # Constants defined for E in eV and theta/phi in degrees
degree = np.pi / 180  # Conversion factors
radian = 1 / degree

# Defining the dimensions of the new warped grid; Takes the k values from the GUI
E_pix = np.shape(chunkCube)[0]  # Number of energy steps possible

# Defining start, delta and end points for all of the variables
Estart = offsetInfoWave[0]
Edelta = deltaInfoWave[0]
Eend = Estart + ((E_pix - 1) * Edelta)

theta_a_start = offsetInfoWave[1]
theta_a_delta = deltaInfoWave[1]
theta_a_size = np.shape(chunkCube)[1]

theta_d_start = offsetInfoWave[2]
theta_d_delta = deltaInfoWave[2]
theta_d_size = np.shape(chunkCube)[2]

# Takes in the gamma offset1 from the GUI and corrects the scales
theta_analyser_corr = gammaoff1
theta_a_start = theta_a_start - theta_analyser_corr
theta_a_end = theta_a_start + (theta_a_size * theta_a_delta)

# Takes in the gamma offset2 from the GUI and corrects the scales
theta_deflector_corr = gammaoff2
theta_d_start = theta_d_start - theta_deflector_corr
theta_d_end = theta_d_start + (theta_d_size * theta_d_delta)

# Takes in the workfunction from the GUI
work_function = workfunction

# Finding max and min values of kx and ky, setting kwarped scale
kxstart = alpha * np.sqrt(Eend) * np.sin(degree * theta_d_start)  # min
kxend = alpha * np.sqrt(Eend) * np.sin(degree * theta_d_end)  # max

# 0.8 is just a factor of the apparatus, scale stretching
kystart = 0.8 * alpha * np.sqrt(Eend) * np.sin(degree * theta_a_start)  # min
kyend = 0.8 * alpha * np.sqrt(Eend) * np.sin(degree * theta_a_end)  # max

# Calculate step sizes for warped grid
kxdelta = (kxend - kxstart) / (kxpixels - 1)
kydelta = (kyend - kystart) / (kypixels - 1)

# Define empty lists for storage
bindingenergylist = []
kineticenergylist = []
kxlist = []
kylist = []

# Create a new array of zeroes where interpolated data will be put
warped_3D = np.zeros((E_pix, kxpixels, kypixels))
theta_a_space = np.arange(theta_a_start, theta_a_end, theta_a_delta)  # Specify scale of original data
theta_d_space = np.arange(theta_d_start, theta_d_end, theta_d_delta)


for i in range(0, E_pix):  # Iterate through slices of constant energy
    energy = Estart + i * Edelta  # Specify the energy of the slice

    kineticenergylist.append(energy)    # Add energies to list, Ebin = - Ekin - workfunction
    bindingenergylist.append(energy - work_function)

    alpha_E = alpha * np.sqrt(energy)  # Redefine a constant involving alpha
    angles2D = chunkCube[i]  # Pull out the slice of intensity data from the original datacube

    for j in range(0, kypixels):  # Iterate through lines of constant ky
        ky = kystart + j * kydelta
        if i == 0:  # On the first energy iteration, add the ky values to empty list
            kylist.append(ky)

        theta_d_list = []  # Create empty lists to store new theta a and d;
        theta_a_list = []  # Faster to interpolate through list than by each element directly during loop

        for k in range(0, kxpixels):  # Iterate through kx elements
            kx = kxstart + k * kxdelta

            if i == 0 and j == 0:  # On the first energy and ky iteration, add kx values to empty list
                kxlist.append(kx)

            absk = np.sqrt(kx ** 2 + ky ** 2)  # Work 'backwards' to find associated angles for each (kx,ky) point
            theta = np.arcsin(absk / alpha_E)  # These correspond to angles from the original scale of the slice
            theta_d = np.arcsin(kx / alpha_E)
            theta_a = np.arccos(np.cos(theta) / np.cos(theta_d))

            if ky < 0:  # Specifies the correct quadrant
                theta_a = -abs(theta_a)
            else:
                theta_a = abs(theta_a)

            theta_d_list.append(theta_d * radian)
            theta_a_list.append(theta_a * radian)

        # Define an interpolation function by inputting original grid scales and the slice
        funct = interpolate.interp2d(theta_d_space, theta_a_space, angles2D)
        # Place the interpolated values into the empty warped array
        for x in range(len(theta_a_list) - 1):
            warped_3D[i][x][j] = funct(theta_d_list[x], theta_a_list[x])

    print(str(i + 1) + "/" + str(dimInfoWave[0]))  # Could try to replace this with a progress bar

# If the GUI output field is left empty, saves as a default name
if save == '':
    saved = os.path.basename(filename)
    newname = os.path.splitext(saved)
    namename = str(newname[0]) + "_warped" + str(newname[1])
    if not os.path.exists(namename):
        g = h5py.File(namename)
    elif os.path.exists(namename):
        j = 0
        while os.path.exists(str(newname[0]) + "_warped" + str(j) + str(newname[1])):
            j += 1
        else:
            g = h5py.File(str(newname[0]) + "_warped" + str(j) + str(newname[1]))

else:
    g = h5py.File(str(save))

# Creates the new .nxs file; Would be beneficial to duplicate the old file to retain all other information.
nxentry = g.create_group('entry')
nxentry.attrs['NX_class'] = 'NXentry'
nxentry.attrs['default'] = 'warped'
nxentry.create_dataset('title', data='kwarping')

nxdata = nxentry.create_group('warped data')
nxdata.attrs['NX_class'] = 'NXdata'

warpedCube = nxdata.create_dataset('Warped Datacube', data=warped_3D)
energy_axis = nxdata.create_dataset('Kinetic energy', data=kineticenergylist)
binding_energy = nxdata.create_dataset('Binding energy', data=bindingenergylist)
kx_axis = nxdata.create_dataset('kx', data=kxlist)
ky_axis = nxdata.create_dataset('ky', data=kylist)

g.close()
