from selenium import webdriver
import take_screenshot

def run():

    # obtain a firefox web driver for selenium
    browser = webdriver.Firefox()

    items = [ ("http://www.bbc.co.uk/news", "bbc-news.png"), ("http://www.bbc.co.uk/news/uk", "bbc-news-uk.png") ]

    for item in items:

        url = item[0]
        filename = item[1]

        # open the webpage
        browser.get(url)

        # do other webpage actions here

        # take a screenshot 
        take_screenshot.take_screenshot(browser, filename)

    browser.quit()

if __name__ == '__main__':
    run()
