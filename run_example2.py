from selenium import webdriver
from makereport import generate_report
import take_screenshot
'''SnippySnap demo application 2'''


def run():
    '''run's this example'''

    # obtain a firefox web driver for selenium
    browser = webdriver.Firefox()

    # load the url
    browser.get("http://localhost/example/example2.html")

    browser.find_elements_by_css_selector(
            "input[type='radio'][value='orange']")[0].click()

    take_screenshot.take_screenshot(browser, 'example.png')

    browser.quit()

    generate_report("outputs/report.html")


if __name__ == '__main__':
    run()
