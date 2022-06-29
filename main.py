import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
import skimage.io as io
import SimpleITK as sit_k
import os

interpolate_times = 0
smooth_positive_scale = 0.33
smooth_negative_scale = -0.34
smooth_iteration_times = 90
spacing = [3.0, 0.28125, 0.28125]


def save_img(image):
    for i in range(image.shape[0]):
        plt.imshow(image[i, :, :], cmap='gray')
        path = "./annotation/" + str(i + 1)
        plt.savefig(path)


def write_obj(vertices, faces, normals):
    obj = open('test.obj', 'w')
    for item in vertices:
        obj.write("v {0} {1} {2}\n".format(item[0], item[1], item[2]))

    for item in normals:
        obj.write("vn {0} {1} {2}\n".format(item[0], item[1], item[2]))

    for item in faces:
        obj.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0], item[1], item[2]))
    obj.close()


def interpolate(array):
    array1 = np.empty([0, array.shape[1], array.shape[2]])
    i = 0
    while i < array.shape[0] - 1:
        inter_array = (array[i] + array[i + 1]) / 2
        array1 = np.append(array1, [inter_array], axis=0)
        i = i + 1
    res = np.empty([0, array.shape[1], array.shape[2]])
    i0 = 0
    i1 = 0
    while i0 < array.shape[0] or i1 < array1.shape[0]:
        if i0 < array.shape[0]:
            res = np.append(res, [array[i0]], axis=0)
            i0 = i0 + 1
        if i1 < array1.shape[0]:
            res = np.append(res, [array1[i1]], axis=0)
            i1 = i1 + 1
    return res


def smoothing(vertices, neighbor, times):
    def update_vertices(scale):
        for cur, nei in enumerate(neighbor):
            nei_len = len(nei)
            sum_pos = np.array([0.0, 0.0, 0.0])
            for k in nei:
                sum_pos += vertices[k] - vertices[cur]
            vertices[cur] += scale * sum_pos / nei_len

    i = 0
    while i < times:
        update_vertices(smooth_positive_scale)
        update_vertices(smooth_negative_scale)
        i = i + 1
        print("smoothing_iteration: {0}/{1} ".format(i, times))
    return vertices


def get_neighbor(vertices, faces):
    length = vertices.shape[0]
    neighbor = [{} for _ in range(length)]
    for face in faces:
        if face[1] not in neighbor[face[0]]:
            neighbor[face[0]][face[1]] = 1
        if face[2] not in neighbor[face[0]]:
            neighbor[face[0]][face[2]] = 1
        if face[0] not in neighbor[face[1]]:
            neighbor[face[1]][face[0]] = 1
        if face[2] not in neighbor[face[1]]:
            neighbor[face[1]][face[2]] = 1
        if face[0] not in neighbor[face[2]]:
            neighbor[face[2]][face[0]] = 1
        if face[1] not in neighbor[face[2]]:
            neighbor[face[2]][face[1]] = 1
    return neighbor


def num(path):
    i = path.find("_")
    k = path[0: i]
    return int(k)


def get_list(path):
    for _, _, files in os.walk(path):
        return files


img_dir = "./img/"
img_list = get_list(img_dir)
img_list = sorted(img_list, key=num)
final_array = np.empty([0, 640, 640])
for img in img_list:
    print("reading: ", img_dir + img)
    img_array = io.imread(img_dir + img)
    slice_array = np.empty([img_array.shape[0], img_array.shape[1]])
    for p in range(img_array.shape[0]):
        for q in range(img_array.shape[1]):
            if img_array[p, q, 0] > 0:
                slice_array[p, q] = 1
            else:
                slice_array[p, q] = 0
    final_array = np.append(final_array, [slice_array], axis=0)
print("dataset size: ", final_array.shape)

# itk_img = sit_k.ReadImage('./nii/annotation.nii')
# img = sit_k.GetArrayFromImage(itk_img)
# save_img(img)

img = final_array

# interpolate between slices

denominator = 2 ** interpolate_times
while interpolate_times > 0:
    img = interpolate(img)
    interpolate_times = interpolate_times - 1

v, f, n, values = measure.marching_cubes(img, 0.01, spacing=[spacing[0] / denominator, spacing[1], spacing[2]])
neighbors = get_neighbor(v, f)
v = smoothing(v, neighbors, smooth_iteration_times)
f = f + 1
write_obj(v, f, n)
