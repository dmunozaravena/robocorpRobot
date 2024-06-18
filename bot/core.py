import time
import os
import json
import logging
from datetime import datetime

from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

from .props import props
from .utils import (check_download_dir,
                    download_image,
                    image_filename,
                    update_result,
                    check_limit_date,
                    count_phrase,
                    check_currency,
                    check_init_params,
                    check_exists_output_dir,
                    )


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # NOQA


class Core:
    def __init__(self):
        self.run()

    def run(self):
        """Run main process flow"""
        navigate = Navigate()
        save_result = SaveResult()
        valid = navigate.load_init_params()
        if valid:
            check_exists_output_dir(logger)
            result, date_dir = navigate.perform_navigation()
            navigate.close_browser()
            if result:
                save_result.process_results(result, date_dir)
            else:
                logger.info("Nothing to save")
        else:
            logger.info("Check your input params, and try again")


class Navigate:
    def __init__(self):
        """Start browser"""
        # Init browser instance
        self.browser = Selenium()
        self.files_dir = ''

    def load_init_params(self) -> bool:
        # check if work item is avaliable, if not read dire from file
        try:
            work_items = WorkItems()
            work_items.get_input_work_item()
            self.url = work_items.get_work_item_variable("url", "")
            self.search_phrase = work_items.get_work_item_variable("search_phrase","")  # NOQA
            self.months = work_items.get_work_item_variable("months", 1)
            self.news_filters = work_items.get_work_item_variable("news_filters", [])  # NOQA
            logger.info("Got input params from work item")
        except Exception:
            logger.info("Getting input params from file")
            file_path = props['work_item_path']
            with open(file_path, 'r') as file:
                json_config = file.read()
            data = json.loads(json_config)
            logger.info(data)
            payload = data[0]['payload']
            self.url = payload.get('url', '')
            self.search_phrase = payload.get('search_phrase', '')
            self.months = payload.get('months', 1)
            self.news_filters = payload.get('news_filters', [])

        return check_init_params(self.url, self.search_phrase, logger)

    def close_browser(self) -> None:
        """Close browser instance"""
        logger.info("Closing Browser")
        self.browser.close_browser()

    def perform_navigation(self) -> list:
        """Start browser and performe a navigation in order to obtain data"""
        logger.info("Navigating the website...")
        self.browser.open_available_browser(self.url)
        self.browser.maximize_browser_window()
        self.search_keyword()
        self.order_by_newest()
        self.apply_filters()
        data_result = self.get_data()

        return data_result

    def get_data(self) -> list:
        """Scrape over news to collect data"""
        current_date = datetime.now()
        self.files_dir = check_download_dir(current_date, logger)
        parent_elements = self.browser.get_webelements(props['xpath_elements_li']) # NOQA
        result_list = []
        logger.info("Getting news data")
        for parent in parent_elements:
            try:
                promo_timestamp = self.browser.find_element(props['xpath_date_news'], parent) # NOQA
                timestamp = self.browser.get_element_attribute(promo_timestamp, props['attribute_date']) # NOQA
            except Exception:
                try:
                    promo_timestamp = self.browser.find_element(props['xpath_date_news_full'], parent) # NOQA
                    timestamp = self.browser.get_element_attribute(promo_timestamp, props['attribute_date']) # NOQA
                except Exception:
                    logger.info("Element not found, skipping...")
                    continue
            if check_limit_date(timestamp, self.months):
                break
            try:
                promo_title = self.browser.find_element(props['xpath_title_news'], parent) # NOQA
                title = self.browser.get_text(promo_title)
            except Exception:
                title = ''
            try:    
                promo_description = self.browser.find_element(props['xpath_description_news'], parent) # NOQA
                description = self.browser.get_text(promo_description)
            except Exception:
                description = ''

            try:
                image_element = self.browser.find_element(props['xpath_img_news'], parent) # NOQA
                image_url = self.browser.get_element_attribute(image_element, props["attribute_src"]) # NOQA
            except Exception:
                image_url = ''
            file_name = image_filename(timestamp)

            if image_url:
                download_image(image_url, self.files_dir, file_name, logger=logger) # NOQA
            else:
                logger.info(f"Image {file_name} not found")
                file_name = ''
            currency = check_currency(title, description)
            counted_phrase = count_phrase(title, description, self.search_phrase) # NOQA
            result = update_result(props["template_result"],
                                   title=title,
                                   description=description,
                                   timestamp=timestamp,
                                   file_name=file_name,
                                   currency=currency,
                                   counted_phrase=counted_phrase,
                                   )
            logger.info(result)
            result_list.append(result)
        print(result_list)
        logger.info("Data collected")
        return result_list, current_date

    def order_by_newest(self) -> None:
        """filter news from latest to older"""
        logger.info("Ordering news by newer")
        select_locator = props['order_by_newest']
        option_value = props['newest']
        self.browser.select_from_list_by_value(select_locator, option_value)

    def search_keyword(self) -> None:
        """Search phrase on website"""
        search_text = self.search_phrase
        logger.info(f"Searching for {search_text}")
        js_code = props['search_phrase'].format(search_text=search_text)
        self.browser.execute_javascript(js_code)
        self.wait_for_element(props['xpath_newest'])

    def apply_filters(self) -> None:
        """This filter news by topics and type"""
        logger.info("Selecting filters")
        for filters in self.news_filters:
            try:
                for title in props['filter_titles']:
                    xpath = props['xpath_filter_titles'].format(title=title)# NOQA
                    self.browser.click_element(xpath)
                    time.sleep(1)
            except Exception as e:
                logger.info(f'Error: {e}')
            time.sleep(2)
            xpath = props['xpath_filters'].format(filters=filters)
            try:
                self.browser.click_element(xpath)
                logger.info(f"Clicked on span with text: {filters}")
            except Exception as e:
                logger.info(f"Error: {e}")
            # time.sleep(10)
            self.wait_for_page_load()

    def wait_for_page_load(self):
        WebDriverWait(self.browser.driver, props['wait_timeout']).until(
            lambda driver: driver.execute_script('return document.readyState') in ['interactive', 'complete'] # NOQA
        )

    def wait_for_element(self, locator, by=By.XPATH) -> None:
        wait = WebDriverWait(self.browser.driver, props['wait_timeout'])
        try:
            wait.until(EC.presence_of_element_located((by, locator)))
        except TimeoutError:
            logger.info(f"Element {locator} not found within given time")


class SaveResult:
    def process_results(self, result, date_dir):
        save_file_dir = f"{props['output_dir']}/{date_dir}"
        """Create a dataframe with pandas to save data into a xlsx file"""
        df = pd.DataFrame(result)
        # convert epoch to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms') # NOQA
        df.columns = props['cols']
        xlsx_filename = props['xlsx_filename']
        excel_file_path = f'{save_file_dir}/{xlsx_filename}'
        # Write DataFrame to Excel
        df.to_excel(excel_file_path, index=False)
        try:
            output_dir = props['output_dir']
            for root, dirs, files in os.walk(output_dir):
                logger.info(f'Root: {root}')
                logger.info('Directories:')
                for dir_name in dirs:
                    logger.info(f'  {dir_name}')
                print('Files:')
                for file_name in files:
                    logger.info(f'  {file_name}')
                logger.info('')
        except FileNotFoundError:
            logger.info(f"The directory {output_dir} does not exist.")
        except PermissionError:
            logger.info(f"Permission denied to access {output_dir}.")
        except Exception as e:
            logger.info(f"An error occurred: {e}")
