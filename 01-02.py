# Deepseek
import requests
import json
import pprint
from time import sleep

def get_binance_data():
    """Получаем данные с Binance Public API"""
    print("=== Binance Public API ===")
    try:
        # Получаем список символов и цены
        symbols_url = 'https://api.binance.com/api/v3/ticker/price'
        result = requests.get(symbols_url, timeout=10)
        
        if result.status_code == 200:
            data = result.json()
            # Фильтруем только популярные криптовалюты к USDT
            popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                           'DOGEUSDT', 'DOTUSDT', 'UNIUSDT', 'LTCUSDT', 'LINKUSDT']
            
            binance_data = {}
            for coin in data:
                if coin['symbol'] in popular_coins:
                    binance_data[coin['symbol']] = float(coin['price'])
            
            return binance_data
        else:
            print(f"Ошибка Binance: {result.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении данных с Binance: {e}")
        return None

def get_coingecko_data():
    """Получаем данные с CoinGecko"""
    print("=== CoinGecko ===")
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum,bnb,cardano,ripple,dogecoin,polkadot,uniswap,litecoin,chainlink',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        
        result = requests.get(url, params=params, timeout=10)
        
        if result.status_code == 200:
            data = result.json()
            coingecko_data = {}
            for coin in data:
                coingecko_data[coin['symbol'].upper()] = coin['current_price']
            
            return coingecko_data
        else:
            print(f"Ошибка CoinGecko: {result.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении данных с CoinGecko: {e}")
        return None

def get_coincap_data():
    """Получаем данные с CoinCap v2"""
    print("=== CoinCap v2 ===")
    try:
        url = 'https://api.coincap.io/v2/assets'
        params = {
            'limit': 10
        }
        
        result = requests.get(url, params=params, timeout=10)
        
        if result.status_code == 200:
            data = result.json()
            coincap_data = {}
            for asset in data['data']:
                coincap_data[asset['symbol']] = float(asset['priceUsd'])
            
            return coincap_data
        else:
            print(f"Ошибка CoinCap: {result.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении данных с CoinCap: {e}")
        return None

def get_cryptocompare_data():
    """Получаем данные с CryptoCompare"""
    print("=== CryptoCompare ===")
    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        params = {
            'fsyms': 'BTC,ETH,BNB,ADA,XRP,DOGE,DOT,UNI,LTC,LINK',
            'tsyms': 'USD',
            'api_key': 'YOUR_API_KEY'  # Можно оставить пустым для бесплатного использования
        }
        
        result = requests.get(url, params=params, timeout=10)
        
        if result.status_code == 200:
            data = result.json()
            cryptocompare_data = {}
            for coin, price_data in data.items():
                cryptocompare_data[coin] = price_data['USD']
            
            return cryptocompare_data
        else:
            print(f"Ошибка CryptoCompare: {result.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении данных с CryptoCompare: {e}")
        return None

def main():
    """Основная функция программы"""
    print("Получаем курсы криптовалют из различных источников\n")
    
    # Настраиваем PrettyPrinter
    p = pprint.PrettyPrinter(indent=4)
    
    # Получаем данные из всех источников поочередно
    sources = [
        ('Binance', get_binance_data),
        ('CoinGecko', get_coingecko_data),
        ('CoinCap', get_coincap_data),
        ('CryptoCompare', get_cryptocompare_data)
    ]
    
    all_data = {}
    
    for source_name, source_function in sources:
        data = source_function()
        if data:
            all_data[source_name] = data
            p.pprint(data)
            print()
        else:
            print(f"Не удалось получить данные от {source_name}\n")
        
        # Небольшая пауза между запросами
        sleep(1)
    
    # Выводим сводную информацию
    print("=== СВОДНАЯ ИНФОРМАЦИЯ ===")
    for source, data in all_data.items():
        print(f"{source}: {len(data)} криптовалют")
    
    # Сохраняем данные в файл
    try:
        with open('crypto_prices.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print("\nДанные сохранены в файл 'crypto_prices.json'")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

if __name__ == "__main__":
    main()