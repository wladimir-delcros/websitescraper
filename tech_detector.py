import re
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Set
from urllib.parse import urlparse

class TechnologyDetector:
    def __init__(self):
        # Patterns pour la détection des technologies
        self.tech_patterns = {
            'wordpress': {
                'html': [r'wp-content|wp-includes|wordpress'],
                'meta': {'generator': r'WordPress'},
            },
            'drupal': {
                'html': [r'drupal|sites/all|sites/default'],
                'meta': {'generator': r'Drupal'},
            },
            'joomla': {
                'html': [r'joomla|com_content'],
                'meta': {'generator': r'Joomla'},
            },
            'react': {
                'html': [r'react-root|react-modal'],
                'scripts': [r'react\.js|react\.min\.js|react\.production\.min\.js'],
            },
            'vue': {
                'html': [r'v-bind|v-if|v-for|v-model'],
                'scripts': [r'vue\.js|vue\.min\.js|vue\.runtime\.js'],
            },
            'angular': {
                'html': [r'ng-app|ng-controller|ng-model'],
                'scripts': [r'angular\.js|angular\.min\.js'],
            },
            'bootstrap': {
                'html': [r'class="[^"]*\b(?:btn|container|row|col-[a-z]{2}-\d+)\b'],
                'styles': [r'bootstrap\.css|bootstrap\.min\.css'],
            },
            'tailwind': {
                'html': [r'class="[^"]*\b(?:text-[a-z]+-\d+|bg-[a-z]+-\d+)\b'],
                'styles': [r'tailwind\.css|tailwind\.min\.css'],
            },
            'nginx': {
                'headers': {'Server': r'nginx'},
            },
            'apache': {
                'headers': {'Server': r'Apache'},
            },
            'google-analytics': {
                'html': [r'google-analytics\.com|ga\.js|analytics\.js'],
                'scripts': [r'google-analytics\.com|ga\.js|analytics\.js'],
            },
            'matomo': {
                'html': [r'matomo\.js|piwik\.js'],
                'scripts': [r'matomo\.js|piwik\.js'],
            },
            'google-tag-manager': {
                'html': [r'googletagmanager\.com|gtm\.js'],
                'scripts': [r'googletagmanager\.com|gtm\.js'],
            },
            'facebook-pixel': {
                'html': [r'connect\.facebook\.net|fbevents\.js'],
                'scripts': [r'connect\.facebook\.net|fbevents\.js'],
            },
            'woocommerce': {
                'html': [r'woocommerce|wc-api'],
                'meta': {'generator': r'WooCommerce'},
            },
            'shopify': {
                'html': [r'shopify|myshopify\.com'],
                'meta': {'generator': r'Shopify'},
            },
            'prestashop': {
                'html': [r'prestashop|presta-shop'],
                'meta': {'generator': r'PrestaShop'},
            },
            'cloudflare': {
                'headers': {'Server': r'cloudflare'},
            },
            'varnish': {
                'headers': {'X-Varnish': r'.+'},
            },
            'jquery': {
                'scripts': [r'jquery\.js|jquery\.min\.js'],
            },
            'lodash': {
                'scripts': [r'lodash\.js|lodash\.min\.js'],
            },
            'moment': {
                'scripts': [r'moment\.js|moment\.min\.js'],
            },
            'font-awesome': {
                'styles': [r'font-awesome\.css|fontawesome'],
            },
            'google-fonts': {
                'styles': [r'fonts\.googleapis\.com'],
            },
            'recaptcha': {
                'html': [r'www\.google\.com/recaptcha|recaptcha\.js'],
                'scripts': [r'www\.google\.com/recaptcha|recaptcha\.js'],
            },
            'hcaptcha': {
                'html': [r'hcaptcha\.com|hcaptcha\.js'],
                'scripts': [r'hcaptcha\.com|hcaptcha\.js'],
            },
            'webpack': {
                'scripts': [r'webpack'],
            },
            'babel': {
                'scripts': [r'babel'],
            },
            'amp': {
                'html': [r'⚡|amp-'],
                'meta': {'mobile-web-app-capable': r'yes'},
            },
        }

    def detect_technologies(self, html_content: str, headers: Dict = None) -> Dict[str, List[str]]:
        """
        Détecte les technologies utilisées sur une page web
        
        Args:
            html_content: Contenu HTML de la page
            headers: En-têtes HTTP de la réponse (optionnel)
            
        Returns:
            Dict avec les catégories de technologies et leurs détections
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        detected_tech = {
            'cms': set(),
            'frameworks_js': set(),
            'frameworks_css': set(),
            'serveurs': set(),
            'analytics': set(),
            'marketing': set(),
            'ecommerce': set(),
            'performance': set(),
            'libraries_js': set(),
            'fonts': set(),
            'securite': set(),
            'build_tools': set(),
            'mobile': set(),
        }

        # Mapping des technologies vers leurs catégories
        tech_categories = {
            'wordpress': 'cms',
            'drupal': 'cms',
            'joomla': 'cms',
            'react': 'frameworks_js',
            'vue': 'frameworks_js',
            'angular': 'frameworks_js',
            'bootstrap': 'frameworks_css',
            'tailwind': 'frameworks_css',
            'nginx': 'serveurs',
            'apache': 'serveurs',
            'google-analytics': 'analytics',
            'matomo': 'analytics',
            'google-tag-manager': 'marketing',
            'facebook-pixel': 'marketing',
            'woocommerce': 'ecommerce',
            'shopify': 'ecommerce',
            'prestashop': 'ecommerce',
            'cloudflare': 'performance',
            'varnish': 'performance',
            'jquery': 'libraries_js',
            'lodash': 'libraries_js',
            'moment': 'libraries_js',
            'font-awesome': 'fonts',
            'google-fonts': 'fonts',
            'recaptcha': 'securite',
            'hcaptcha': 'securite',
            'webpack': 'build_tools',
            'babel': 'build_tools',
            'amp': 'mobile',
            'pwa': 'mobile',
        }

        # Analyse des balises meta
        meta_tags = soup.find_all('meta')
        meta_data = {}
        for meta in meta_tags:
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_data[name.lower()] = content

        # Analyse des scripts
        scripts = [script.get('src', '') for script in soup.find_all('script', src=True)]
        scripts_content = ' '.join([script.string or '' for script in soup.find_all('script')])

        # Analyse des styles
        styles = [link.get('href', '') for link in soup.find_all('link', rel='stylesheet')]
        styles_content = ' '.join([style.string or '' for style in soup.find_all('style')])

        # Détection pour chaque technologie
        for tech, patterns in self.tech_patterns.items():
            detected = False

            # Vérification des patterns HTML
            if 'html' in patterns:
                for pattern in patterns['html']:
                    if re.search(pattern, str(soup), re.I):
                        detected = True
                        break

            # Vérification des meta tags
            if 'meta' in patterns and not detected:
                for meta_name, pattern in patterns['meta'].items():
                    if meta_name in meta_data and re.search(pattern, meta_data[meta_name], re.I):
                        detected = True
                        break

            # Vérification des scripts
            if 'scripts' in patterns and not detected:
                for pattern in patterns['scripts']:
                    if any(re.search(pattern, script, re.I) for script in scripts):
                        detected = True
                        break
                    if re.search(pattern, scripts_content, re.I):
                        detected = True
                        break

            # Vérification des styles
            if 'styles' in patterns and not detected:
                for pattern in patterns['styles']:
                    if any(re.search(pattern, style, re.I) for style in styles):
                        detected = True
                        break
                    if re.search(pattern, styles_content, re.I):
                        detected = True
                        break

            # Vérification des headers
            if headers and 'headers' in patterns and not detected:
                for header_name, pattern in patterns['headers'].items():
                    header_value = headers.get(header_name, '')
                    if header_value and re.search(pattern, header_value, re.I):
                        detected = True
                        break

            if detected:
                category = tech_categories.get(tech)
                if category:
                    detected_tech[category].add(tech)

        # Conversion des sets en listes pour la sérialisation JSON
        return {k: list(v) for k, v in detected_tech.items() if v}

    def get_headers_info(self, headers: Dict) -> Dict[str, str]:
        """
        Extrait les informations importantes des en-têtes HTTP
        
        Args:
            headers: Dictionnaire des en-têtes HTTP
            
        Returns:
            Dict avec les informations des en-têtes
        """
        return {
            'server': headers.get('Server', ''),
            'x_powered_by': headers.get('X-Powered-By', ''),
            'content_type': headers.get('Content-Type', ''),
            'content_encoding': headers.get('Content-Encoding', '')
        }

    def get_security_headers(self, headers: Dict) -> Dict[str, str]:
        """
        Vérifie la présence des en-têtes de sécurité
        
        Args:
            headers: Dictionnaire des en-têtes HTTP
            
        Returns:
            Dict avec les en-têtes de sécurité
        """
        security_headers = {
            'x_frame_options': headers.get('X-Frame-Options', ''),
            'x_xss_protection': headers.get('X-XSS-Protection', ''),
            'x_content_type_options': headers.get('X-Content-Type-Options', ''),
            'content_security_policy': headers.get('Content-Security-Policy', ''),
            'strict_transport_security': headers.get('Strict-Transport-Security', ''),
            'referrer_policy': headers.get('Referrer-Policy', '')
        }
        return security_headers
