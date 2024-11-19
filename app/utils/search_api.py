import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'app', 'config', '.env'))

BING_API_KEY = os.getenv('BING_API_KEY')
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

def search_bing(query):
    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY
    }
    params = {
        "q": query,  # the search query
        "textDecorations": True,
        "textFormat": "HTML"
    }
    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()  # Check if the request was successful
        search_results = response.json()

        if not search_results.get('webPages', {}).get('value'):
            raise ValueError("No search results found.")


        return search_results
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while querying Bing API: {e}")