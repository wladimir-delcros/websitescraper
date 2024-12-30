import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SocialMediaExtractor:
    def __init__(self):
        self.social_patterns = {
            'facebook': r'facebook\.com/[\w.]+',
            'linkedin': r'linkedin\.com/(?:company/[\w-]+|in/[\w-]+)',
            'instagram': r'instagram\.com/[\w.]+',
            'twitter': r'(?:twitter\.com|x\.com)/[\w]+',
            'youtube': r'youtube\.com/(?:user/|channel/|c/)?[\w-]+',
            'github': r'github\.com/[\w-]+',
            'pinterest': r'pinterest\.(?:com|fr)/[\w-]+',
            'tiktok': r'(?:tiktok\.com|vm\.tiktok\.com)/@?[\w.]+',
            'snapchat': r'snapchat\.com/add/[\w-]+',
            'houzz': r'houzz\.(?:com|fr)/[\w-]+',
            'google': r'(?:plus\.google\.com|g\.page)/[\w.+]+',
            'yelp': r'yelp\.(?:com|fr)/[\w-]+',
            'nextdoor': r'nextdoor\.(?:com|fr)/[\w-]+'
        }

    def extract_social_links(self, soup: BeautifulSoup, base_url: str) -> dict:
        """
        Extrait les liens des réseaux sociaux d'une page web
        
        Args:
            soup: Objet BeautifulSoup de la page
            base_url: URL de base pour résoudre les liens relatifs
            
        Returns:
            dict: Dictionnaire des liens sociaux trouvés avec toutes les plateformes initialisées à None
        """
        # Initialiser toutes les plateformes à None
        social_media = {platform: None for platform in self.social_patterns.keys()}
        
        # Recherche dans les liens <a>
        for link in soup.find_all('a', href=True):
            href = urljoin(base_url, link['href'])
            for platform, pattern in self.social_patterns.items():
                if re.search(pattern, href, re.I):
                    social_media[platform] = href
        
        # Recherche dans les meta tags (pour Open Graph et autres)
        meta_tags = soup.find_all('meta', property=lambda x: x and ('og:' in x or 'twitter:' in x))
        for meta in meta_tags:
            content = meta.get('content', '')
            if content:
                for platform, pattern in self.social_patterns.items():
                    if re.search(pattern, content, re.I):
                        social_media[platform] = content
        
        return social_media
