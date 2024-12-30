import json
import os
from datetime import datetime
from typing import List, Dict, Any
from json_to_csv import json_to_csv

# Dans votre code de scraping
# saver = DataSaver()
# json_path, csv_path = saver.save_all(scraped_data)

class DataSaver:
    def __init__(self, base_directory: str = "."):
        """
        Initialise le gestionnaire de sauvegarde de données
        
        Args:
            base_directory (str): Répertoire de base pour sauvegarder les fichiers
        """
        self.base_directory = base_directory
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        os.makedirs(self.base_directory, exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, "json"), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, "csv"), exist_ok=True)
    
    def _generate_filename(self, prefix: str, extension: str) -> str:
        """Génère un nom de fichier unique avec timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def save_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Sauvegarde les données au format JSON
        
        Args:
            data: Les données à sauvegarder
            filename: Nom du fichier (optionnel)
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        if filename is None:
            filename = self._generate_filename("scraping_results", "json")
        
        json_path = os.path.join(self.base_directory, "json", filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def save_csv(self, json_file: str, filename: str = None) -> str:
        """
        Convertit et sauvegarde les données au format CSV
        
        Args:
            json_file: Chemin vers le fichier JSON source
            filename: Nom du fichier CSV (optionnel)
            
        Returns:
            str: Chemin du fichier CSV sauvegardé
        """
        if filename is None:
            filename = self._generate_filename("scraping_results", "csv")
        
        csv_path = os.path.join(self.base_directory, "csv", filename)
        json_to_csv(json_file, csv_path)
        
        return csv_path
    
    def save_all(self, data: List[Dict[str, Any]], json_filename: str = None, csv_filename: str = None) -> tuple[str, str]:
        """
        Sauvegarde les données en JSON et CSV
        
        Args:
            data: Les données à sauvegarder
            json_filename: Nom du fichier JSON (optionnel)
            csv_filename: Nom du fichier CSV (optionnel)
            
        Returns:
            tuple: (chemin_json, chemin_csv)
        """
        # Sauvegarde JSON
        json_path = self.save_json(data, json_filename)
        
        # Sauvegarde CSV
        csv_path = self.save_csv(json_path, csv_filename)
        
        return json_path, csv_path


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de données
    test_data = [
        {
            "status": "success",
            "request_id": "test123",
            "data": [
                {
                    "domain": "example.com",
                    "emails": [{"value": "test@example.com", "sources": ["contact"]}]
                }
            ]
        }
    ]
    
    # Utilisation du DataSaver
    saver = DataSaver()
    json_file, csv_file = saver.save_all(test_data)
    print(f"Données sauvegardées dans:\nJSON: {json_file}\nCSV: {csv_file}")
