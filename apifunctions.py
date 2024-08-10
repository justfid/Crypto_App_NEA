import requests

apiKey = []
def get_price(coin):
    url =  f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin}&x_cg_demo_api_key={apiKey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if len(data):
            bitcoin_price = data[0]['current_price']
            return bitcoin_price
        else:
            print(f"{coin} data not found")
            return "Error"
    else:
        print("Error fetching data:", response.status_code)
        return "Error"
    

def get_prices(coins):
    coinIds = ','.join(coins)
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coinIds}&x_cg_demo_api_key={apiKey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices = {}
        for coin_data in data:
            coin_id = coin_data['id']
            price = coin_data['current_price']
            prices[coin_id] = price







print(get_price("bitcoin"))