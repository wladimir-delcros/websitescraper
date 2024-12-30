import re
from bs4 import BeautifulSoup
import json
from typing import Dict, Optional

class CompanyDetector:
    def __init__(self):
        # Patterns pour les numéros d'entreprise
        self.patterns = {
            'siren': r'\b(?:SIREN|siren|Siren|siret)\s*:?\s*(\d{9})\b',
            'siret': r'\b(?:SIRET|siret|Siret)\s*:?\s*(\d{14})\b',
            'tva': r'\b(?:TVA|N°\s*TVA|Numéro\s*TVA|VAT)\s*(?:intra(?:communautaire)?)?(?:n°|num[ée]ro)?\s*:?\s*((?:FR|BE|DE|IT|ES)\s*\d{2}\s*\d{9})\b'
        }
        
        # Patterns alternatifs (sans labels)
        self.alt_patterns = {
            'siren': r'\b(\d{9})(?!\d)\b',  # Ne pas capturer les 9 premiers chiffres d'un SIRET
            'siret': r'\b(\d{14})\b',
            'tva': r'\b((?:FR|BE|DE|IT|ES)\s*\d{2}\s*\d{9})\b'
        }

    def clean_number(self, number: str) -> str:
        """Nettoie un numéro en enlevant les espaces et caractères spéciaux"""
        return re.sub(r'[^\dA-Z]', '', number.upper())

    def validate_siren(self, siren: str) -> bool:
        """Valide un numéro SIREN"""
        if not siren or not siren.isdigit() or len(siren) != 9:
            return False
        
        total = 0
        for i, digit in enumerate(siren):
            digit = int(digit)
            if i % 2 == 1:  # Position impaire (en commençant par 0)
                digit = digit * 2
                if digit > 9:
                    digit -= 9
            total += digit
        
        return total % 10 == 0

    def validate_siret(self, siret: str) -> bool:
        """Valide un numéro SIRET"""
        if not siret or not siret.isdigit() or len(siret) != 14:
            return False
        
        # Le SIRET est composé du SIREN (9 premiers chiffres) suivi d'un numéro d'ordre de 5 chiffres
        total = 0
        for i, digit in enumerate(siret):
            digit = int(digit)
            if i % 2 == 0:
                digit = digit * 2
                if digit > 9:
                    digit -= 9
            total += digit
        
        return total % 10 == 0

    def validate_tva(self, tva: str) -> bool:
        """Valide un numéro de TVA intracommunautaire"""
        if not tva:
            return False
        
        # Supprimer les espaces et mettre en majuscules
        tva = tva.replace(" ", "").upper()
        
        # Vérifier le format de base
        if not re.match(r'^[A-Z]{2}\d{11}$', tva):
            return False
        
        # Pour la France, vérifier que les chiffres après FR forment un nombre valide
        if tva.startswith('FR'):
            siren = tva[4:]  # Ignorer 'FR' et les deux premiers chiffres
            return self.validate_siren(siren)
        
        return True

    def extract_company_info(self, html_content: str, url: str) -> Dict[str, Optional[str]]:
        """
        Extrait les informations d'entreprise (SIREN, SIRET, TVA) d'une page HTML
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialiser le résultat
        result = {
            'siren': None,
            'siret': None,
            'tva': None,
            'source': None
        }
        
        # Chercher dans le texte
        text = soup.get_text()
            
        # Chercher SIRET avec les patterns principaux
        for pattern in [self.patterns['siret'], self.alt_patterns['siret']]:
            siret_match = re.search(pattern, text)
            if siret_match:
                siret = siret_match.group(1)
                if self.validate_siret(siret):
                    result['siret'] = siret
                    result['siren'] = siret[:9]
                    result['source'] = url
                    break
        
        # Chercher SIREN si pas trouvé via SIRET
        if not result['siren']:
            for pattern in [self.patterns['siren'], self.alt_patterns['siren']]:
                siren_match = re.search(pattern, text)
                if siren_match:
                    siren = siren_match.group(1)
                    if self.validate_siren(siren):
                        result['siren'] = siren
                        result['source'] = url
                        break
        
        # Chercher TVA
        for pattern in [self.patterns['tva'], self.alt_patterns['tva']]:
            tva_match = re.search(pattern, text)
            if tva_match:
                tva = tva_match.group(1)
                if self.validate_tva(tva):
                    result['tva'] = tva.replace(" ", "")
                    result['source'] = url
                    break
        
        return result
