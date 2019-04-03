import os
import shutil
import imagecompare
from selenium import webdriver


def take_screenshot(browser, filename):
    '''Takes a screenshot of the requested webpage
    :param browser: an instance of a selenium webdriver
    :param filename: the filename to save as
    :return: true if image is the same, false if its different
    '''

    #if it doesn't exist make the outputs directory
    if os.path.exists("outputs") != True:
        os.mkdir("outputs")


    browser.save_screenshot("outputs/"+filename)
    same = True
    #compare with the previous screenshot (if it exists)
    if os.path.isfile("outputs/old_screenshots/"+filename) == True:
        print("old image exists, comparing ","outputs/"+filename,"with outputs/old_screenshots/"+filename)
        same = imagecompare.compare_image("outputs/"+filename, "outputs/old_screenshots/"+filename, "outputs/comparison-"+filename, "outputs/mask-"+filename)
        if same == True:
            print(filename,"has not changed")
        else:
            print(filename,"has changed")
    else:
        print("old file doesn't exist")


    #if it doesn't exist make a directory for screenshots
    if os.path.exists("outputs/old_screenshots") != True:
        os.mkdir("outputs/old_screenshots")

    #copy the image
    shutil.copyfile("outputs/"+filename,"outputs/old_screenshots/"+filename)
    return same

