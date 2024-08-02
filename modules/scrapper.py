import logging
from typing import Any, List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import random
import uuid

class Scrapper:
    """
    Scrapper Class
    """

    def __init__(self, url: Optional[str] = None, contents: Optional[List[str]] = None, crawl: bool = False, proxy_file: str = 'proxies.txt') -> None:
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
        self.request_id = str(uuid.uuid4())
        logging.debug(f'Initialized Scrapper with URL: {url}, crawl: {crawl}, proxies: {self.proxies}, request_id: {self.request_id}')

    def load_proxies(self, proxy_file: str) -> List[str]:
        try:
            with open(proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                logging.debug(f'Loaded proxies: {proxies}')
                return proxies
        except FileNotFoundError:
            logging.warning(f'Proxy file {proxy_file} not found')
            return []

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        proxy = {'http': random.choice(self.proxies)} if self.proxies else None
        logging.debug(f'Using proxy: {proxy}')
        return proxy

    def get_headers(self) -> Dict[str, str]:
        user_agent = self.ua.random
        logging.debug(f'Using User-Agent: {user_agent}')
        return {'User-Agent': user_agent}

    def clean(self) -> List[str]:
        """Clean HTML contents.
        
        Returns:
            list: Cleaned text content.
        """
        contents: List[str] = []
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

    def get_contact_and_legal_urls(self, soup: BeautifulSoup) -> List[str]:
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

    def getURLs(self) -> List[str]:
        """Get URLs from the main page
        
        Returns:
            list: List of URLs found on the page.
        """
        urls: List[str] = []
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

    def extract_emails(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Extract emails from text and HTML content
        
        Returns:
            list: List of unique emails found with their sources.
        """
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = set()

        # Extract emails from plain text
        found_emails = email_pattern.findall(text)
        logging.debug(f'Emails found in {source}: {found_emails}')
        emails.update(found_emails)

        # Extract emails from href attributes of <a> tags
        soup = BeautifulSoup(text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('mailto:'):
                email = href.split(':', 1)[1].split('?')[0]
                logging.debug(f'Email found in href: {email}')
                emails.add(email)

        logging.debug(f'Extracted emails: {emails}')
        return [{"value": email, "sources": [source]} for email in emails]

    def extract_phones(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Extract phone numbers from text and remove duplicates.
        
        Returns:
            list: List of unique phone numbers found with their sources.
        """
        phone_regex = re.compile(r'\b(\+33|0)[1-9](?:[\s.-]?\d{2}){4}\b')
        found_phones = phone_regex.findall(text)
        unique_phones = list(set(found_phones))  # Utiliser un set pour éliminer les doublons
        logging.debug(f'Extracted phones from {source}: {unique_phones}')
        return [{"value": phone, "sources": [source]} for phone in unique_phones]

    def extract_social_media(self, urls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
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

    def extract_links_for_contact_info(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract contact information from specific links
        
        Returns:
            list: List of contact information found with their sources.
        """
        contact_info = []
        for url in urls:
            if "tel:" in url:
                contact_info.append({"value": url.replace("tel:", ""), "sources": [self.url]})
            if "wa.me" in url:
                match = re.search(r'wa.me/(\+?\d+)', url)
                if match:
                    contact_info.append({"value": match.group(1), "sources": [self.url]})
        logging.debug(f'Extracted contact info from links: {contact_info}')
        return contact_info

    def extract_siret_or_siren(self, text: str, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract SIRET or SIREN numbers from text
        
        Returns:
            dict: Extracted SIRET and SIREN numbers with their sources.
        """
        siret_pattern = re.compile(r'\b\d{14}\b')
        siren_pattern = re.compile(r'\b\d{9}\b')
        siret_numbers = set(siret_pattern.findall(text))
        siren_numbers = set(siren_pattern.findall(text)) - set(num[:9] for num in siret_numbers)

        logging.debug(f'Initial SIRET numbers in {source}: {siret_numbers}')
        logging.debug(f'Initial SIREN numbers in {source}: {siren_numbers}')

        valid_siret = [{"value": num, "sources": [source]} for num in siret_numbers]
        valid_siren = [{"value": num, "sources": [source]} for num in siren_numbers]

        logging.debug(f'Final SIRET numbers: {valid_siret}')
        logging.debug(f'Final SIREN numbers: {valid_siren}')
        
        return {
            "SIRET": valid_siret,
            "SIREN": valid_siren
        }

    def extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
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

    def get_homepage_meta_info(self) -> Dict[str, Any]:
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

    def getText(self) -> Dict[str, Any]:
        """Get text and other information from the URL, ensuring no duplicate phone numbers or emails.
        
        Returns:
            dict: Extracted information including text, URLs, emails, phone numbers, social media links, and SIRET/SIREN numbers.
        """
        urls = self.getURLs()
        filtered_urls = self.filter_urls(urls)
        all_text = []
        contents = []
        all_emails = []
        all_phones = []
        all_siret = []
        all_siren = []

        if self.crawl:
            for url in filtered_urls:
                for attempt in range(3):  # Try up to 3 times
                    try:
                        if url:
                            req = requests.get(url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
                            contents.append(req.text)
                            logging.debug(f'Crawled URL: {url}')
                            # Accumuler les e-mails et SIRET/SIREN de chaque page
                            emails_found = self.extract_emails(req.text, url)
                            phones_found = self.extract_phones(req.text, url)
                            siret_found = self.extract_siret_or_siren(req.text, url).get("SIRET", [])
                            siren_found = self.extract_siret_or_siren(req.text, url).get("SIREN", [])
                            logging.debug(f'Emails found in {url}: {emails_found}')
                            logging.debug(f'Phones found in {url}: {phones_found}')
                            logging.debug(f'SIRET found in {url}: {siret_found}')
                            logging.debug(f'SIREN found in {url}: {siren_found}')
                            all_emails.extend(emails_found)
                            all_phones.extend(phones_found)
                            all_siret.extend(siret_found)
                            all_siren.extend(siren_found)
                            break  # Exit the retry loop if successful
                    except requests.exceptions.RequestException as e:
                        logging.error(f'Error crawling URL {url}: {e}')
                        continue
        else:
            try:
                req = requests.get(self.url, headers=self.get_headers(), proxies=self.get_random_proxy(), timeout=10)
                contents.append(req.text)
                all_emails.extend(self.extract_emails(req.text, self.url))
                all_phones.extend(self.extract_phones(req.text, self.url))
                siret_or_siren = self.extract_siret_or_siren(req.text, self.url)
                all_siret.extend(siret_or_siren.get("SIRET", []))
                all_siren.extend(siret_or_siren.get("SIREN", []))
            except Exception as e:
                logging.error(f'Error fetching content from main URL: {e}')

        # Log all HTML content retrieved
        for content in contents:
            logging.debug(f'HTML content for email extraction: {content[:500]}...')  # Log the first 500 characters of each content

        phones = self.extract_links_for_contact_info(urls)
        all_phones.extend(phones)
        all_phones = list({phone['value']: phone for phone in all_phones}.values())  # Dédoublonner les numéros de téléphone
        social_media = self.extract_social_media(urls)
        homepage_meta_info = self.get_homepage_meta_info()

        logging.debug(f'Extracted emails: {all_emails}')
        logging.debug(f'Extracted phone numbers: {all_phones}')
        logging.debug(f'Extracted social media: {social_media}')
        logging.debug(f'Extracted SIRET: {all_siret}')
        logging.debug(f'Extracted SIREN: {all_siren}')
        logging.debug(f'Extracted homepage meta info: {homepage_meta_info}')

        # Dédoublonner toutes les clés
        all_emails = list({email['value']: email for email in all_emails}.values())
        all_siret = list({siret['value']: siret for siret in all_siret}.values())
        all_siren = list({siren['value']: siren for siren in all_siren}.values())
        
        return {
            "text": contents,
            "urls": urls,
            "E-Mails": all_emails,
            "Numbers": all_phones,
            "SocialMedia": social_media,
            "SIRET_OR_SIREN": {"SIRET": all_siret, "SIREN": all_siren},
            "HomepageMetaInfo": homepage_meta_info,
            "request_id": self.request_id
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

    def merge_data(self, original_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new data into original data while avoiding duplicates for emails and phone numbers.
        """
        for key in ['E-Mails', 'Numbers', 'SocialMedia']:
            original_items = {item['value']: item for item in original_data.get(key, [])}
            for new_item in new_data.get(key, []):
                if new_item['value'] not in original_items:
                    original_data[key].append(new_item)
                else:
                    original_items[new_item['value']]['sources'].extend(new_item['sources'])
            original_data[key] = list(original_items.values())
        return original_data
