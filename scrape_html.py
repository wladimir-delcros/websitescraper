import requests
import json
from pathlib import Path
import time

def scrape_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Erreur lors du scraping de {url}: {str(e)}"

def main():
    # Lire le fichier JSON
    with open('resultats_scraping.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Créer un dossier pour stocker les fichiers HTML
    html_folder = Path('html_content')
    html_folder.mkdir(exist_ok=True)

    # Pour chaque site dans les données
    for item in data:
        if 'data' in item:
            for site in item['data']:
                if 'crawled_pages' in site:
                    # Pour chaque page crawlée
                    for page in site['crawled_pages']:
                        url = page['url']
                        page_type = page['type']
                        
                        # Créer un nom de fichier sécurisé
                        safe_filename = url.replace('https://', '').replace('http://', '').replace('/', '_') + '.html'
                        file_path = html_folder / safe_filename
                        
                        # Scraper la page
                        print(f"Scraping {url}...")
                        html_content = scrape_page(url)
                        
                        # Sauvegarder le contenu HTML
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(f"<!-- URL: {url} -->\n")
                            f.write(f"<!-- Type: {page_type} -->\n")
                            f.write(f"<!-- Date: {time.strftime('%Y-%m-%d %H:%M:%S')} -->\n\n")
                            f.write(html_content)
                        
                        print(f"Sauvegardé dans {file_path}")
                        
                        # Attendre un peu entre chaque requête pour être poli
                        time.sleep(2)

if __name__ == "__main__":
    main()
    print("Scraping terminé !")
