import requests

#MUTUAL FUNCTIONS
def read_api_key(file_path):
    """Reads the API key from a file."""
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
    api_key = api_key
    """Gathers the data for the price tracker overview"""
    #sets up parameters and headers"
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(ids),
        #TODO make it ascending
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
        #makes sure the req is valid
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        results_dict = {}
        #formats the result into a dictionary of lists
        for coin in data:
            results = []
            for column in ["name", "symbol", "current_price", 
                           "price_change_percentage_1h_in_currency", 
                           "price_change_percentage_24h_in_currency", 
                           "price_change_percentage_7d_in_currency", 
                           "market_cap", "market_cap_rank"]:
                results.append(coin[column])
            results_dict[coin["id"]] = results
        
        return results_dict
    
    except requests.RequestException:
        return None


def get_price_tracker_data(coins):
    #TODO add it so it reads the coins from the database
    api_keys = read_api_key("coingecko_API_keys.txt")
    for key in api_keys:
        #checks to see if api key valid
        result = get_PT_data(coins, key) #calls the function that actually calls the api
        if result:
            #returns the result if valid
            return(result)
    else:
        pass

#FCA API FUNCTIONS

def get_exchange_rate(original_currency, new_currency):
    """Get the exchange rate for a currency pair."""
    api_url = "https://api.freecurrencyapi.com/v1/latest"
    api_keys = read_api_key("freecurrency_API_keys.txt")
    for key in api_keys: #validates the key to make sure it works
        response = requests.get(f"{api_url}?apikey={key}&base_currency={original_currency}&currencies={new_currency}")
        if response.status_code == 200:
            return response.json()['data'][new_currency]
    return "Error, Try again"


if __name__ == "__main__":
    pass
