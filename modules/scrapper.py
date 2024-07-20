import logging
from typing import Any, List
import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import random

class Scrapper:
    """
    Scrapper Class
    """

    def __init__(self, url: str = None, contents: list = None, crawl=False, proxy_file='proxies.txt') -> None:
        """Constructor
    
        Args:
            url (str): URL to scrape. Defaults to None.
            contents (list, optional): Contents to process. Defaults to None.
            crawl (bool): Whether to crawl additional URLs. Defaults to False.
            proxy_file (str): File containing proxy addresses. Defaults to 'proxies.txt'.
        """
        self.url = url
        self.urls = []
        self.contents = contents if contents is not None else []
        self.crawl = crawl
        self.ua = UserAgent()
        self.proxies = self.load_proxies(proxy_file)
        logging.debug(f'Initialized Scrapper with URL: {url}, crawl: {crawl}, proxies: {self.proxies}')

    def load_proxies(self, proxy_file):
        try:
            with open(proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                logging.debug(f'Loaded proxies: {proxies}')
                return proxies
        except FileNotFoundError:
            logging.warning(f'Proxy file {proxy_file} not found')
            return []

    def get_random_proxy(self):
        proxy = {'http': random.choice(self.proxies)} if self.proxies else None
        logging.debug(f'Using proxy: {proxy}')
        return proxy

    def get_headers(self):
        user_agent = self.ua.random
        logging.debug(f'Using User-Agent: {user_agent}')
        return {'User-Agent': user_agent}

    def clean(self) -> list:
        """Clean HTML contents.

        Returns:
            list: Cleaned text content.
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
        logging.debug('Cleaned contents from HTML')
        return contents

    def get_contact_and_legal_urls(self, soup):
        """Prioritize contact and legal pages"""
        contact_keywords = ['contact', 'mentions-legales', 'impressum', 'terms', 'privacy']
        urls = []
        for link in soup.find_all('a'):
            href = link.get("href")
            if href and any(keyword in href.lower() for keyword in contact_keywords):
                if not href.startswith("http"):
                    href = requests.compat.urljoin(self.url, href)
                urls.append(href)
        return urls

    def getURLs(self) -> list:
        """Get URLs from the main page

        Returns:
            list: List of URLs found on the page.
        """
        urls: list = []
        try:
            response = requests.get(self.url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
            content: str = response.text
            logging.debug(f'Retrieved HTML content: {content[:500]}...')  # Log the first 500 characters of the HTML content
            soup = BeautifulSoup(content, "html.parser")
            # Prioritize contact and legal pages
            urls.extend(self.get_contact_and_legal_urls(soup))
            for link in soup.find_all('a'):
                href = link.get("href")
                if href:
                    if not href.startswith("http"):
                        href = requests.compat.urljoin(self.url, href)
                    urls.append(href)
            logging.debug(f'Found URLs: {urls}')
        except Exception as e:
            logging.error(f'Error fetching URLs: {e}')
        return urls

    def extract_emails(self, text: str) -> list:
        """Extract emails from text and HTML content

        Returns:
            list: List of unique emails found.
        """
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = set()

        # Extraire les e-mails du texte brut
        found_emails = email_pattern.findall(text)
        logging.debug(f'Emails found in text: {found_emails}')
        emails.update(found_emails)

        # Extraire les e-mails des attributs href des balises <a>
        soup = BeautifulSoup(text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('mailto:'):
                email = href.split(':', 1)[1].split('?')[0]
                logging.debug(f'Email found in href: {email}')
                emails.add(email)

        logging.debug(f'Extracted emails: {emails}')
        return list(emails)

    def extract_phones(self, text: str) -> list:
        """Extract phone numbers from text

        Returns:
            list: List of phone numbers found.
        """
        phone_regex = re.compile(r'\b\d{10,15}\b')
        return phone_regex.findall(text)

    def extract_social_media(self, urls: List[str]) -> dict:
        """Extract social media links from a list of URLs

        Returns:
            dict: Dictionary of social media links found.
        """
        social_media = {
            "facebook": [],
            "linkedin": [],
            "instagram": [],
            "houzz": [],
            "pinterest": [],
            "hoodspot": [],
            "google": [],
            "twitter": [],
            "trustpilot": [],
            "yelp": [],
            "youtube": [],
            "whatsapp": [],
            "tiktok": []
        }
        social_media_patterns = {
            "facebook": re.compile(r'https?://(www\.)?facebook\.com/[a-zA-Z0-9_\-.]+'),
            "linkedin": re.compile(r'https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_\-.]+|https?://(www\.)?linkedin\.com/company/[a-zA-Z0-9_\-.]+'),
            "instagram": re.compile(r'https?://(www\.)?instagram\.com/[a-zA-Z0-9_\-.]+'),
            "houzz": re.compile(r'https?://(www\.)?houzz\.fr/professionnels/[a-zA-Z0-9_\-.]+'),
            "pinterest": re.compile(r'https?://(www\.)?pinterest\.fr/[a-zA-Z0-9_\-.]+'),
            "hoodspot": re.compile(r'https?://(www\.)?hoodspot\.fr/[a-zA-Z0-9_\-.]+'),
            "google": re.compile(r'https?://(www\.)?google\.[a-zA-Z0-9_\-.]+'),
            "twitter": re.compile(r'https?://(www\.)?twitter\.com/[a-zA-Z0-9_\-.]+'),
            "trustpilot": re.compile(r'https?://(www\.)?trustpilot\.com/review/[a-zA-Z0-9_\-.]+'),
            "yelp": re.compile(r'https?://(www\.)?yelp\.fr/biz/[a-zA-Z0-9_\-.]+'),
            "youtube": re.compile(r'https?://(www\.)?youtube\.com/[a-zA-Z0-9_\-.]+'),
            "whatsapp": re.compile(r'https?://wa\.me/\+\d+'),
            "tiktok": re.compile(r'https?://(www\.)?tiktok\.com/@[a-zA-Z0-9_\-.]+')
        }
        for url in urls:
            for platform, pattern in social_media_patterns.items():
                if pattern.match(url):
                    social_media[platform].append({"value": url, "sources": [self.url]})
                    break
        logging.debug(f'Extracted social media: {social_media}')
        return social_media

    def extract_links_for_contact_info(self, urls: List[str]) -> List[str]:
        """Extract contact information from specific links

        Returns:
            list: List of contact information found.
        """
        contact_info = []
        for url in urls:
            if "tel:" in url:
                contact_info.append(url.replace("tel:", ""))
            if "wa.me" in url:
                match = re.search(r'wa.me/(\+?\d+)', url)
                if match:
                    contact_info.append(match.group(1))
        logging.debug(f'Extracted contact info from links: {contact_info}')
        return contact_info

    def extract_siret_or_siren(self, text: str) -> dict:
        """Extract SIRET or SIREN numbers from text

        Returns:
            dict: Extracted SIRET and SIREN numbers.
        """
        siret_pattern = re.compile(r'\b\d{14}\b')
        siren_pattern = re.compile(r'\b\d{9}\b')
        siret_numbers = set(siret_pattern.findall(text))
        siren_numbers = set(siren_pattern.findall(text)) - set(num[:9] for num in siret_numbers)

        logging.debug(f'Initial SIRET numbers: {siret_numbers}')
        logging.debug(f'Initial SIREN numbers: {siren_numbers}')

        valid_siret = []
        valid_siren = None

        # If SIRET numbers are found, use them and exclude SIREN
        if siret_numbers:
            valid_siret = list(siret_numbers)
            logging.debug(f'Found SIRET numbers: {valid_siret}')
        else:
            # If no SIRET is found, use one of the SIREN numbers
            if siren_numbers:
                valid_siren = list(siren_numbers)[0]  # Take the first available SIREN
                logging.debug(f'No SIRET found, using SIREN: {valid_siren}')

        logging.debug(f'Final SIRET numbers: {valid_siret}')
        logging.debug(f'Final SIREN numbers: {[valid_siren] if valid_siren else []}')
        
        return {
            "SIRET": valid_siret,
            "SIREN": [valid_siren] if valid_siren else []
        }

    def extract_meta_info(self, soup: BeautifulSoup) -> dict:
        """Extract meta information such as title, description, and headers

        Returns:
            dict: Extracted meta information.
        """
        title = soup.title.string if soup.title else ''
        meta_description = ''
        if soup.find("meta", attrs={"name": "description"}):
            meta_description = soup.find("meta", attrs={"name": "description"}).get("content", '')
        
        headers = {
            "H1": [h1.get_text(strip=True) for h1 in soup.find_all("h1")],
            "H2": [h2.get_text(strip=True) for h2 in soup.find_all("h2")],
            "H3": [h3.get_text(strip=True) for h3 in soup.find_all("h3")]
        }
        
        logging.debug(f'Extracted title: {title}')
        logging.debug(f'Extracted meta description: {meta_description}')
        logging.debug(f'Extracted headers: {headers}')
        
        return {
            "title": title,
            "meta_description": meta_description,
            "headers": headers
        }

    def get_homepage_meta_info(self) -> dict:
        """Get meta information from the homepage URL

        Returns:
            dict: Extracted meta information including title, description, and headers.
        """
        try:
            response = requests.get(self.url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
            content = response.text
            soup = BeautifulSoup(content, "html.parser")
            return self.extract_meta_info(soup)
        except Exception as e:
            logging.error(f'Error fetching homepage meta info: {e}')
            return {
                "title": "",
                "meta_description": "",
                "headers": {"H1": [], "H2": [], "H3": []}
            }

    def getText(self) -> dict:
        """Get text and other information from the URL

        Returns:
            dict: Extracted information including text, URLs, emails, phone numbers, social media links, and SIRET/SIREN numbers.
        """
        urls = self.getURLs()
        filtered_urls = self.filter_urls(urls)
        all_text = []
        contents = []
        all_emails = set()
        all_siret = set()
        all_siren = set()

        if self.crawl:
            for url in filtered_urls:
                for attempt in range(3):  # Try up to 3 times
                    try:
                        if url:
                            req = requests.get(url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
                            contents.append(req.text)
                            logging.debug(f'Crawled URL: {url}')
                            # Accumuler les e-mails et SIRET/SIREN de chaque page
                            emails_found = self.extract_emails(req.text)
                            siret_found = self.extract_siret_or_siren(req.text).get("SIRET", [])
                            siren_found = self.extract_siret_or_siren(req.text).get("SIREN", [])
                            logging.debug(f'Emails found in {url}: {emails_found}')
                            logging.debug(f'SIRET found in {url}: {siret_found}')
                            logging.debug(f'SIREN found in {url}: {siren_found}')
                            all_emails.update(emails_found)
                            all_siret.update(siret_found)
                            all_siren.update(siren_found)
                            break  # Exit the retry loop if successful
                    except requests.exceptions.RequestException as e:
                        logging.error(f'Error crawling URL {url}: {e}')
                        time.sleep(2)  # Wait for 2 seconds before retrying
                        continue
        else:
            req = requests.get(self.url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
            contents.append(req.text)
            all_emails.update(self.extract_emails(req.text))
            siret_or_siren = self.extract_siret_or_siren(req.text)
            all_siret.update(siret_or_siren.get("SIRET", []))
            all_siren.update(siret_or_siren.get("SIREN", []))

        # Log all HTML content retrieved
        for content in contents:
            logging.debug(f'HTML content for email extraction: {content[:500]}...')  # Log the first 500 characters of each content

        combined_text = ' '.join(contents)
        phones = self.extract_phones(combined_text)
        contact_info = self.extract_links_for_contact_info(urls)
        phones.extend(contact_info)
        social_media = self.extract_social_media(urls)
        homepage_meta_info = self.get_homepage_meta_info()

        # Normalize phone numbers extracted from URLs
        normalized_phones = [self.normalize_phone_number(phone) for phone in phones]

        logging.debug(f'Extracted emails: {all_emails}')
        logging.debug(f'Extracted phone numbers: {phones}')
        logging.debug(f'Extracted social media: {social_media}')
        logging.debug(f'Extracted SIRET: {all_siret}')
        logging.debug(f'Extracted SIREN: {all_siren}')
        logging.debug(f'Extracted homepage meta info: {homepage_meta_info}')

        return {
            "text": contents,
            "urls": urls,
            "E-Mails": [{"value": email, "sources": [self.url]} for email in all_emails],
            "Numbers": [{"value": phone, "sources": [self.url]} for phone in normalized_phones],
            "SocialMedia": social_media,
            "SIRET_OR_SIREN": {"SIRET": list(all_siret), "SIREN": list(all_siren)},
            "HomepageMetaInfo": homepage_meta_info
        }

    def normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number format

        Returns:
            str: Normalized phone number.
        """
        return re.sub(r'\D', '', phone)

    def filter_urls(self, urls: List[str]) -> List[str]:
        """Filter URLs to prioritize contact and legal pages

        Returns:
            list: Filtered list of URLs.
        """
        contact_keywords = ['contact', 'mentions-legales', 'impressum', 'terms', 'privacy']
        filtered_urls = [url for url in urls if any(keyword in url.lower() for keyword in contact_keywords)]
        logging.debug(f'Filtered URLs: {filtered_urls}')
        return filtered_urls