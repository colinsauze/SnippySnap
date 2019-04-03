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

    if os.path.exists("outputs/screenshots") != True:
        os.mkdir("outputs/screenshots")


    browser.save_screenshot("outputs/screenshots/"+filename)
    is_different = False
    #compare with the previous screenshot (if it exists)
    if os.path.isfile("outputs/old_screenshots/"+filename) == True:
        print("old image exists, comparing ","outputs/screenshots/"+filename,"with outputs/old_screenshots/"+filename)
        is_different = imagecompare.compare_image("outputs/screenshots/"+filename, "outputs/old_screenshots/"+filename, "outputs/comparison-"+filename, "outputs/mask-"+filename)
        if is_different == True:
            print(filename,"has changed")
            status_file = open("outputs/"+filename+".status","w")
            status_file.write("changed")
            status_file.close()
        else:
            print(filename,"hasn't changed")
            # delete the mask and comparison image if they exist
            status_file = open("outputs/"+filename+".status","w")
            status_file.write("unchanged")
            status_file.close()

        #copy the image for the report
        print("copying outputs/old_screenshots/"+filename,"to outputs/report-"+filename)
        shutil.copyfile("outputs/old_screenshots/"+filename,"outputs/report-"+filename)


    else:
        print("old file doesn't exist")


    #if it doesn't exist make a directory for screenshots
    if os.path.exists("outputs/old_screenshots") != True:
        os.mkdir("outputs/old_screenshots")

    #copy the image
    shutil.copyfile("outputs/screenshots/"+filename,"outputs/old_screenshots/"+filename)
    return is_different

