import re
import string
from socid_extractor import parse, extract
from typing import List

class InfoReader:
    """
    InfoReader Class
    """

    def __init__(self, content: dict = None, social_path: str = "./socials.txt") -> None:
        """Constructor

        Args:
            content (dict): [description]. Defaults to None.
            social_path (str): [description]. Defaults to "./socials.txt".
        """

        if content is None:
            content = {
                "text": [],
                "urls": []
            }

        self.content = content
        self.social_path = social_path
        self.res = {
            "phone": r"\+?\d[\d\s\-\(\)]{7,}\d",
            "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        }

    def getPhoneNumber(self) -> list:
        """getPhoneNumber function

        Returns:
            list: [description]
        """
        numbers = []
        texts = self.content.get("text", [])

        for text in texts:
            for n in text.split("\n"):
                if re.match(self.res["phone"], n):
                    for letter in string.ascii_letters:
                        n = n.replace(letter, "")
                    numbers.append(n)

        return list(dict.fromkeys(numbers))

    def getEmails(self) -> list:
        """getEmails Function

        Returns:
            list: [description]
        """
        emails = []
        texts = self.content.get("text", [])
        
        for text in texts:
            logging.debug(f'Processing text for emails: {text[:500]}...')  # Log the first 500 characters
            for s in text.split("\n"):
                if re.match(self.res["email"], s):
                    emails.append(s)

        for link in self.content.get("urls", []):
            if link is None:
                continue
            if "mailto:" in link:
                emails.append(link.replace("mailto:", ""))

        logging.debug(f'Extracted emails: {emails}')
        return list(dict.fromkeys(emails))

    def getSocials(self) -> list:
        """getSocials Function

        Returns:
            list: [description]
        """
        sm_accounts = []
        socials = open(self.social_path, "r+").readlines()

        for url in self.content.get("urls", []):
            for s in socials:
                if url is None:
                    continue
                if s.replace("\n", "").lower() in url.lower():
                    sm_accounts.append(url)
        return list(dict.fromkeys(sm_accounts))

    def getSocialsInfo(self) -> List[dict]:
        urls = self.getSocials()
        sm_info = []
        for url in urls:
            try:
                text, _ = parse(url)
                sm_info.append({"url": url, "info": extract(text)})
            except Exception:  # Quick fix for now
                pass
        return sm_info