import os

from diskcache import Index
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from crawler_common import WebBrowserClient, GroupsIOProfileCrawler


class PlaywrightWebBrowserClient(WebBrowserClient):

    def __init__(self):
        self.done = False
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)

    def login(self, login_url, credentials):
        self.page = self.browser.new_page()
        self.page.goto(login_url)
        self.page.fill("#email", credentials[0])
        self.page.press("#email", "Tab")
        self.page.keyboard.type(credentials[1])
        self.page.click('#loginform button[type="submit"]')

    def get_directory_page_links(self):
        all_links_on_dir_page = self.page.query_selector_all("a")
        return [
            l.get_attribute("href")
            for l in all_links_on_dir_page
            if l.get_attribute("href")
        ]

    def get_content(self, url):
        self.page.goto(url)
        return self.page.content()

    def goto(self, url):
        self.page.goto(url)

    def __del__(self):
        self.browser.close()
        self.playwright.stop()


load_dotenv()
credentials = (os.environ["login_name"], os.environ["password"])
group_name = os.environ["group_name"]
html_cache = Index(os.path.join(os.getcwd(), "htmlindex"))
GroupsIOProfileCrawler(
    credentials, group_name, PlaywrightWebBrowserClient(), html_cache
).crawl()
