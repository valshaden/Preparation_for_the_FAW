# -*- coding: utf-8 -*-
# Упрощенная версия получения курсов криптовалют
import requests
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# --- Функции для получения данных из API ---

def get_binance_data():
    """Получаем популярные пары с Binance"""
    try:
        url = 'https://api.binance.com/api/v3/ticker/price'
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Проверка на ошибки HTTP
        data = response.json()
        
        # Фильтруем популярные монеты
        popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                         'DOGEUSDT', 'SOLUSDT', 'DOTUSDT', 'LTCUSDT', 'LINKUSDT']
        result = {item['symbol']: float(item['price']) for item in data if item['symbol'] in popular_coins}
        return result
    except Exception as e:
        messagebox.showerror("Ошибка Binance", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_coingecko_data():
    """Получаем данные с CoinGecko"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum,bnb,cardano,ripple,dogecoin,solana,polkadot,litecoin,chainlink',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        for coin in data:
            symbol = coin['symbol'].upper()
            result[symbol] = {
                'price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'change_24h': coin['price_change_percentage_24h']
            }
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CoinGecko", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_cryptocompare_data():
    """Получаем данные с CryptoCompare"""
    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        params = {
            'fsyms': 'BTC,ETH,BNB,ADA,XRP,DOGE,SOL,DOT,LTC,LINK',
            'tsyms': 'USD'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Преобразуем данные в нужный формат
        result = {coin: price_info['USD'] for coin, price_info in data.items()}
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CryptoCompare", f"Не удалось получить данные:\n{str(e)}")
        return None

# --- Функции интерфейса ---

def show_result_window(title, data):
    """Создает окно для отображения результата"""
    if data is None:
        return # Ошибка уже показана в функции API
        
    result_window = tk.Toplevel(root)
    result_window.title(f"Результаты: {title}")
    result_window.geometry("700x500")

    # Область с прокруткой для текста
    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=80, height=30, font=("Consolas", 10))
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Форматируем данные как JSON с отступами
    formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
    text_area.insert(tk.END, formatted_data)
    text_area.configure(state='disabled') # Только для чтения

def on_get_data():
    """Обработчик нажатия кнопки 'Получить данные'"""
    selected_api = api_var.get()
    
    if selected_api == "Binance":
        data = get_binance_data()
        show_result_window("Binance Public API", data)
    elif selected_api == "CoinGecko":
        data = get_coingecko_data()
        show_result_window("CoinGecko API", data)
    elif selected_api == "CryptoCompare":
        data = get_cryptocompare_data()
        show_result_window("CryptoCompare API", data)
    else:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите источник данных.")

# --- Создание основного окна ---
root = tk.Tk()
root.title("Курсы криптовалют")
root.geometry("350x150")
root.resizable(False, False) # Запрет изменения размера

# Создание и размещение элементов интерфейса
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="Выберите источник данных:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))

# Выпадающий список для выбора API
api_var = tk.StringVar(value="CoinGecko") # Значение по умолчанию
api_combobox = ttk.Combobox(main_frame, textvariable=api_var, 
                           values=["Binance", "CoinGecko", "CryptoCompare"], 
                           state="readonly", width=20)
api_combobox.pack(anchor=tk.W, pady=(0, 15))

# Кнопка для получения данных
get_data_btn = ttk.Button(main_frame, text="Получить данные", command=on_get_data)
get_data_btn.pack()

# Запуск главного цикла событий
root.mainloop()