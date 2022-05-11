import selenium.webdriver.chromium.webdriver

from DriverKit import SDKit


def getESPNPlyrUniverse(url: str):
    sdrvr = SDKit(headless=False).driver
    sdrvr.get(url)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    getESPNPlyrUniverse(url="https://www.espn.com/fantasy/baseball/story/_/id/33208450/fantasy-baseball-rankings-head"
                            "-head-category-rotiserrie-leagues-2022")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
