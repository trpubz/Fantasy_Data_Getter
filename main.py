import selenium.webdriver.chromium.webdriver
from selenium.webdriver.common.by import By
import DriverKit


def getESPNPlyrUniverse(url: str):
    sdrvr = DriverKit.driver_config(dirDownload='/Users/Shared/Baseball HQ', headless=False)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)
    elmArticle = sdrvr.find_element(By.CSS_SELECTOR, 'div.article-body')
    rawHTML = elmArticle.get_attribute("innerHTML")
    sdrvr.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    getESPNPlyrUniverse(url="https://www.espn.com/fantasy/baseball/story/_/id/33208450/fantasy-baseball-rankings-head"
                            "-head-category-rotiserrie-leagues-2022")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
