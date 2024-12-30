import json
from data_saver import DataSaver

# Charger les données existantes
with open('resultats_scraping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sauvegarder dans les deux formats
saver = DataSaver()
json_path, csv_path = saver.save_all(data)
print(f"Fichiers sauvegardés :\nJSON : {json_path}\nCSV : {csv_path}")
