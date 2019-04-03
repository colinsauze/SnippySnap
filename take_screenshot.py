import os
import shutil
import imagecompare
from selenium import webdriver


def take_screenshot(browser, filename):
    '''Takes a screenshot of the requested webpage
    :param browser: an instance of a selenium webdriver
    :param filename: the filename to save as
    '''

    browser.save_screenshot(filename)

    #compare with the previous screenshot (if it exists)
    if os.path.isfile("old_screenshots/"+filename) == True:
        print("old image exists, comparing ",filename,"with old_screenshots/"+filename)
        same = imagecompare.compare_image(filename, "old_screenshots/"+filename, "comparison-"+filename, "mask-"+filename)
        if same == True:
            print(filename,"has not changed")
        else:
            print(filename,"has changed")
    else:
        print("old file doesn't exist")


    #if it doesn't exist make a directory for screenshots
    if os.path.exists("old_screenshots") != True:
        os.mkdir("old_screenshots")

    #copy the image
    shutil.copyfile(filename,"old_screenshots/"+filename)

def run():
    '''Runs all the tests everything'''
    browser = webdriver.Firefox()
    browser.get("http://www.bbc.co.uk/news") 
    take_screenshot(browser, 'bbc.png')
    browser.quit()

if __name__ == '__main__':
    run()
