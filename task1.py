import pydicom as dicom
import numpy as np
import matplotlib.pyplot as plt
import os

path="VHF-Head\Head"
ct_images=os.listdir(path)

slices = [dicom.read_file(path+'/'+s,force=True) for s in ct_images]
#print(slices)
slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])
img_shape = list(slices[0].pixel_array.shape)
img_shape.append(len(slices))
volume3d=np.zeros(img_shape)

for i,s in enumerate(slices):
    array2D=s.pixel_array
    volume3d[:,:,i]= array2D
fig=plt.figure()
for i in range(img_shape[2]):
    plt.title("Axial")
    plt.imshow(volume3d[:,:,i])
    plt.pause(0.0000000005)
plt.pause(3)

for i in range(img_shape[1]):
    plt.title("Sagital")
    plt.imshow(volume3d[:,i,:])
    plt.pause(0.0000000005)
plt.pause(3)

for i in range(img_shape[0]):
    plt.title("Coronal")
    plt.imshow(volume3d[i,:,:].T)
    plt.pause(0.0000000005)

plt.show()










