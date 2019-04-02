import cv2
import numpy as np

img1 = cv2.imread('1.png')
print(img1.dtype,img1.shape)
img2 = cv2.imread('2.png')


dt1 = np.dtype((np.uint32, (np.uint8, 4)))

width = img1.shape[1]
height = img1.shape[0]

img3 = np.ndarray(shape=[height, width], dtype=np.uint32)

#output images
img4 = np.ndarray(shape=[height, width,3 ], dtype=np.uint8)
mask = np.ndarray(shape=[height, width], dtype=np.uint8)

#print(img3.dtype,img3.shape)

#img3 = img1.view(dtype=dt1)

for y in range(0,height):
    for x in range(0,width):
        #print(type(img1[y][x]))
        b = img1[y][x][0]
        g = img1[y][x][1]
        r = img1[y][x][2]
        v1 = r + (g*256) + (b * 256**2)

        b = img2[y][x][0]
        g = img2[y][x][1]
        r = img2[y][x][2]
        v2 = r + (g*256) + (b * 256**2)
        
        if v1 != v2:
            img4[y][x][0] = 0
            img4[y][x][1] = 0
            img4[y][x][2] = 255
            mask[y][x]=255
        else:
            img4[y][x][0] = b
            img4[y][x][1] = g
            img4[y][x][2] = r
            mask[y][x]=0


cv2.imwrite("test3.png",img4)
cv2.imwrite("mask.png",mask)


