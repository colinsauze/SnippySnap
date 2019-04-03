import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from makereport import generate_report
import take_screenshot



def wait_for(function_with_assertion, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            return function_with_assertion()
        except (AssertionError, WebDriverException):
            time.sleep(0.1)
    # one more try, which will raise any errors if they are outstanding
    return function_with_assertion()

def run():

    # obtain a firefox web driver for selenium
    browser = webdriver.Firefox()

    #load the url
    browser.get("http://localhost/example/example2.html")
    wait_for(lambda: assertTrue('SnippySnap Example Form 2' in browser.title))

    browser.find_elements_by_css_selector("input[type='radio'][value='orange']")[0].click()

    take_screenshot.take_screenshot(browser, 'example.png')

    browser.quit()

    # items = [ ("http://localhost/example/example1.html", "example1.png"), ("http://localhost/example/example2.html", "example2.png") ]
    #
    # # lists for which images have/haven't changed
    # unchanged_images = []
    # changed_images = []
    #
    # for item in items:
    #
    #     url = item[0]
    #     filename = item[1]
    #
    #     # open the webpage
    #     browser.get(url)
    #
    #     # do other webpage actions here
    #
    #     # take a screenshot
    #     same = take_screenshot.take_screenshot(browser, filename)
    #     if same == True:
    #         unchanged_images.append(filename)
    #     else:
    #         changed_images.append(filename)
    #
    # browser.quit()
    #
    # generate_report(changed_images, unchanged_images, "outputs/report.html")

if __name__ == '__main__':
    run()
