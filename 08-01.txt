# -*- coding: utf-8 -*-
# Упрощенная версия получения курсов криптовалют с табличным выводом
# Столбцы: "Название", "Тикер", "Курс", "Валюта"
# Источник по умолчанию: Binance
# Курс с двумя знаками после запятой
import requests
import tkinter as tk
from tkinter import ttk, messagebox

# --- Маппинг кодов к полным названиям криптовалют ---
CRYPTO_NAMES = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'BNB': 'Binance Coin',
    'ADA': 'Cardano',
    'XRP': 'Ripple',
    'DOGE': 'Dogecoin',
    'SOL': 'Solana',
    'DOT': 'Polkadot',
    'LTC': 'Litecoin',
    'LINK': 'Chainlink',
    'USDT': 'Tether',
    'USDC': 'USD Coin',
    'BUSD': 'Binance USD',
    'EUR': 'Евро',
    'USD': 'Доллар США'
}

# --- Функции для получения данных из API ---

def get_binance_data():
    """Получаем популярные пары с Binance"""
    try:
        url = 'https://api.binance.com/api/v3/ticker/price'  # исправлено - убраны лишние пробелы
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Фильтруем популярные пары
        popular_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                         'DOGEUSDT', 'SOLUSDT', 'DOTUSDT', 'LTCUSDT', 'LINKUSDT',
                         'BTCUSDC', 'BTCEUR', 'BNBUSDC', 'ETHUSDC']
        result = []
        for item in data:
            if item['symbol'] in popular_pairs:
                # Пытаемся разделить символ на криптовалюту и валюту
                symbol = item['symbol']
                price = float(item['price'])
                
                # Улучшенная логика разделения
                if len(symbol) > 4 and symbol[-4:] in ['USDT', 'USDC', 'BUSD']:
                    crypto_code = symbol[:-4]
                    currency_code = symbol[-4:]
                elif len(symbol) > 3 and symbol[-3:] in ['EUR', 'USD', 'BTC']:
                    crypto_code = symbol[:-3]
                    currency_code = symbol[-3:]
                else:
                    # Если не смогли разделить, пропускаем
                    continue
                    
                full_name = CRYPTO_NAMES.get(crypto_code, crypto_code)
                currency_name = CRYPTO_NAMES.get(currency_code, currency_code)
                
                result.append({
                    'name': full_name,
                    'ticker': crypto_code,
                    'price': price,
                    'currency': currency_name
                })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка Binance", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_coingecko_data():
    """Получаем данные с CoinGecko"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'  # исправлено - убраны лишние пробелы
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum,binancecoin,cardano,ripple,dogecoin,solana,polkadot,litecoin,chainlink',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        result = []
        for coin in data:
            crypto_code = coin['symbol'].upper()
            full_name = coin['name']  # CoinGecko дает полное имя
            price = coin['current_price']
            currency_code = 'USD'
            currency_name = CRYPTO_NAMES.get(currency_code, currency_code)
            
            result.append({
                'name': full_name,
                'ticker': crypto_code,
                'price': price,
                'currency': currency_name
            })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CoinGecko", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_cryptocompare_data():
    """Получаем данные с CryptoCompare"""
    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'  # исправлено - убраны лишние пробелы
        params = {
            'fsyms': 'BTC,ETH,BNB,ADA,XRP,DOGE,SOL,DOT,LTC,LINK',
            'tsyms': 'USD,EUR'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = []
        for crypto_code, prices in data.items():
            full_name = CRYPTO_NAMES.get(crypto_code, crypto_code)
            for currency_code, price in prices.items():
                if price:  # Проверяем, что цена существует
                    currency_name = CRYPTO_NAMES.get(currency_code, currency_code)
                    
                    result.append({
                        'name': full_name,
                        'ticker': crypto_code,
                        'price': price,
                        'currency': currency_name
                    })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CryptoCompare", f"Не удалось получить данные:\n{str(e)}")
        return None

# --- Функции интерфейса ---

def show_result_window(title, data):
    """Создает окно с таблицей для отображения результата"""
    if data is None:
        return  # Ошибка уже показана в функции API
        
    result_window = tk.Toplevel(root)
    result_window.title(f"Результаты: {title}")
    result_window.geometry("800x500")

    # Создаем фрейм для таблицы с возможностью прокрутки
    frame = ttk.Frame(result_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Определяем столбцы
    columns = ('name', 'ticker', 'price', 'currency')
    
    # Создаем Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
    
    # Определяем заголовки столбцов
    tree.heading('name', text='Название')
    tree.heading('ticker', text='Тикер')
    tree.heading('price', text='Курс')
    tree.heading('currency', text='Валюта')
    
    # Устанавливаем ширину столбцов
    tree.column('name', width=250, anchor=tk.W)
    tree.column('ticker', width=80, anchor=tk.CENTER)
    tree.column('price', width=150, anchor=tk.E)
    tree.column('currency', width=100, anchor=tk.CENTER)

    # Добавляем вертикальную прокрутку
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    
    # Размещаем таблицу и скроллбар
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Заполняем таблицу данными
    for item in data:
        # Форматируем цену с двумя знаками после запятой
        formatted_price = f"{item['price']:.2f}"
        tree.insert('', tk.END, values=(
            item['name'],
            item['ticker'],
            formatted_price,
            item['currency']
        ))

    # Добавляем метку с количеством записей
    count_label = ttk.Label(result_window, text=f"Всего записей: {len(data)}")
    count_label.pack(pady=(0, 10))

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
root.resizable(False, False)  # Запрет изменения размера

# Создание и размещение элементов интерфейса
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="Выберите источник данных:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))

# Выпадающий список для выбора API - по умолчанию Binance
api_var = tk.StringVar(value="Binance")  # Значение по умолчанию изменено на Binance
api_combobox = ttk.Combobox(main_frame, textvariable=api_var, 
                           values=["Binance", "CoinGecko", "CryptoCompare"], 
                           state="readonly", width=20)
api_combobox.pack(anchor=tk.W, pady=(0, 15))

# Кнопка для получения данных
get_data_btn = ttk.Button(main_frame, text="Получить данные", command=on_get_data)
get_data_btn.pack()

# Запуск главного цикла событий
root.mainloop()

"""
Рекомендации по улучшению:
Добавить кэширование для уменьшения количества запросов
Добавить индикатор загрузки во время получения данных
Реализовать автообновление курсов
Добавить экспорт данных в CSV/Excel
Программа является рабочим вариантом после исправления URL и улучшения обработки символов.
"""