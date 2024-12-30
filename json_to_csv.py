import json
import csv
import pandas as pd
from typing import List, Dict
from itertools import chain

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Aplatit un dictionnaire imbriqué"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Pour les listes, on crée une colonne pour chaque élément possible
            if v and isinstance(v[0], dict):
                # Si c'est une liste de dictionnaires
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
            else:
                # Si c'est une liste simple, on la joint en string
                items.append((new_key, '|'.join(map(str, v)) if v else ''))
        else:
            items.append((new_key, v))
    return dict(items)

def get_all_possible_keys(data: List[Dict]) -> set:
    """Récupère toutes les clés possibles des données"""
    all_keys = set()
    for item in data:
        flattened = flatten_dict(item)
        all_keys.update(flattened.keys())
    return all_keys

def process_technologies(technologies):
    """Traite les technologies pour les convertir en format CSV"""
    if isinstance(technologies, list):
        return {'other': technologies}  # Convertit la liste en dictionnaire
    return technologies

def json_to_csv(json_file: str, csv_file: str):
    """Convertit le fichier JSON en CSV"""
    # Lire le fichier JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire les données pertinentes
    rows = []
    for item in data:
        if 'data' in item and item['data']:
            for site_data in item['data']:
                # Créer une ligne pour chaque domaine
                row = {
                    'domain': site_data['domain'],
                    'status': item['status'],
                    'request_id': item['request_id']
                }
                
                # Traiter les pages crawlées
                if 'crawled_pages' in site_data:
                    for i, page in enumerate(site_data['crawled_pages']):
                        row[f'page_{i}_url'] = page['url']
                        row[f'page_{i}_type'] = page['type']
                
                # Traiter les emails
                if 'emails' in site_data:
                    for i, email in enumerate(site_data['emails']):
                        row[f'email_{i}'] = email['value']
                        row[f'email_{i}_sources'] = '|'.join(email['sources'])
                
                # Traiter les numéros de téléphone
                if 'phone_numbers' in site_data:
                    for i, phone in enumerate(site_data['phone_numbers']):
                        row[f'phone_{i}'] = phone['value']
                        row[f'phone_{i}_sources'] = '|'.join(phone['sources'])
                
                # Traiter les réseaux sociaux
                if 'social_media' in site_data:
                    for platform, url in site_data['social_media'].items():
                        row[f'social_{platform}'] = url
                
                # Traiter les technologies
                technologies = process_technologies(site_data.get('technologies', {}))
                for category, techs in technologies.items():
                    if isinstance(techs, list):
                        row[f'tech_{category}'] = ','.join(techs)
                    else:
                        row[f'tech_{category}'] = str(techs)
                
                # Traiter les informations d'en-têtes
                if 'headers_info' in site_data:
                    for header, value in site_data['headers_info'].items():
                        row[f'header_{header}'] = value
                
                # Traiter les en-têtes de sécurité
                if 'security_headers' in site_data:
                    for header, value in site_data['security_headers'].items():
                        row[f'security_{header}'] = value
                
                # Traiter les informations d'entreprise
                if 'company_info' in site_data:
                    for info, value in site_data['company_info'].items():
                        row[f'company_{info}'] = value
                
                rows.append(row)
    
    # Créer un DataFrame pandas
    df = pd.DataFrame(rows)
    
    # Remplir les valeurs manquantes avec des chaînes vides
    df = df.fillna('')
    
    # Sauvegarder en CSV
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    json_file = 'resultats_scraping.json'
    csv_file = 'resultats_scraping.csv'
    json_to_csv(json_file, csv_file)
    print(f"Conversion terminée. Résultats sauvegardés dans {csv_file}")
