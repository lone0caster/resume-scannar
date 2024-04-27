import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np
from fake_useragent import UserAgent

class GitHubBot:
    def __init__(self, driver_path=r'C:/Users/abhij/Mini Project/chromedriver.exe'):
        self.driver_path = driver_path
        self.user_agent = UserAgent().random
        self.driver = self.create_driver()
        self.driver.implicitly_wait(5)
        self.search_query = None

    def create_driver(self):
        option = webdriver.ChromeOptions()
        option.add_argument(f'user-agent={self.user_agent}')
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options = option)
        driver.maximize_window()
        return driver

    def open_url(self, url):
        self.driver.get(url)

    def click_repositories_tab(self):
        repositories_tab = self.driver.find_element(By.XPATH, "//a[@data-tab-item='repositories']")
        repositories_tab.click()

    def scrape_repositories_data(self):
        titles = []
        languages = []

        repo_containers = self.driver.find_elements(By.XPATH, "//div[@class='col-10 col-lg-9 d-inline-block']")

        for container in repo_containers:
            title_element = container.find_element(By.TAG_NAME, 'a')
            title = title_element.text
            titles.append(title)

            language_elements = container.find_elements(By.XPATH, ".//span[@itemprop='programmingLanguage']")
            if language_elements:
                language = language_elements[0].text
            else:
                language = np.nan
            languages.append(language)

        return titles, languages