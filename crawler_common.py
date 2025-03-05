from abc import ABC, abstractmethod
import logging
import posixpath

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class WebBrowserClient(ABC):
    """
    Defines an interface for controlling a web browser for the purpose of
    web scraping Groups.io website profile pages. See the GroupsIOCrawler class
    for an example of how this interface is used.
    """

    @abstractmethod
    def login(self, login_url, credentials):
        """
        Log into the website using the provided credentials
        :param login_url:
        :param credentials: username and password tuple
        :return:
        """
        pass

    @abstractmethod
    def get_directory_page_links(self):
        """
        Get all the anchor tag hrefs on the current directory page, which should
        be a groups.io user profile directory page :return: collection of urls
        as strings"""
        pass

    @abstractmethod
    def get_content(self, url):
        """
        Get the HTML content of the page at the provided url
        :param url:
        :return: string
        """
        pass

    @abstractmethod
    def goto(self, url):
        """
        Navigate the browser/client to the provided url
        :param url:
        :return: None
        """
        pass


class GroupsIOProfileCrawler:

    def __init__(self, credentials, group_name, webBrowserClient, cache):
        self.credentials = credentials
        self.group_name = group_name
        self.webBrowserClient = webBrowserClient
        self.cache = cache
        self.directory_url = posixpath.join(
            "https://groups.io/", "g", group_name, "directory"
        )

    def crawl(self):
        # attempt to access the directory page, the browser will redirect to the
        # login page and upon successful login will redirect back to the
        # directory page
        self.webBrowserClient.login(self.directory_url, self.credentials)
        logger.info("Logged in")
        done = False
        page_number = 0
        while not done:

            # visit all the profile pages on the directory page, capture the HTML content
            # and store it in the cache

            dir_page_links = self.webBrowserClient.get_directory_page_links()

            # leveraging a quirk in the ui, the account used to run this script have
            # 2 profile links on each directory page, one on in the left nave which
            # has a "//profile" and the 'normal one' in the directory which will be
            # "/profile".  This must be leveraged to avoid early exit which is
            # triggered by visiting the same profile page twice.
            dir_page_profile_url_frag = f"{self.group_name}/profile"
            profile_urls = {l for l in dir_page_links if dir_page_profile_url_frag in l}

            for url in profile_urls:

                # no dots for debugging
                if logger.getEffectiveLevel() >= logging.INFO:
                    print(".", end="", flush=True)

                logger.debug(f"Processing {url}")

                if url not in self.cache:
                    logger.debug(f"Adding {url} to cache")
                    self.cache[url] = self.webBrowserClient.get_content(url)
                else:
                    logger.debug(f"Skipping {url} as it is already in the cache")
                    done = True
                    break

            # next user profile directory page, can't say I grok all of this, but
            # I'm just replicating what I see when I do the same thing manually
            # in the browser
            page_number += 20
            directory_page_link = f"https://how.groups.io/g/{self.group_name}/directory?p=fullname,,,20,1,{str(page_number)},0&next=1"
            self.webBrowserClient.goto(directory_page_link)
            logger.debug(f"Next page: {page_number}")
