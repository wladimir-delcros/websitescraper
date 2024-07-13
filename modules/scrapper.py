from typing import Any
import requests
from requests.models import Response
from bs4 import BeautifulSoup
import re

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
            soup: Any = BeautifulSoup(content, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            cleaned: str = soup.get_text()
            lines: Any = (line.strip() for line in cleaned.splitlines())
            chunks: Any = (
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
        content: str = requests.get(self.url).text
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all('a'):
            href = link.get("href")
            if href:
                if self.url not in href:
                    if not any(proto in href for proto in ["http", "https", "mailto:"]):
                        href = self.url + href
                urls.append(href)
        return urls

    def extract_emails(self, text: str) -> list:
        """Extract emails from text"""
        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        return email_regex.findall(text)

    def extract_phones(self, text: str) -> list:
        """Extract phone numbers from text"""
        phone_regex = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')
        return phone_regex.findall(text)

    def extract_social_media(self, text: str) -> list:
        """Extract social media links from text"""
        social_media = []
        social_media_patterns = {
            "twitter": re.compile(r'https?://(www\.)?twitter\.com/[a-zA-Z0-9_]+'),
            "linkedin": re.compile(r'https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+'),
            "facebook": re.compile(r'https?://(www\.)?facebook\.com/[a-zA-Z0-9_\-]+'),
            "instagram": re.compile(r'https?://(www\.)?instagram\.com/[a-zA-Z0-9_\-]+'),
            "discord": re.compile(r'https?://(www\.)?discord\.gg/[a-zA-Z0-9_\-]+'),
            "youtube": re.compile(r'https?://(www\.)?youtube\.com/[a-zA-Z0-9_\-]+'),
            "github": re.compile(r'https?://(www\.)?github\.com/[a-zA-Z0-9_\-]+'),
            "medium": re.compile(r'https?://(www\.)?medium\.com/[a-zA-Z0-9_\-]+'),
            "reddit": re.compile(r'https?://(www\.)?reddit\.com/[a-zA-Z0-9_\-]+'),
            "pinterest": re.compile(r'https?://(www\.)?pinterest\.com/[a-zA-Z0-9_\-]+'),
            "tiktok": re.compile(r'https?://(www\.)?tiktok\.com/[a-zA-Z0-9_\-]+')
        }
        for platform, pattern in social_media_patterns.items():
            social_media.extend(pattern.findall(text))
        return social_media

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
                    if url:
                        req: Response = requests.get(url)
                        contents.append(req.text)
                except requests.exceptions.MissingSchema:
                    pass
        else:
            req: Response = requests.get(self.url)
            contents.append(req.text)

        contents = self.clean()
        all_text = ' '.join(contents)
        emails = self.extract_emails(all_text)
        phones = self.extract_phones(all_text)
        social_media = self.extract_social_media(all_text)

        return {
            "text": all_text,
            "E-Mails": emails,
            "Numbers": phones,
            "SocialMedia": social_media,
            "SocialMediaInfo": [{"url": url, "info": {}} for url in social_media]
        }
        