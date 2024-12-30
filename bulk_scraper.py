import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import tqdm
import aiofiles
from contact_extractor import ContactExtractor
from social_media_extractor import SocialMediaExtractor
from tech_detector import TechnologyDetector
from company_detector import CompanyDetector
from data_saver import DataSaver
import sys
import uuid
import random
from functools import lru_cache
import hashlib
import argparse
import time
import logging
from page_crawler import PageCrawler

class ContactScraper:
    def __init__(self):
        """
        Initialise le scraper avec ses extracteurs
        """
        self.contact_extractor = ContactExtractor()
        self.social_media_extractor = SocialMediaExtractor()
        self.tech_detector = TechnologyDetector()
        self.company_detector = CompanyDetector()
        
        # Liste des User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        ]

    def get_random_headers(self):
        """
        Génère des en-têtes aléatoires pour éviter la détection
        """
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def fetch_url(self, session: aiohttp.ClientSession, url: str, headers: dict) -> tuple[str, dict]:
        """
        Récupère le contenu d'une URL avec gestion des erreurs et des timeouts
        """
        try:
            async with session.get(url, headers=headers) as response:
                # Essayer d'abord avec l'encodage spécifié dans les headers
                content_type = response.headers.get('content-type', '')
                charset = None
                if 'charset=' in content_type:
                    charset = content_type.split('charset=')[-1]
                
                # Lire le contenu
                content = await response.read()
                
                # Essayer différents encodages
                for encoding in [charset, 'utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
                    if not encoding:
                        continue
                    try:
                        html = content.decode(encoding)
                        return html, dict(response.headers)
                    except UnicodeDecodeError:
                        continue
                
                return "", {}
                
        except Exception as e:
            return "", {}

    def extract_contacts(self, html: str, url: str) -> dict:
        """
        Extrait toutes les informations de contact d'une page HTML
        """
        contacts = {
            'emails': [],  
            'phones': [],  
            'social_media': {},
            'url': url
        }

        # Parse le HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraction des emails et téléphones
        emails, phones = self.contact_extractor.extract_contacts(soup)
        
        # Ajout des sources pour les emails
        for email in emails:
            contacts['emails'].append({
                'value': email,
                'sources': [url]  
            })
        
        # Ajout des sources pour les téléphones
        for phone in phones:
            contacts['phones'].append({
                'value': phone,
                'sources': [url]  
            })
        
        # Extraction des liens sociaux
        contacts['social_media'] = self.social_media_extractor.extract_social_links(soup, url)
        
        return contacts

    async def process_url(self, session: aiohttp.ClientSession, url: str, crawl: bool = True):
        """
        Traite une URL et ses pages prioritaires pour extraire les contacts et technologies
        """
        # Normaliser l'URL de départ
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Choisir un User-Agent pour tout le site
        headers = self.get_random_headers()
        
        crawler = PageCrawler(max_pages=5)
        
        # Si crawl est False, on ne traite que la page d'accueil
        if not crawl:
            priority_pages = {url}
        else:
            priority_pages = await crawler.crawl_priority_pages(url, headers)
        
        # Initialiser les résultats
        results = {
            'url': url,
            'emails': [],
            'phones': [],
            'social_media': {},
            'technologies': [],
            'headers_info': {},
            'security_headers': {},
            'crawled_pages': [],  
            'company_info': {
                'siren': None,
                'siret': None,
                'tva': None,
                'source': None
            }
        }
        
        # Traiter chaque page prioritaire
        for page_url in priority_pages:
            try:
                html, response_headers = await self.fetch_url(session, page_url, headers)
                if not html:
                    continue
                
                # Déterminer le type de page
                page_type = self.determine_page_type(page_url)
                if not page_type:
                    page_type = 'home' if page_url == url else 'other'
                
                # Ajouter la page aux pages crawlées
                results['crawled_pages'].append({
                    'url': page_url,
                    'type': page_type
                })
                
                # Extraction des contacts
                page_contacts = self.extract_contacts(html, page_url)
                
                # Fusionner les emails
                for email in page_contacts['emails']:
                    if not any(e['value'] == email['value'] for e in results['emails']):
                        results['emails'].append({
                            'value': email['value'],
                            'sources': [page_url]
                        })
                    else:
                        # Ajouter la source si l'email existe déjà
                        for existing_email in results['emails']:
                            if existing_email['value'] == email['value'] and page_url not in existing_email['sources']:
                                existing_email['sources'].append(page_url)
                
                # Fusionner les téléphones
                for phone in page_contacts['phones']:
                    if not any(p['value'] == phone['value'] for p in results['phones']):
                        results['phones'].append({
                            'value': phone['value'],
                            'sources': [page_url]
                        })
                    else:
                        # Ajouter la source si le téléphone existe déjà
                        for existing_phone in results['phones']:
                            if existing_phone['value'] == phone['value'] and page_url not in existing_phone['sources']:
                                existing_phone['sources'].append(page_url)
                
                # Fusionner les réseaux sociaux
                for platform, url in page_contacts['social_media'].items():
                    if url and platform not in results['social_media']:
                        results['social_media'][platform] = url
                
                # Détecter les technologies si pas encore fait
                if not results['technologies']:
                    results['technologies'] = self.tech_detector.detect_technologies(html)
                    results['headers_info'] = self.tech_detector.get_headers_info(response_headers)
                    results['security_headers'] = self.tech_detector.get_security_headers(response_headers)
                
                # Extraction des informations d'entreprise
                company_info = self.company_detector.extract_company_info(html, page_url)
                if company_info['siren'] and not results['company_info']['siren']:
                    results['company_info'] = company_info
                elif company_info['siret'] and not results['company_info']['siret']:
                    results['company_info'] = company_info
                elif company_info['tva'] and not results['company_info']['tva']:
                    results['company_info'] = company_info
                    
            except Exception as e:
                logging.error(f"Erreur lors du traitement de {page_url}: {str(e)}")
                continue
        
        return results

    async def bulk_scrape(self, urls: list, crawl: bool = True) -> list:
        """
        Scrape en masse une liste d'URLs
        """
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        connector = aiohttp.TCPConnector(ssl=False, limit=5)
        
        print(f"Début du scraping de {len(urls)} URLs...")
        progress_bar = tqdm.tqdm(total=len(urls), unit='site')
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            results = []
            # Traiter les URLs par lots de 3 pour éviter la surcharge
            batch_size = 3
            
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                batch_tasks = []
                
                for url in batch:
                    # Utiliser un timeout plus court pour chaque URL
                    task = asyncio.create_task(
                        asyncio.wait_for(
                            self.process_url(session, url, crawl),
                            timeout=10
                        )
                    )
                    batch_tasks.append(task)
                
                try:
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    for result in batch_results:
                        if isinstance(result, Exception):
                            if not isinstance(result, asyncio.TimeoutError):
                                print(f"Error in batch: {str(result)}")
                            continue
                        if result:
                            results.append(result)
                    progress_bar.update(len(batch))
                except Exception as e:
                    print(f"Batch processing error: {str(e)}")
                
                # Petit délai entre les lots
                await asyncio.sleep(0.5)
            
            progress_bar.close()
            return results

    async def save_results(self, results: list, filename: str):
        """Sauvegarde les résultats dans un fichier JSON et CSV"""
        # Utiliser DataSaver pour sauvegarder les résultats
        data_saver = DataSaver()
        json_path, csv_path = data_saver.save_all(results)
        print(f"Résultats sauvegardés dans:\nJSON: {json_path}\nCSV: {csv_path}")

    def format_response(self, result: dict) -> dict:
        """
        Formate les résultats au format demandé
        """
        social_media = result['social_media']
        
        # Créer le tableau des réseaux sociaux
        social_media_array = []
        for platform, url in social_media.items():
            if url:  # N'ajouter que les réseaux sociaux trouvés
                social_media_array.append({
                    "platform": platform,
                    "url": url
                })

        response = {
            "status": "OK",
            "request_id": str(uuid.uuid4()),
            "data": [{
                "domain": result['url'],
                "query": result['url'],
                "crawled_pages": result.get('crawled_pages', []),  
                "emails": [
                    {
                        "value": email,
                        "sources": [result['url']]
                    } for email in result['emails']
                ],
                "phone_numbers": [
                    {
                        "value": phone,
                        "sources": [result['url']]
                    } for phone in result['phones']
                ],
                "social_media": social_media_array
            }],
            "technical_data": {
                "technologies": result.get('technologies', []),
                "headers_info": result.get('headers_info', {}),
                "security_headers": result.get('security_headers', {})
            }
        }
        return response

    def extract_security_headers(self, headers: dict) -> dict:
        """
        Extrait les en-têtes de sécurité
        """
        security_headers = {}
        
        for key, value in headers.items():
            if key.lower() in ['content-security-policy', 'x-frame-options', 'x-xss-protection', 'strict-transport-security']:
                security_headers[key] = value
        
        return security_headers

    async def process_page(self, html: str, response_headers: dict, page_url: str, url: str, results: dict):
        """
        Traite une page de manière asynchrone
        """
        try:
            # Déterminer le type de page
            page_type = self.determine_page_type(page_url)
            
            # Ajouter la page aux pages crawlées
            results['crawled_pages'].append({
                'url': page_url,
                'type': page_type
            })
            
            # Extraction des contacts de manière asynchrone
            page_contacts = await asyncio.create_task(
                asyncio.to_thread(self.contact_extractor.extract_contacts, html, page_url)
            )
            
            # Fusionner les emails
            for email in page_contacts['emails']:
                if not any(e['value'] == email['value'] for e in results['emails']):
                    results['emails'].append({
                        'value': email['value'],
                        'sources': [page_url]
                    })
                else:
                    for existing_email in results['emails']:
                        if existing_email['value'] == email['value'] and page_url not in existing_email['sources']:
                            existing_email['sources'].append(page_url)
            
            # Fusionner les téléphones
            for phone in page_contacts['phones']:
                if not any(p['value'] == phone['value'] for p in results['phones']):
                    results['phones'].append({
                        'value': phone['value'],
                        'sources': [page_url]
                    })
                else:
                    for existing_phone in results['phones']:
                        if existing_phone['value'] == phone['value'] and page_url not in existing_phone['sources']:
                            existing_phone['sources'].append(page_url)
            
            # Fusionner les réseaux sociaux
            results['social_media'].update(page_contacts['social_media'])
            
            # Détecter les technologies si pas encore fait
            if not results['technologies']:
                tech_task = asyncio.create_task(
                    asyncio.to_thread(self.tech_detector.detect_technologies, html)
                )
                results['technologies'] = await tech_task
                results['headers_info'] = self.tech_detector.get_headers_info(response_headers)
                results['security_headers'] = self.tech_detector.get_security_headers(response_headers)
            
            # Extraction des informations d'entreprise de manière asynchrone
            company_task = asyncio.create_task(
                asyncio.to_thread(self.company_detector.extract_company_info, html, page_url)
            )
            company_info = await company_task
            
            if company_info['siren'] and not results['company_info']['siren']:
                results['company_info'] = company_info
            elif company_info['siret'] and not results['company_info']['siret']:
                results['company_info'] = company_info
            elif company_info['tva'] and not results['company_info']['tva']:
                results['company_info'] = company_info
                
        except Exception as e:
            logging.error(f"Erreur lors du traitement de la page {page_url}: {str(e)}")

    def determine_page_type(self, url: str) -> str:
        """
        Détermine le type de page en fonction de l'URL
        """
        url_lower = url.lower()
        
        # Retirer le protocole et www pour la comparaison
        url_clean = url_lower.replace('http://', '').replace('https://', '').replace('www.', '')
        # Retirer les paramètres et fragments
        url_clean = url_clean.split('?')[0].split('#')[0]
        # Retirer le dernier slash s'il existe
        if url_clean.endswith('/'):
            url_clean = url_clean[:-1]
            
        # Si l'URL nettoyée ne contient que le domaine, c'est la page d'accueil
        if '/' not in url_clean:
            return 'home'
            
        if url_lower.endswith('/contact') or url_lower.endswith('/contact/'):
            return 'contact'
        elif url_lower.endswith('/mentions-legales') or url_lower.endswith('/mentions-legales/'):
            return 'legal'
        elif url_lower.endswith('/a-propos') or url_lower.endswith('/a-propos/') or url_lower.endswith('/about') or url_lower.endswith('/about/'):
            return 'about'
        else:
            return 'other'

if __name__ == "__main__":
    import argparse
    
    # Création du parser d'arguments
    parser = argparse.ArgumentParser(description='Web scraper pour extraire les informations de contact')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--urls', nargs='+', help='URLs des sites à scraper')
    group.add_argument('--bulk', action='store_true', help='Lire les URLs depuis websites.txt')
    parser.add_argument('-o', '--output', default='resultats_scraping.json',
                      help='Fichier de sortie (default: resultats_scraping.json)')
    parser.add_argument('--crawl', action='store_true', default=False,
                      help='Si activé, crawl tout le site. Sinon, analyse uniquement la page d\'accueil')
    
    # Parse les arguments
    args = parser.parse_args()
    
    # Si l'option bulk est activée, lire les URLs depuis le fichier
    if args.bulk:
        try:
            with open('websites.txt', 'r', encoding='utf-8') as f:
                args.urls = [line.strip() for line in f if line.strip()]
            print(f"Chargement de {len(args.urls)} URLs depuis websites.txt")
        except FileNotFoundError:
            print("Erreur: Le fichier websites.txt n'a pas été trouvé")
            sys.exit(1)
    elif not args.urls:
        parser.error("Vous devez spécifier au moins une URL avec --urls ou utiliser --bulk")
    
    # Création et exécution du scraper
    scraper = ContactScraper()
    
    async def main():
        # Scraper les URLs
        results = await scraper.bulk_scrape(args.urls, args.crawl)
        
        # Préparer le résultat final
        final_result = {
            "status": "OK",
            "request_id": str(uuid.uuid4()),
            "data": []
        }
        
        # Ajouter les résultats pour chaque domaine
        for result in results:
            if result:  # Ignorer les résultats vides
                domain_result = {
                    "domain": result["url"],
                    "crawled_pages": result["crawled_pages"],
                    "emails": result["emails"],
                    "phone_numbers": result["phones"],
                    "social_media": result["social_media"],
                    "technologies": result["technologies"],
                    "headers_info": result["headers_info"],
                    "security_headers": result["security_headers"],
                    "company_info": result["company_info"]
                }
                final_result["data"].append(domain_result)
        
        # Afficher le résultat formaté dans la console
        print(json.dumps([final_result], indent=2, ensure_ascii=False))
        
        # Sauvegarder les résultats avec DataSaver
        await scraper.save_results([final_result], args.output)

    # Exécuter le scraper
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
