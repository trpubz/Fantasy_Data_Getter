"""
Specifically webscraping and parsing handlers.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 0.1.0
modified: 03 AUG 2023
by pubins.taylor
"""
from time import sleep
import re

import selenium.webdriver.chrome.webdriver
from driverkit.DriverKit import DKDriverConfig
from src import IOKit
from src.Globals import dirHQ

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag


def getESPNPlyrUniverse(url: str, headless: bool = True):
    """
    Function that navigates to the league's player rater URL.
    :param url: string corresponding to the article destination.  This changes from preseason to regular season
    :param headless: boolean that determines whether to run the browser in headless mode
    :return: none
    """
    sdrvr: webdriver.Chrome = DKDriverConfig(dirDownload=dirHQ, headless=headless)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)

    # sort the page by %Rostered
    pctRosteredColumn = sdrvr.find_element(By.XPATH, "//th[div[span[contains(text(),'%ROST')]]]")
    pctRosteredColumn.click()
    sleep(2.6)
    # get the position radio buttons
    pickerGroup = sdrvr.find_element(By.CSS_SELECTOR, "#filterSlotIds")
    position_buttons = pickerGroup.find_elements(By.TAG_NAME, "label")
    # create empty table to hold the combined data
    # this table will combine all the pages of data into one table
    combinedTable = BeautifulSoup('', 'lxml').new_tag('table')
    for button in position_buttons:
        posGroup = button.text
        if posGroup == "Batters" or posGroup == "Pitchers":
            try:
                # page requires dynamic loading and the initial state is required to be compared to expected state
                initialStatePlayerTable = sdrvr.find_element(By.CSS_SELECTOR, "tbody.Table__TBODY").text
                button.click()
                # give the page time to load
                WebDriverWait(sdrvr, 5).until(
                    lambda _: expectedTableLoaded(initialStatePlayerTable, sdrvr)
                )
                print(f"Processing {posGroup} group")

                combinedTable.append(parsePosGroup(sdrvr, posGroup))

            except Exception as e:
                print(f"An error occurred in getESPNPlyrUniverse while processing {posGroup}. Error message: {e}")
                continue

    # add the combined table to the rawHTML list
    rawHTML = combinedTable.prettify()
    assert len(rawHTML) > 0, "rawHTML is empty, run again"
    # write out the combined table to a file
    sdrvr.close()
    IOKit.writeOut(fileName="tempESPNPlayerUniverse", ext=".html", content=rawHTML)
    return rawHTML


def expectedTableLoaded(initialState, driver: webdriver.Chrome):
    return initialState != driver.find_element(By.CSS_SELECTOR, "tbody.Table__TBODY").text


def parsePosGroup(sdrvr: webdriver, posGroup: str) -> Tag:
    """
    Function that parses the HTML of multiple position group pages and returns the table of player data
    :param sdrvr: webdriver object
    :param posGroup: "Batters" or "Pitchers"
    :return: a combined table of player data
    """
    combinedTable = BeautifulSoup('', 'lxml').new_tag('table')
    page = 1
    pctRostered: float = 99.9
    tableRows: list[str] = []
    while pctRostered > 1.0 or page < 3:
        try:
            WebDriverWait(sdrvr, 7).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, "tbody.Table__TBODY")))
            # get the HTML of the page and parse it with BeautifulSoup
            soup = BeautifulSoup(sdrvr.page_source, 'lxml')
            # there are 2 tables on the page,
            # the first is the player names and the second is the player rater data
            tables = soup.find_all('table')[:2]

            # there are 2 header rows, shed the first one with [1:] slicing
            playerInfoColumns = tables[0].find_all('tr')[1:]
            playerRaterColumns = tables[1].find_all('tr')[1:]
            # add the same rows from each table to the combined table
            pctRostered: float
            for i in range(0, len(playerInfoColumns)):
                if i == 0 and page == 1 and posGroup == "Batters":  # only add the headers once
                    headers = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                    combinedHeaderRow = BeautifulSoup('', 'lxml').new_tag('thead')
                    for header in headers:
                        combinedHeaderRow.append(header)
                    # print(combinedHeaderRow)
                    combinedTable.append(combinedHeaderRow)
                elif i > 0:
                    wholeRow = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                    combinedPlayerRow = BeautifulSoup('', 'lxml').new_tag('tr')
                    for plyr in wholeRow:
                        combinedPlayerRow.append(plyr)
                    # updated the pctRostered variable
                    pctRostered = float(combinedPlayerRow.select_one("div[title*='rostered']").string)
                    if not isDuplicateRow(combinedPlayerRow, tableRows):
                        tableRows.append(str(combinedPlayerRow))
                        combinedTable.append(combinedPlayerRow)
                else:
                    continue  # if i (row) == 0 on any other page, then skip it
            # go to the next page
            print(f"Finished processing page {page} for {posGroup}")
            page += 1
            # always to click to next page, pctRostered will be checked at the top of the loop
            sleep(.3)
            next_button = WebDriverWait(sdrvr, 7).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.Button.Pagination__Button--next")))
            # scroll button into view before clicking
            # ActionChains(sdrvr).move_to_element(next_button).perform()
            next_button.click()
            sleep(1.6)

        except Exception as e:
            print(f"An error occurred while processing page {page}. Error message: {e}")
            continue

    if page < 4:
        print(f"Only {page - 1} pages were processed for {posGroup}. \n should check failure")

    print(f"The lowest %Rostered for {posGroup} group was {pctRostered}")
    print(f"A total of {page - 1} pages were processed for {posGroup} group. \n" +
          f"{len(combinedTable)} players added")
    assert len(combinedTable) > 0, "No players were added to the combined table"
    return combinedTable


def isDuplicateRow(row: Tag, tableRows: list[str]) -> bool:
    """
    Function that checks to see if a row is already in the tableRows list
    :param row: a row of player data
    :param tableRows: a list of rows of player data
    :return: True if the row is already in the list, False if it is not
    """
    idLoc: str = row.find("img").get("data-src") or row.find("img").get("src")
    espnID = re.findall(r'full/(\d+)\.png', idLoc)[0]
    if str(row) not in tableRows:
        return False
    else:
        # check to make sure Shohei Ohtani is not in the table more than twice
        shoheis = filter(lambda x: "39382" in x, tableRows)
        listShoheis = list(shoheis)
        if espnID == "39382" and len(listShoheis) < 2:
            return False
        else:
            print("duplicate row found, skipping table")
            return True