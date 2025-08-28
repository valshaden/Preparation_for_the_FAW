# Qwen
# Получаем курсы криптовалют из разных публичных API
import requests
import json
import pprint

# Настраиваем PrettyPrinter
p = pprint.PrettyPrinter(indent=4)

print("1. Получение данных с Binance Public API (BTC/USDT)\n")
try:
    binance_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    result = requests.get(binance_url)
    data = result.json()
    print("Binance (BTC/USDT):")
    p.pprint(data)
except Exception as e:
    print(f"Ошибка при запросе к Binance: {e}\n")

print("\n" + "="*60 + "\n")

print("2. Получение данных с CoinGecko API (BTC, ETH к USD)\n")
try:
    coingecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    result = requests.get(coingecko_url)
    data = result.json()
    print("CoinGecko (Bitcoin, Ethereum к USD):")
    p.pprint(data)
except Exception as e:
    print(f"Ошибка при запросе к CoinGecko: {e}\n")

print("\n" + "="*60 + "\n")

print("3. Получение данных с CoinCap v2 API (топ-5 криптовалют)\n")
try:
    coincap_url = "https://api.coincap.io/v2/assets?limit=5"
    result = requests.get(coincap_url)
    data = result.json()
    print("CoinCap v2 (топ-5 активов):")
    p.pprint(data)
except Exception as e:
    print(f"Ошибка при запросе к CoinCap: {e}\n")

print("\n" + "="*60 + "\n")

print("4. Получение данных с CryptoCompare API (BTC, ETH, BNB к USD)\n")
try:
    cryptocompare_url = "https://min-api.cryptocompare.com/data/pricemultifull"
    params = {
        'fsyms': 'BTC,ETH,BNB',
        'tsyms': 'USD'
    }
    result = requests.get(cryptocompare_url, params=params)
    data = result.json()
    print("CryptoCompare (BTC, ETH, BNB к USD):")
    p.pprint(data)
except Exception as e:
    print(f"Ошибка при запросе к CryptoCompare: {e}\n")

print("\n" + "="*60)
print("Готово. Данные получены из всех доступных источников.")