import os

from diskcache import Index
from dotenv import load_dotenv
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions

from crawler_common import WebBrowserClient, GroupsIOProfileCrawler


class SeleniumWebBrowserClient(WebBrowserClient):

    def __init__(self):
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("headless")
        self.driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install())
        )

    def login(self, directory_url, credentials):
        self.driver.get(directory_url)
        login_input = self.driver.find_element(By.ID, "email")
        if login_input:
            login_input.click()
            login_input.send_keys(credentials[0])
            login_input.send_keys(Keys.TAB)
            actions = ActionChains(self.driver)
            actions.send_keys(credentials[1]).perform()
            form = self.driver.find_element(By.ID, "loginform")
            form.submit()

    def get_directory_page_links(self):

        # find all of the links
        all_links_on_dir_page = self.driver.find_elements(By.TAG_NAME, "a")
        return [
            l.get_attribute("href")
            for l in all_links_on_dir_page
            if l.get_attribute("href")
        ]

    def get_content(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def goto(self, url):
        self.driver.get(url)

    def __del__(self):
        self.driver.quit()


load_dotenv()
credentials = (os.environ["login_name"], os.environ["password"])
group_name = os.environ["group_name"]
html_cache = Index(os.path.join(os.getcwd(), "htmlindex"))
GroupsIOProfileCrawler(
    credentials, group_name, SeleniumWebBrowserClient(), html_cache
).crawl()
