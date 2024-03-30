"""
Specifically webscraping and parsing handlers.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 3.0.1
modified: 30 MAR 2024
by pubins.taylor
"""
from time import sleep
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag

from mtbl_driverkit.mtbl_driverkit import dk_driver_config, TempDirType
import mtbl_iokit.write

from app.src.mtbl_globals import ETLType


class Scraper:
    def __init__(self,
                 directory: tuple[TempDirType, str],
                 etl_type: ETLType,
                 headless: bool = False):
        """
        Combined table used for REGSZN. Bats and Arms used for PRESZN.
        :param directory: The directory tuple for the app
        :param etl_type: PRESZN or REGSZN
        :param headless: boolean to run the browser in headless mode
        """
        self.directory = directory
        self.driver, _ = dk_driver_config(directory, headless=headless)
        self.etl_type = etl_type
        # create empty table to hold the combined data
        # this table will combine all the pages of data into one table
        self.combined_table = BeautifulSoup('', 'lxml').new_tag('table')
        self.bats = BeautifulSoup('', 'lxml').new_tag('table')
        self.arms = BeautifulSoup('', 'lxml').new_tag('table')

    def get_espn_plyr_universe(self, url: str):
        """
        Navigates to the league's player rater URL and scrapes the pages & stores in temp file.
        :param url: string corresponding to the article destination.
                    This changes from preseason to regular season
        :return: None
        """
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        self.prep_extract()

        # get the position radio buttons
        picker_group = self.driver.find_element(By.CSS_SELECTOR, "#filterSlotIds")
        position_buttons = picker_group.find_elements(By.TAG_NAME, "label")

        for button in position_buttons:
            pos_group = button.text
            if pos_group == "Batters" or pos_group == "Pitchers":
                try:
                    # page requires dynamic loading and the initial state is required to be compared
                    # to expected state
                    initial_state_player_table = (self.driver.find_element(
                        By.CSS_SELECTOR, "tbody.Table__TBODY").text)
                    # if the label is already selected, clicking the label with throw
                    # ElementClickInterceptedException()
                    if not button.get_attribute("class").__contains__("checked"):
                        button.click()
                        # give the page time to load
                        WebDriverWait(self.driver, 5).until(
                            lambda _: self.expected_table_loaded(initial_state_player_table)
                        )
                    print(f"Processing {pos_group} group")

                    match self.etl_type:
                        case ETLType.REG_SZN:
                            self.combined_table.append(self.parse_pos_group(pos_group))
                        case ETLType.PRE_SZN:
                            match pos_group:
                                case "Batters":
                                    self.bats = self.parse_pos_group(pos_group)
                                case "Pitchers":
                                    self.arms = self.parse_pos_group(pos_group)

                except Exception as e:
                    print(f"An error occurred in while processing {pos_group}. "
                          f"Error message: {e}")
                    continue

        self.driver.close()
        self.write_out_html()

    def parse_pos_group(self, pos_group: str) -> Tag:
        """
        Function that parses the HTML of multiple position group pages and returns the table of
        player data.
        :param pos_group: "Batters" or "Pitchers"
        :return: a combined table of player data
        """
        combined_table = BeautifulSoup('', 'lxml').new_tag('table')
        page = 1
        # ignored for PRESZN projections but page value is sufficient control
        pct_rostered: float = 99.9
        table_rows: list[str] = []
        while pct_rostered > 1.0 and page < 7:  # 6 total pages will yield 300 players per pos group
            try:
                WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, "tbody.Table__TBODY")))
                # get the HTML of the page and parse it with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                # there are 2 tables on the page,
                # the first is the player names and the second is the player rater data
                tables = soup.find_all('table')[:2]

                # there are 2 header rows, shed the first one with [1:] slicing
                player_info_rows = tables[0].find_all('tr')[1:]
                player_stat_rows = tables[1].find_all('tr')[1:]
                # add the same rows from each table to the combined table
                for i in range(0, len(player_info_rows)):
                    if i == 0 and page == 1 and (
                            pos_group == "Batters" and self.etl_type == ETLType.REG_SZN or
                            pos_group == "Pitchers" and self.etl_type == ETLType.PRE_SZN):
                        # only add the headers once
                        headers = player_info_rows[i].contents + player_stat_rows[i].contents
                        combined_header_row = BeautifulSoup('', 'lxml').new_tag('thead')
                        for header in headers:
                            combined_header_row.append(header)
                        # print(combined_header_row)
                        combined_table.append(combined_header_row)
                    elif i > 0:
                        whole_row = player_info_rows[i].contents + player_stat_rows[i].contents
                        combined_player_row = BeautifulSoup('', 'lxml').new_tag('tr')
                        for plyr in whole_row:
                            combined_player_row.append(plyr)
                        # updated the pct_rostered variable
                        row_pct_rostered = combined_player_row.select_one("div[title*='rostered']")
                        if row_pct_rostered is not None:
                            pct_rostered = float(row_pct_rostered.string)

                        if is_unique_row(combined_player_row, table_rows):
                            table_rows.append(str(combined_player_row))
                            combined_table.append(combined_player_row)
                    else:
                        continue  # if i (row) == 0 on any other page, then skip it
                # go to the next page
                page += 1
                # always to click to next page, pct_rostered will be checked at the top of the loop
                sleep(.3)
                next_button = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button.Button.Pagination__Button--next")))

                next_button.click()
                sleep(1.6)

            except Exception as e:
                print(f"An error occurred while processing page {page}. Error message: {e}")
                continue

        if page < 4:
            print(f"Only {page - 1} pages were processed for {pos_group}.\n   Potential scraping "
                  f"failure.")
            pass

        # print(f"The lowest %Rostered for {posGroup} group was {pct_rostered}")
        # print(f"A total of {page - 1} pages were processed for {posGroup} group. \n" +
        #       f"{len(combined_table)} players added")
        assert len(combined_table) > 0, "No players were added to the combined table"
        return combined_table

    def write_out_html(self):
        match self.etl_type:
            case ETLType.REG_SZN:
                # get the second value of the directory tuple for the path
                mtbl_iokit.write.write_out(self.combined_table.prettify(),
                                           self.directory[1],
                                           "temp_espn_player_universe",
                                           ".html")
            case ETLType.PRE_SZN:
                # get the second value of the directory tuple for the path
                mtbl_iokit.write.write_out(self.bats.prettify(),
                                           self.directory[1],
                                           "temp_espn_bats_universe",
                                           ".html")
                mtbl_iokit.write.write_out(self.arms.prettify(),
                                           self.directory[1],
                                           "temp_espn_arms_universe",
                                           ".html")

    def prep_extract(self):
        """
        Prepare the page.  If REGSZN, need to sort on %Rostered. If PRESZN, need to click on
        Sortable Projections.
        :return:
        """
        match self.etl_type:
            case ETLType.REG_SZN:
                pct_rostered_column = self.driver.find_element(
                    By.XPATH, "//th[div[span[contains(text(),'%ROST')]]]")
                pct_rostered_column.click()
                sleep(1.6)
            case ETLType.PRE_SZN:
                button_group = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ButtonGroup"))
                )

                sortable_proj_button = button_group.find_element(By.XPATH,
                                                                 "//button[span[text()='Sortable "
                                                                 "Projections']]")
                sortable_proj_button.click()
                sleep(1.6)

    def expected_table_loaded(self, initial_state) -> bool:
        """
        Compares the current state against the initial state
        :param initial_state: HTML string of the initial state
        :return: bool that compares HTML Table Body strings
        """
        return initial_state != self.driver.find_element(By.CSS_SELECTOR, "tbody.Table__TBODY").text


def is_unique_row(row: Tag, table_rows: list[str]) -> bool:
    """
    Function that checks to see if a row is already in the tableRows list
    :param row: a row of player data
    :param table_rows: a list of rows of player data
    :return: True if the row is already in the list, False if it is not
    """
    id_loc: str = row.find("img").get("data-src") or row.find("img").get("src")
    espn_id = re.findall(r'full/(\d+)\.png', id_loc)[0]
    return str(row) not in table_rows
    # else:
    #     # check to make sure Shohei Ohtani is not in the table more than twice
    #     shoheis = filter(lambda x: "39382" in x, table_rows)
    #     list_shoheis = list(shoheis)
    #     if espn_id == "39382" and len(list_shoheis) < 2:
    #         return False
    #     else:
    #         # print("duplicate row found, skipping table")
    #         return True
