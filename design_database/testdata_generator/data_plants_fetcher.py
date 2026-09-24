
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv('PERENUAL_API_KEY')
OUTPUT_FILE = 'data_plants.json'
PAGES_TO_FETCH = 10
FETCH_IMAGES = False

if not API_KEY:
        print("Error: PERENUAL_API_KEY is missing from your .env file.")
        exit(1)

data_plants = []
for page in range(1, PAGES_TO_FETCH+1):
    api_url = f"https://perenual.com/api/v2/species-list?key={API_KEY}&page={page}"

    try:
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            for plant in data.get('data', []):
                name = plant.get('common_name')
                if name:
                    scientific_list = plant.get('scientific_name', [])
                    scientific_name = scientific_list[0] if scientific_list else None
                    if FETCH_IMAGES:
                        img_obj = plant.get('default_image')
                    
                        data_plants.append({
                            'name': name.title(),
                            'scientific_name': scientific_name,
                            'image_url': img_obj.get('regular_url') if img_obj else None,
                        })
                    else:
                        data_plants.append({
                            'name': name.title(),
                            'scientific_name': scientific_name,
                        })
        
        else:
            print(f"Http request failed on page {page}/{PAGES_TO_FETCH} with "
                  f"status code {response.status_code}")
        
    except Exception as err:
        print(f"Network error on page {page}: {err}")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
    json.dump(data_plants, file, indent=4, ensure_ascii=False)
