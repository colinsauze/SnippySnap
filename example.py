from selenium import webdriver
from makereport import generate_report
import take_screenshot
'''Example SnippySnap application
This will screenshot two URLs using Selenium, then ask SnippySnap to compare it
to the previous screenshot and produce a report.
'''


def run():
    '''Runs everything'''

    # obtain a firefox web driver for Selenium
    browser = webdriver.Firefox()

    items = [("http://localhost/example/example1.html", "example1.png"),
             ("http://localhost/example/example2.html", "example2.png")]

    # lists for which images have/haven't changed
    unchanged_images = []
    changed_images = []

    for item in items:

        url = item[0]
        filename = item[1]

        # open the webpage
        browser.get(url)

        # do other webpage actions here

        # take a screenshot
        same = take_screenshot.take_screenshot(browser, filename)
        if same is True:
            unchanged_images.append(filename)
        else:
            changed_images.append(filename)

    browser.quit()

    generate_report("outputs/report.html")


if __name__ == '__main__':
    run()
