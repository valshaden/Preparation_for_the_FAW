# Получаем курсы криптовалют из интернета
import requests
import json
import pprint

# Настройка PrettyPrinter для красивого вывода
pp = pprint.PrettyPrinter(indent=4)

# 1. Binance Public API (пары BTC к другим валютам)
print("--- Binance Public API ---")
try:
    binance_result = requests.get('https://api.binance.com/api/v3/ticker/price?symbols=["BTCUSDT","BTCUSDC","BTCEUR"]', timeout=10)
    if binance_result.status_code == 200:
        binance_data = json.loads(binance_result.text)
        pp.pprint(binance_data)
    else:
        print(f"Ошибка Binance API: {binance_result.status_code}")
except Exception as e:
    print(f"Не удалось получить данные от Binance: {e}")

print("\n--- CoinGecko API ---")
# 2. CoinGecko API (цены для нескольких криптовалют в USD)
try:
    coingecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,litecoin&vs_currencies=usd,eur,btc"
    coingecko_result = requests.get(coingecko_url, timeout=10)
    if coingecko_result.status_code == 200:
        coingecko_data = json.loads(coingecko_result.text)
        pp.pprint(coingecko_data)
    else:
        print(f"Ошибка CoinGecko API: {coingecko_result.status_code}")
except Exception as e:
    print(f"Не удалось получить данные от CoinGecko: {e}")

print("\n--- CoinCap v2 API ---")
# 3. CoinCap v2 API (получаем информацию о нескольких активах)
try:
    coincap_url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,litecoin"
    coincap_result = requests.get(coincap_url, timeout=10)
    if coincap_result.status_code == 200:
        coincap_data = json.loads(coincap_result.text)
        pp.pprint(coincap_data)
    else:
        print(f"Ошибка CoinCap API: {coincap_result.status_code}")
except Exception as e:
    print(f"Не удалось получить данные от CoinCap: {e}")

print("\n--- CryptoCompare API ---")
# 4. CryptoCompare API (цены на BTC и ETH к USD и EUR)
# Примечание: Для более стабильной работы рекомендуется использовать ваш собственный API ключ.
# Бесплатный API-ключ можно получить на https://www.cryptocompare.com/
try:
    cryptocompare_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,EUR"
    # Если у вас есть API ключ, добавьте его в заголовки:
    # headers = {'authorization': 'Apikey ВАШ_API_КЛЮЧ_ЗДЕСЬ'}
    # cryptocompare_result = requests.get(cryptocompare_url, headers=headers, timeout=10)
    cryptocompare_result = requests.get(cryptocompare_url, timeout=10)
    if cryptocompare_result.status_code == 200:
        cryptocompare_data = json.loads(cryptocompare_result.text)
        pp.pprint(cryptocompare_data)
    else:
        print(f"Ошибка CryptoCompare API: {cryptocompare_result.status_code} - {cryptocompare_result.text}")
except Exception as e:
    print(f"Не удалось получить данные от CryptoCompare: {e}")

print("\n--- Завершено ---")
