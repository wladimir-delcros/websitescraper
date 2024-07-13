from flask import Flask, request, jsonify
import json
import requests
from modules.info_reader import InfoReader
from modules.scrapper import Scrapper

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, Flask is up and running!'

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    crawl = data.get('crawl', False)
    sm = data.get('sm', False)
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    if not (url.startswith("https://") or url.startswith("http://")):
        url = "http://" + url

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching the URL: {e}"}), 400

    scrap = Scrapper(url=url, crawl=crawl)
    IR = InfoReader(content=scrap.getText())
    emails = IR.getEmails()
    numbers = IR.getPhoneNumber()
    socials = IR.getSocials()
    sirets = scrap.extract_siret(' '.join(scrap.getText()['text']))
    result = {
        "E-Mails": emails,
        "Numbers": numbers,
        "SocialMedia": socials,
        "SIRET": sirets
    }
    
    if sm:
        sm_info = IR.getSocialsInfo()
        result["SocialMediaInfo"] = sm_info

    return jsonify(result), 200

@app.route('/scrape_multiple', methods=['POST'])
def scrape_multiple():
    data = request.json
    urls = data.get('urls', [])
    crawl = data.get('crawl', False)
    sm = data.get('sm', False)
    
    if not urls:
        return jsonify({"error": "URLs are required"}), 400

    results = []
    for url in urls:
        if not (url.startswith("https://") or url.startswith("http://")):
            url = "http://" + url
        
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            results.append({"url": url, "error": f"Error fetching the URL: {e}"})
            continue
        
        scrap = Scrapper(url=url, crawl=crawl)
        IR = InfoReader(content=scrap.getText())
        emails = IR.getEmails()
        numbers = IR.getPhoneNumber()
        socials = IR.getSocials()
        sirets = scrap.extract_siret(' '.join(scrap.getText()['text']))
        result = {
            "Target": url,
            "E-Mails": emails,
            "Numbers": numbers,
            "SocialMedia": socials,
            "SIRET": sirets
        }
        
        if sm:
            sm_info = IR.getSocialsInfo()
            result["SocialMediaInfo"] = sm_info
        
        results.append(result)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
