from typing import Any
import requests
from requests.models import Response
from bs4 import BeautifulSoup

class Scrapper:
    """
    Scrapper Class
    """

    def __init__(self, url: str = None, contents: list = [], crawl=False) -> None:
        """Constructor

        Args:
            url (str): [description]. Defaults to None.
            contents (list, optional): Defaults to [].
            crawl (bool): Defaults to False.
        """

        self.url = url
        self.urls = []
        self.contents = contents
        self.crawl = crawl

    def clean(self) -> list:
        """clean function

        Returns:
            list: [description]
        """

        contents: list = []

        for content in self.contents:
            soup: any = BeautifulSoup(content, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            cleaned: str = soup.get_text()
            lines: object = (line.strip() for line in cleaned.splitlines())
            chunks: object = (
                phrase.strip()
                for line in lines for phrase in line.split("  ")
            )
            contents.append('\n'.join(chunk for chunk in chunks if chunk))

        return contents

    def getURLs(self) -> list:
        """getURLs function

        Returns:
            list: [description]
        """

        urls: list = []
        try:
            content: str = requests.get(self.url, timeout=10).text
            soup = BeautifulSoup(content, "html.parser")
            for link in soup.find_all('a'):
                if link.get("href") is not None:
                    if self.url not in link.get("href"):
                        if "http" not in link.get("href") and "https" not in link.get("href") and "mailto:" not in link.get(
                                "href"):
                            urls.append(self.url + link.get('href'))
                            continue
                urls.append(link.get("href"))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
        return urls

    def getText(self) -> dict:
        """getText function

        Returns:
            dict
        """
        urls = self.getURLs()
        contents: list = []
        if self.crawl:
            for url in urls:
                try:
                    if url is not None:
                        req: Response = requests.get(url, timeout=10)
                        contents.append(req.text)
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching the URL: {e}")
                    pass
        else:
            try:
                req: Response = requests.get(self.url, timeout=10)
                contents.append(req.text)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching the URL: {e}")
        contents = Scrapper(contents=contents).clean()
        return {"text": contents, "urls": urls}