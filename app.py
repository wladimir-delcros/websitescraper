import logging
from flask import Flask, request, jsonify
import requests
from modules.scrapper import Scrapper
import phonenumbers
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Fonction pour normaliser et supprimer les doublons des numéros de téléphone
def normalize_phone_numbers(phone_list):
    normalized_numbers = {}
    for phone in phone_list:
        try:
            number = phonenumbers.parse(phone['value'], "FR")
            if phonenumbers.is_valid_number(number):
                normalized_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                if normalized_number not in normalized_numbers:
                    normalized_numbers[normalized_number] = {
                        'value': normalized_number,
                        'sources': phone['sources']
                    }
                else:
                    normalized_numbers[normalized_number]['sources'].extend(phone['sources'])
                    normalized_numbers[normalized_number]['sources'] = list(set(normalized_numbers[normalized_number]['sources']))
        except phonenumbers.NumberParseException:
            if phone['value'] not in normalized_numbers:
                normalized_numbers[phone['value']] = phone
            else:
                normalized_numbers[phone['value']]['sources'].extend(phone['sources'])
                normalized_numbers[phone['value']]['sources'] = list(set(normalized_numbers[phone['value']]['sources']))
    return list(normalized_numbers.values())

# Fonction pour supprimer les doublons tout en consolidant les sources
def remove_duplicates(data_list):
    seen = {}
    new_list = []
    for item in data_list:
        if item['value'] not in seen:
            seen[item['value']] = {
                'value': item['value'],
                'sources': item['sources']
            }
            new_list.append(seen[item['value']])
        else:
            seen[item['value']]['sources'].extend(item['sources'])
            seen[item['value']]['sources'] = list(set(seen[item['value']]['sources']))
    return new_list

@app.route('/')
def home():
    app.logger.info('Home endpoint hit')
    return 'Hello, Flask is up and running!'

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        url = data.get('url')
        crawl = data.get('crawl', False)
        sm = data.get('sm', False)
        
        if not url:
            app.logger.error('No URL provided')
            return jsonify({"error": "URL is required"}), 400
        
        url = url if url.startswith(("http://", "https://")) else f"http://{url}"

        scrap = Scrapper(url=url, crawl=crawl)
        text_data = scrap.getText()
        
        emails = text_data.get('E-Mails', [])
        phone_numbers = text_data.get('Numbers', [])
        socials = text_data.get('SocialMedia', {})
        siret_or_siren = text_data.get('SIRET_OR_SIREN', {})
        meta_info = text_data.get('HomepageMetaInfo', {})

        result = {
            "status": "OK",
            "request_id": request.headers.get('X-Request-ID', ''),
            "data": [{
                "domain": url,
                "query": url,
                "emails": emails,
                "phone_numbers": phone_numbers,
                "socials": socials,
                "siret_or_siren": siret_or_siren,
                "meta_info": meta_info
            }]
        }
        
        # Supprimez ou commentez cette ligne si getSocialsInfo n'est pas nécessaire
        # if sm:
        #     result["data"][0]["SocialMediaInfo"] = scrap.getSocialsInfo()

        app.logger.debug('Scrape result prepared')
        return jsonify(result), 200
    
    except Exception as e:
        app.logger.error(f'Error during scraping: {str(e)}')
        return jsonify({"error": f"Error during scraping: {str(e)}"}), 500

@app.route('/scrape_multiple', methods=['POST'])
def scrape_multiple():
    app.logger.info('Scrape multiple endpoint hit')
    data = request.json
    urls = data.get('urls', [])
    crawl = data.get('crawl', False)
    sm = data.get('sm', False)
    
    if not urls:
        app.logger.error('No URLs provided')
        return jsonify({"error": "URLs are required"}), 400

    results = []
    for url in urls:
        url = url if url.startswith(("http://", "https://")) else f"http://{url}"
        
        try:
            scrap = Scrapper(url=url, crawl=crawl)
            text_data = scrap.getText()
            
            emails = remove_duplicates(text_data.get('E-Mails', []))
            phone_numbers = normalize_phone_numbers(text_data.get('Numbers', []))
            socials = text_data.get('SocialMedia', {})
            siret_or_siren = text_data.get('SIRET_OR_SIREN', {})
            meta_info = text_data.get('HomepageMetaInfo', {})

            valid_siret = [siret for siret in siret_or_siren.get("SIRET", [])
                           if any(siret.startswith(siren) for siren in siret_or_siren.get("SIREN", []))]
            siret_or_siren["SIRET"] = valid_siret

            result = {
                "domain": url,
                "query": url,
                "emails": emails,
                "phone_numbers": phone_numbers,
                "socials": socials,
                "siret_or_siren": siret_or_siren,
                "meta_info": meta_info
            }
            
            if sm:
                result["SocialMediaInfo"] = scrap.getSocialsInfo()
            
            results.append(result)
        except Exception as e:
            app.logger.error(f'Error scraping URL {url}: {str(e)}')
            results.append({"url": url, "error": f"Error scraping URL: {str(e)}"})

    response = {
        "status": "OK",
        "request_id": request.headers.get('X-Request-ID', ''),
        "data": results
    }
    
    app.logger.debug('Scrape multiple result prepared')
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)