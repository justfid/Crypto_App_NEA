import requests

#MUTUAL FUNCTIONS
def read_api_key(file_path):
    """reads API key from a file."""
    try:
        with open(file_path, 'r') as file:
            keys = [line.strip() for line in file if line.strip()]
        if not keys:
            print(f"No API keys found in {file_path}")
            return None
        return keys
        
    except FileNotFoundError:
        print(f"API key file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading API key file: {e}")
        return None

#CG API FUNCTIONS

def get_PT_data(ids, api_key):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(ids),
        "order": "market_cap_rank",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "1h,24h,7d",
        "x_cg_demo_api_key": api_key
    }
    
    headers = {
        "Accepts": "application/json",
        "X-CG-Demo-API-Key": api_key
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        results_dict = {}
        for coin in data:
            results = [
                coin['name'],
                coin['symbol'],
                coin['current_price'],
                coin.get('price_change_percentage_1h_in_currency', 0),
                coin.get('price_change_percentage_24h_in_currency', 0),
                coin.get('price_change_percentage_7d_in_currency', 0),
                coin['market_cap'],
                coin['market_cap_rank']
            ]
            results_dict[coin['id']] = results
            
        return results_dict
        
    except requests.RequestException:
        return None

def get_price_tracker_data(coins):
    api_keys = read_api_key("coingecko_API_keys.txt")
    for key in api_keys:
        result = get_PT_data(coins, key)
        if result:
            return result
    return {coin: {} for coin in coins}


def get_coin_ticker(coin_name, api_key):
    """retrieves ticker (symbol) for a given coin name using CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/search"
    params = {
        "query": coin_name,
        "x_cg_demo_api_key": api_key
    }
    headers = {
        "Accepts": "application/json",
        "X-CG-Demo-API-Key": api_key
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['coins']:
            return data['coins'][0]['symbol']
        else:
            return None

    except requests.RequestException:
        return None
    

def get_coin_ticker_with_key(coin_name):
    """attempts to get coin ticker using multiple API keys"""
    api_keys = read_api_key("coingecko_API_keys.txt")
    for key in api_keys:
        result = get_coin_ticker(coin_name, key)
        if result:
            return result
    return None


#FCA API FUNCTIONS

def get_exchange_rate(original_currency, new_currency):
    """gets exchange rate for a currency pair."""
    api_url = "https://api.freecurrencyapi.com/v1/latest"
    api_keys = read_api_key("freecurrency_API_keys.txt")
    for key in api_keys: #validates the key to make sure it works
        response = requests.get(f"{api_url}?apikey={key}&base_currency={original_currency}&currencies={new_currency}")
        if response.status_code == 200:
            return response.json()['data'][new_currency]
    return "Error, Try again"

#NEWS API FUNCTIONS

def get_news(filters = None):
    api_url = "https://cryptopanic.com/api/v1/posts/"
    api_keys = read_api_key("cryptopanic_API_keys.txt")
    
    for key in api_keys: #validates the key to make sure it works
        response = requests.get(f"{api_url}?auth_token={key}{filters if filters else ''}")
        if response.status_code == 200:
            return response.json()["results"]
    return "Error, Try again"


def get_formatted_news(filters=None):
    data = get_news(filters)

    #processes and returns data
    processed_data = []
    for item in data:
        processed_item = {
            'title': item['title'],
            'url': item['url'],
            'ticker': extract_ticker(item),
            'published_at': item['published_at'].rstrip("Z").replace("T", " / ")
        }
        processed_data.append(processed_item)
    return processed_data


def extract_ticker(item):
    if 'currencies' in item and item['currencies']:
        return item['currencies'][0]['code']
    return None


if __name__ == "__main__":
    pass