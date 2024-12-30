import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
from collections import defaultdict
import re
from company_detector import CompanyDetector
import time
import logging
import ssl
import importlib.util

class PageCrawler:
    def __init__(self, max_pages: int = 10):
        self.max_pages = max_pages
        self.company_detector = CompanyDetector()
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.visited = set()
        self.priority_urls = set()
        self.html_cache = {}  # Cache pour le contenu HTML
        self.semaphore = asyncio.Semaphore(5)  # Limite les requêtes parallèles
        
        # Patterns pour les pages prioritaires (compilés)
        self.priority_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in [
            r'contact',
            r'about',
            r'apropos',
            r'qui-sommes-nous',
            r'about-us',
            r'contactez-nous',
            r'contact-us',
            r'mentions-legales'
        ]]  # Réduit la liste pour se concentrer sur les plus importants

        # Parser HTML rapide
        self.parser = 'lxml'
        if not importlib.util.find_spec('lxml'):
            self.parser = 'html.parser'

    async def get_page_content(self, session: aiohttp.ClientSession, url: str, headers: dict) -> tuple[str, dict]:
        """Récupère le contenu d'une page avec cache et compression"""
        if url in self.html_cache:
            return self.html_cache[url], {}
            
        async with self.semaphore:
            try:
                # Ajouter l'acceptation de la compression
                headers['Accept-Encoding'] = 'gzip, deflate'
                async with session.get(url, headers=headers, ssl=self.ssl_context, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        self.html_cache[url] = html
                        return html, dict(response.headers)
                    else:
                        logging.error(f"Erreur HTTP {response.status} pour {url}")
                        return "", {}
            except Exception as e:
                logging.error(f"Erreur lors de la récupération de {url}: {str(e)}")
                return "", {}

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extrait tous les liens d'une page qui appartiennent au même domaine
        Version optimisée avec set et parsing rapide
        """
        links = set()
        base_domain = urlparse(base_url).netloc
        
        # Extraction rapide des liens avec sélecteur CSS
        for tag in soup.select('a[href]'):
            href = tag.get('href', '').strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            try:
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if parsed.netloc == base_domain and parsed.scheme in ('http', 'https'):
                    # Normaliser l'URL
                    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        normalized += f"?{parsed.query}"
                    links.add(normalized)
            except:
                continue
        
        return list(links)

    def is_priority_page(self, url: str) -> bool:
        """
        Détermine si une URL correspond à une page prioritaire
        Version optimisée avec patterns compilés
        """
        try:
            path = urlparse(url).path.lower()
            return any(pattern.search(path) for pattern in self.priority_patterns)
        except:
            return False

    async def crawl_priority_pages(self, start_url: str, headers: dict):
        """Crawl optimisé des pages prioritaires"""
        timeout = aiohttp.ClientTimeout(total=20, connect=5)
        connector = aiohttp.TCPConnector(ssl=False, limit=5, force_close=True)
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # Toujours ajouter l'URL de départ
                self.priority_urls.add(start_url)
                
                html, headers_info = await self.get_page_content(session, start_url, headers)
                if html:
                    soup = BeautifulSoup(html, self.parser)
                    initial_links = self.extract_links(soup, start_url)
                    
                    # Filtrer d'abord les liens prioritaires
                    priority_links = [link for link in initial_links if self.is_priority_page(link)]
                    self.priority_urls.update(priority_links)
                    
                    # Créer les tâches pour les liens prioritaires uniquement
                    tasks = []
                    for link in priority_links[:3]:  # Réduit à 3 liens prioritaires
                        if len(self.visited) < self.max_pages:
                            tasks.append(self.collect_priority_urls(session, link, headers))
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                
                return self.format_crawl_results(self.priority_urls)
                
        except Exception as e:
            logging.error(f"Erreur lors du crawl: {str(e)}")
            return self.format_crawl_results(self.priority_urls)

    async def collect_priority_urls(self, session, url: str, headers: dict):
        """Collecte optimisée des URLs prioritaires"""
        if url in self.visited:
            return
        self.visited.add(url)
        
        html, _ = await self.get_page_content(session, url, headers)
        if html is None:  # Vérifie explicitement None
            return
            
        soup = BeautifulSoup(html, self.parser)
        links = self.extract_links(soup, url)
        priority_links = [link for link in links if self.is_priority_page(link)]
        self.priority_urls.update(priority_links)

    def format_crawl_results(self, results: Set[str]) -> List[str]:
        """
        Formate les résultats du crawl dans l'ordre de priorité
        """
        # Retourner toutes les URLs trouvées
        return list(results)

    # Mots-clés pour les pages prioritaires dans différentes langues
    priority_keywords = {
        'home': [
            '', 'home', 'index', 'accueil', 'inicio', 'startseite', 'homepage',
            'home-page', 'main', 'welcome', 'bienvenue', 'bienvenido', 'willkommen',
            'start', 'portada', 'principal'
        ],
        'contact': [
            'contact', 'contacts', 'kontakt', 'contacto', 'contactenos', 'nous-contacter',
            'contact-us', 'contactez-nous', 'get-in-touch', 'reach-us', 'write-to-us',
            'contactar', 'kontaktiere-uns', 'about-us', 'about', 'a-propos', 'a-propos-de-nous',
            'qui-sommes-nous', 'notre-equipe', 'our-team', 'team', 'equipe', 'devis',
            'demande-de-devis', 'quote', 'get-quote', 'estimate', 'callback', 'rappel',
            'demande-de-rappel', 'rdv', 'appointment', 'prendre-rdv', 'book-appointment'
        ],
        'legal': [
            'legal', 'mentions-legales', 'privacy', 'privacy-policy', 'datenschutz',
            'confidentialite', 'mentions', 'terms', 'conditions', 'cgv', 'cgu',
            'impressum', 'aviso-legal', 'politica-privacidad', 'legal-notice',
            'legal-mentions', 'terms-of-use', 'terms-of-service', 'tos', 'cookies',
            'cookie-policy', 'politique-cookies', 'rgpd', 'gdpr', 'politique-confidentialite',
            'confidentialite', 'disclaimer', 'avertissement', 'credits', 'credits-legaux',
            'sitemap', 'plan-du-site', 'plan-site', 'mapa-del-sitio', 'accessibility',
            'accessibilite', 'accessibilidad'
        ]
    }
