import cv2
import numpy as np


def compare_image(file1, file2, changes_file, mask_file):
    '''Compares and highlights the differences between two images
    :param file1: The first image file
    :param file2: The second image file
    :param changes_file: File to highlight differences in
    :param mask_file: The output showing a mask of only the changed pixels
    :return: True if the image has changed, false if it hasn't
    '''

    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)

    dt1 = np.dtype((np.uint32, (np.uint8, 4)))

    width1 = img1.shape[1]
    height1 = img1.shape[0]
    width2 = img2.shape[1]
    height2 = img2.shape[0]

    if width1 != width2:
        print("Error: width's different, image1 = ", width1, "image2 = ",
              width2)
        return
    if height1 != height2:
        print("Error: height's different, image1 = ", height1,
              "image2 = ", height2)
        return

    # output images
    changes_img = np.ndarray(shape=[height1, width1, 3], dtype=np.uint8)
    mask_img = np.ndarray(shape=[height1, width1], dtype=np.uint8)

    is_different = False

    # Loops through every pixel in the image and compares it
    # FIXME: this is really suboptimal but I couldn't numpy magic to work
    for y in range(0, height1):
        for x in range(0, width1):
            # combine the R, G and B channels into one value for comparison
            b = img1[y][x][0]
            g = img1[y][x][1]
            r = img1[y][x][2]
            v1 = r + (g*256) + (b * 256**2)

            b = img2[y][x][0]
            g = img2[y][x][1]
            r = img2[y][x][2]
            v2 = r + (g*256) + (b * 256**2)

            # see if the pixels are different
            # highlight the changes in both the changes image and mask
            if v1 != v2:
                # invert the changed pixels
                changes_img[y][x][0] = 255 - img2[y][x][0]
                changes_img[y][x][1] = 255 - img2[y][x][1]
                changes_img[y][x][2] = 255 - img2[y][x][2]
                # make mask white
                mask_img[y][x] = 255
                is_different = True
            else:
                # justcopy the pixels
                changes_img[y][x][0] = b
                changes_img[y][x][1] = g
                changes_img[y][x][2] = r
                # leave mask black
                mask_img[y][x] = 0

    cv2.imwrite(changes_file, changes_img)
    cv2.imwrite(mask_file, mask_img)
    return is_different
