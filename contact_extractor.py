import re
from bs4 import BeautifulSoup
import base64
from html import unescape
from country_codes import COUNTRY_CODES
from phone_keywords import PHONE_KEYWORDS, EXCLUDE_PATTERNS
import logging

class ContactExtractor:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Utiliser la liste complète des codes pays
        self.country_codes = COUNTRY_CODES
        
        # Construire le pattern de contexte avec tous les mots-clés
        self.phone_context_before = r'(?:(?:^|[^\w])|(?:' + '|'.join(PHONE_KEYWORDS) + r')[: .-]*)?'
        self.phone_context_after = r'(?:$|[^\d])'
        
        # Patterns à exclure (compilés)
        self.exclude_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in EXCLUDE_PATTERNS]
        
        # Construction et compilation des patterns de téléphone
        phone_patterns = [
            # Format français avec contexte (plus permissif)
            rf"{self.phone_context_before}(?:(?:(?:\+|00)?33|0)\s*[1-9](?:[\s.-]*\d{{2}}){{4}}){self.phone_context_after}",
            
            # Format nord-américain avec contexte (plus permissif)
            rf"{self.phone_context_before}(?:\+?1[-. ]?)?\(?[2-9][0-9]{{2}}\)?[-. ]?[0-9]{{3}}[-. ]?[0-9]{{4}}{self.phone_context_after}",
            
            # Format international avec contexte (plus permissif)
            rf"{self.phone_context_before}(?:\+|00)?(?:{'|'.join(code for code, _ in self.country_codes.values())})\s*[1-9][0-9]{{7,14}}{self.phone_context_after}",
            
            # Format générique pour les numéros sans indicatif
            rf"{self.phone_context_before}0[1-9](?:[\s.-]*\d{{2}}){{4}}{self.phone_context_after}",
        ]
        self.phone_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in phone_patterns]
        
        # Cache pour les numéros déjà nettoyés
        self.clean_number_cache = {}

    def is_excluded_pattern(self, text: str) -> bool:
        """
        Vérifie si le texte correspond à un pattern à exclure
        """
        text = text.lower().strip()
        
        # Vérifier si le texte est dans un contexte qui indique que ce n'est pas un numéro de téléphone
        if any(pattern.search(text) for pattern in self.exclude_patterns):
            return True
            
        # Vérifier le contexte immédiat (5 caractères avant et après)
        context = text[-5:] + text[:5]
        suspicious_patterns = [
            r'id',
            r'version',
            r'timestamp',
            r'date',
            r'time',
            r'size',
            r'width',
            r'height',
            r'index',
            r'item',
            r'row',
            r'col'
        ]
        
        if any(pattern in context.lower() for pattern in suspicious_patterns):
            return True
            
        return False

    def clean_phone_number(self, phone: str) -> str:
        """Nettoie et normalise un numéro de téléphone avec cache"""
        if phone in self.clean_number_cache:
            return self.clean_number_cache[phone]
            
        try:
            if self.is_excluded_pattern(phone):
                self.clean_number_cache[phone] = None
                return None
                
            # Supprimer tous les caractères non numériques sauf + au début
            cleaned = re.sub(r'[^\d+]', '', phone)
            
            # Traitement rapide des cas communs
            if not cleaned or len(cleaned) < 8:
                self.clean_number_cache[phone] = None
                return None
                
            result = None
            # Format français
            if cleaned.startswith('0') and len(cleaned) == 10:
                if cleaned[1] in '12345678':
                    result = f"+33{cleaned[1:]}"
            # Format international
            elif cleaned.startswith('+'):
                if 10 <= len(cleaned) <= 15:
                    result = cleaned
            # Format avec 00
            elif cleaned.startswith('00'):
                if 11 <= len(cleaned) <= 15:
                    result = f"+{cleaned[2:]}"
            
            self.clean_number_cache[phone] = result
            return result
            
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage du numéro {phone}: {str(e)}")
            self.clean_number_cache[phone] = None
            return None

    def is_valid_phone(self, phone: str) -> bool:
        """
        Vérifie si un numéro de téléphone est valide
        """
        try:
            if not phone or self.is_excluded_pattern(phone):
                return False
                
            # Le numéro doit être au format international maintenant
            if not phone.startswith('+'):
                return False
                
            # Supprimer les espaces pour la vérification
            cleaned = phone.replace(' ', '')
            
            # Vérifier la longueur (entre 8 et 15 chiffres pour les formats internationaux)
            if not (8 <= len(cleaned) <= 15):
                return False
                
            # Vérifier que le numéro ne contient que des chiffres après le +
            if not cleaned[1:].isdigit():
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de la validation du numéro {phone}: {str(e)}")
            return False

    def extract_phones(self, soup: BeautifulSoup) -> set:
        """Extrait les numéros de téléphone d'une page web (optimisé)"""
        phones = set()
        try:
            # Extraction du texte visible uniquement des balises pertinentes
            text_blocks = []
            for tag in soup.find_all(['p', 'div', 'span', 'a', 'li', 'td']):
                if tag.string:
                    text_blocks.append(tag.string)
                elif tag.name == 'a' and tag.get('href', '').startswith('tel:'):
                    phone = tag['href'].replace('tel:', '').strip()
                    cleaned = self.clean_phone_number(phone)
                    if cleaned:
                        phones.add(cleaned)
            
            # Traitement du texte en un seul bloc
            text_content = ' '.join(text_blocks)
            
            # Recherche des numéros avec les patterns compilés
            for pattern in self.phone_patterns:
                for match in pattern.finditer(text_content):
                    phone = match.group().strip()
                    cleaned = self.clean_phone_number(phone)
                    if cleaned:
                        phones.add(cleaned)
            
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des numéros de téléphone: {str(e)}")
        
        return phones

    def extract_contacts(self, soup: BeautifulSoup):
        """
        Extrait les emails et numéros de téléphone d'une page
        """
        logging.info("Début de l'extraction des contacts")
        try:
            emails = set()
            phones = set()
            
            # Extraction du texte visible
            text_content = ' '.join([text for text in soup.stripped_strings])
            logging.debug(f"Texte visible extrait: {text_content[:200]}...")
            
            # Extraction des emails
            emails.update(self.email_pattern.findall(text_content))
            emails.update(self.email_pattern.findall(str(soup)))
            
            # Recherche spécifique dans les balises qui contiennent souvent des contacts
            for tag in soup.find_all(['a', 'div', 'span', 'p', 'script', 'meta']):
                # Vérifier le contenu de la balise
                tag_text = tag.get_text()
                if tag_text:
                    # Recherche d'emails
                    found_emails = self.email_pattern.findall(tag_text)
                    emails.update(found_emails)
                    
                    # Recherche de téléphones
                    for pattern in self.phone_patterns:
                        found_phones = pattern.findall(tag_text)
                        for phone in found_phones:
                            cleaned = self.clean_phone_number(phone)
                            if cleaned:
                                phones.add(cleaned)
            
            logging.info(f"Emails trouvés: {emails}")
            logging.info(f"Téléphones trouvés: {phones}")
            
            return list(emails), list(phones)
            
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des contacts: {str(e)}", exc_info=True)
            return [], []
